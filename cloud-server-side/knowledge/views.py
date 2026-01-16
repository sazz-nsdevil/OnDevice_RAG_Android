from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
import os
import sqlite3
import json
import tempfile

from .models import Course, Document, Chunk
from .serializers import (
    CourseSerializer, DocumentSerializer, DocumentDetailSerializer,
    DocumentUploadSerializer, ChunkSerializer, ChunkSummarySerializer
)
from .services import (
    EmbeddingService, ChunkingService, DocumentParsingService
)


class CourseViewSet(viewsets.ModelViewSet):
    """
    Course Management API
    
    CRUD operations for managing courses (e.g., SCI10, MATH09).
    
    list: Get all courses
    create: Create a new course
    retrieve: Get course details with documents
    update: Update course
    destroy: Delete course
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for a course"""
        course = self.get_object()
        documents = course.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download_knowledge_base(self, request, pk=None):
        """Download knowledge base as SQLite vector snapshot"""
        course = self.get_object()
        
        try:
            # Get all chunks for this course
            chunks = Chunk.objects.filter(document__course=course).select_related('document')
            
            if not chunks.exists():
                return Response({'error': 'No chunks found for this course'}, status=status.HTTP_404_NOT_FOUND)
            
            # Create SQLite database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create schema
            cursor.execute('''
                CREATE TABLE courses (
                    id INTEGER PRIMARY KEY,
                    code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE documents (
                    id INTEGER PRIMARY KEY,
                    course_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    file_type TEXT,
                    FOREIGN KEY (course_id) REFERENCES courses(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE chunks (
                    id INTEGER PRIMARY KEY,
                    document_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    vector TEXT NOT NULL,
                    embedding_model TEXT,
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                )
            ''')
            
            # Insert course
            cursor.execute('INSERT INTO courses (id, code, name) VALUES (?, ?, ?)',
                          (course.id, course.code, course.name))
            
            # Insert documents and chunks
            for chunk in chunks:
                doc = chunk.document
                
                # Insert document
                cursor.execute('INSERT OR IGNORE INTO documents (id, course_id, title, file_type) VALUES (?, ?, ?, ?)',
                              (doc.id, course.id, doc.title, doc.file_type))
                
                # Insert chunk
                vector_json = json.dumps(chunk.vector)
                cursor.execute('INSERT INTO chunks (document_id, text, chunk_index, vector, embedding_model) VALUES (?, ?, ?, ?, ?)',
                              (doc.id, chunk.text, chunk.chunk_index, vector_json, chunk.embedding_model))
            
            conn.commit()
            conn.close()
            
            # Return file
            response = FileResponse(
                open(db_path, 'rb'),
                as_attachment=True,
                filename=f"{course.code}_knowledge_base.db"
            )
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Document Upload & Management API
    
    Upload documents to a course. Documents are automatically:
    - Parsed (TXT, PDF, DOCX)
    - Split into chunks (with overlap)
    - Vectorized using ONNX embeddings
    - Saved to database
    
    list: Get all documents (filter by course_id)
    create: Upload new document
    retrieve: Get document with chunks
    update: Update document metadata
    destroy: Delete document
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentUploadSerializer
        elif self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentSerializer
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if course_id:
            return Document.objects.filter(course_id=course_id)
        return Document.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Upload and process document"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        
        try:
            self._process_document(document)
            response_serializer = DocumentDetailSerializer(document)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            document.delete()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_document(self, document: Document):
        """Parse, chunk, and embed document"""
        # Parse document
        file_path = document.file.path
        text = DocumentParsingService.parse_document(file_path, document.file_type)
        
        # Chunk text
        chunks_text = ChunkingService.chunk_text(text)
        
        # Generate embeddings
        embedding_service = EmbeddingService()
        embeddings = embedding_service.embed_batch(chunks_text)
        
        # Save chunks and vectors to database
        for idx, (chunk_text, embedding) in enumerate(zip(chunks_text, embeddings)):
            Chunk.objects.create(
                document=document,
                text=chunk_text,
                chunk_index=idx,
                vector=embedding,
                embedding_model=embedding_service.model_name
            )
    
    @action(detail=True, methods=['get'])
    def chunks(self, request, pk=None):
        """Get chunks for a document"""
        document = self.get_object()
        chunks = document.chunks.all()
        serializer = ChunkSummarySerializer(chunks, many=True)
        return Response(serializer.data)
