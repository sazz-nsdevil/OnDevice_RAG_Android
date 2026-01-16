from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
import os
import tempfile

from .models import Grade, Subject, Document, Chunk, Embedding, VectorSnapshot
from .serializers import (
    GradeSerializer, SubjectSerializer, DocumentSerializer, 
    DocumentUploadSerializer, VectorSnapshotSerializer, ChunkWithEmbeddingSerializer
)
from .services import (
    EmbeddingService, ChunkingService, DocumentParsingService, VectorSnapshotService
)


class GradeViewSet(viewsets.ModelViewSet):
    """
    Grade Management API
    
    CRUD operations for managing grade levels (e.g., Grade 7, Grade 8).
    Each grade can have multiple subjects.
    
    list: Retrieve all grades
    create: Create a new grade
    retrieve: Get details of a specific grade
    update: Update a grade
    destroy: Delete a grade
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """Get all subjects for a grade"""
        grade = self.get_object()
        subjects = grade.subjects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_snapshot(self, request, pk=None):
        """Create vector snapshot for entire grade"""
        grade = self.get_object()
        try:
            snapshot_path = VectorSnapshotService.export_snapshot(grade_id=grade.id)
            
            # Save to VectorSnapshot model
            snapshot = VectorSnapshot.objects.create(
                grade=grade,
                snapshot_type='grade',
                snapshot_file=snapshot_path
            )
            serializer = VectorSnapshotSerializer(snapshot)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubjectViewSet(viewsets.ModelViewSet):
    """
    Subject Management API
    
    CRUD operations for managing subjects within grades.
    Each subject belongs to one grade and can have multiple documents.
    
    list: Retrieve all subjects (optionally filter by grade_id)
    create: Create a new subject
    retrieve: Get details of a specific subject
    update: Update a subject
    destroy: Delete a subject
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
    def get_queryset(self):
        grade_id = self.request.query_params.get('grade_id')
        if grade_id:
            return Subject.objects.filter(grade_id=grade_id)
        return Subject.objects.all()
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for a subject"""
        subject = self.get_object()
        documents = subject.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_snapshot(self, request, pk=None):
        """Create vector snapshot for subject"""
        subject = self.get_object()
        try:
            snapshot_path = VectorSnapshotService.export_snapshot(subject_id=subject.id)
            
            # Save to VectorSnapshot model
            snapshot = VectorSnapshot.objects.create(
                subject=subject,
                snapshot_type='subject',
                snapshot_file=snapshot_path
            )
            serializer = VectorSnapshotSerializer(snapshot)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Document Management API
    
    CRUD operations for uploading and managing documents.
    Automatically processes documents: parses, chunks, and generates embeddings.
    
    Supported formats: TXT, PDF, DOCX
    
    list: Retrieve all documents (filter by subject_id or grade_id)
    create: Upload new document (multipart form data)
    retrieve: Get document details with chunks and embeddings
    update: Update document metadata
    destroy: Delete document
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentUploadSerializer
        return DocumentSerializer
    
    def get_queryset(self):
        subject_id = self.request.query_params.get('subject_id')
        grade_id = self.request.query_params.get('grade_id')
        
        queryset = Document.objects.all()
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        elif grade_id:
            queryset = queryset.filter(subject__grade_id=grade_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Upload and process document"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        
        # Process document: parse, chunk, and embed
        try:
            self._process_document(document)
            response_serializer = DocumentSerializer(document)
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
        
        # Save chunks and embeddings to database
        for idx, (chunk_text, embedding) in enumerate(zip(chunks_text, embeddings)):
            chunk = Chunk.objects.create(
                document=document,
                text=chunk_text,
                chunk_index=idx
            )
            Embedding.objects.create(
                chunk=chunk,
                vector=embedding,
                embedding_model=embedding_service.model_name
            )
    
    @action(detail=True, methods=['get'])
    def chunks(self, request, pk=None):
        """Get chunks for a document"""
        document = self.get_object()
        chunks = document.chunks.all()
        serializer = ChunkWithEmbeddingSerializer(chunks, many=True)
        return Response(serializer.data)


class VectorSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vector Snapshot Download API
    
    Read-only endpoints for downloading vector snapshots.
    Snapshots contain all chunks and embeddings for a grade or subject.
    
    Exported as SQLite database for mobile app to directly load.
    
    list: List all snapshots (filter by grade_id or subject_id)
    retrieve: Get snapshot metadata
    """
    queryset = VectorSnapshot.objects.all()
    serializer_class = VectorSnapshotSerializer
    
    def get_queryset(self):
        grade_id = self.request.query_params.get('grade_id')
        subject_id = self.request.query_params.get('subject_id')
        
        queryset = VectorSnapshot.objects.all()
        
        if grade_id:
            queryset = queryset.filter(grade_id=grade_id)
        elif subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download snapshot as SQLite file"""
        snapshot = self.get_object()
        
        if snapshot.snapshot_file:
            file_path = snapshot.snapshot_file.path
            file_name = os.path.basename(file_path)
            
            return FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=file_name
            )
        
        return Response({'error': 'Snapshot file not found'}, status=status.HTTP_404_NOT_FOUND)
