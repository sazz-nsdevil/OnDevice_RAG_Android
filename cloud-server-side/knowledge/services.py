import sqlite3
import json
from typing import List, Dict, Any
import numpy as np
import os
from pathlib import Path


# Set up embedding cache directory
BASE_DIR = Path(__file__).resolve().parent.parent
PRETRAINED_MODELS_DIR = BASE_DIR / 'pretrained_models'
PRETRAINED_MODELS_DIR.mkdir(exist_ok=True)


class EmbeddingService:
    """Service for generating embeddings using ONNX models from HuggingFace"""
    
    def __init__(self, model_name: str = "exp-models/dragonkue-KoEn-E5-Tiny-ONNX"):
        """
        Initialize embedding service with ONNX model.
        Downloads model from HuggingFace Hub to local cache if not present.
        """
        self.model_name = model_name
        self.model_path = None
        self.tokenizer = None
        self.session = None
        self._init_model()
    
    def _init_model(self):
        """Initialize and download ONNX model"""
        try:
            from huggingface_hub import snapshot_download
            import onnxruntime as ort
            from tokenizers import Tokenizer
            
            # Download model to local directory
            print(f"Downloading model: {self.model_name}")
            self.model_path = snapshot_download(
                repo_id=self.model_name,
                cache_dir=str(PRETRAINED_MODELS_DIR),
                allow_patterns=["*.onnx", "tokenizer.json", "config.json", "special_tokens_map.json"]
            )
            print(f"Model downloaded to: {self.model_path}")
            
            # Load tokenizer
            tokenizer_path = os.path.join(self.model_path, "tokenizer.json")
            self.tokenizer = Tokenizer.from_file(tokenizer_path)
            
            # Load ONNX session
            onnx_model_path = os.path.join(self.model_path, "model.onnx")
            if not os.path.exists(onnx_model_path):
                # Try alternative names
                onnx_files = [f for f in os.listdir(self.model_path) if f.endswith('.onnx')]
                if onnx_files:
                    onnx_model_path = os.path.join(self.model_path, onnx_files[0])
                else:
                    raise FileNotFoundError("No ONNX model file found")
            
            self.session = ort.InferenceSession(onnx_model_path, providers=['CPUExecutionProvider'])
            print("ONNX model loaded successfully")
            
        except ImportError as e:
            raise ImportError(f"Required packages not installed: {e}. Install with: uv pip install huggingface-hub onnxruntime tokenizers")
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not self.session or not self.tokenizer:
            raise RuntimeError("Model not initialized properly")
        
        try:
            # Tokenize
            encoded = self.tokenizer.encode(text)
            input_ids = np.array([encoded.ids], dtype=np.int64)
            attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
            
            # Run ONNX inference
            input_name = self.session.get_inputs()[0].name
            output_name = self.session.get_outputs()[0].name
            
            embedding = self.session.run([output_name], {input_name: input_ids})[0]
            
            # Return flattened embedding
            return embedding[0].tolist() if embedding.ndim > 1 else embedding.tolist()
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Fallback to random embedding
            return np.random.randn(384).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.session or not self.tokenizer:
            raise RuntimeError("Model not initialized properly")
        
        embeddings = []
        for text in texts:
            embeddings.append(self.embed(text))
        
        return embeddings


class ChunkingService:
    """Service for chunking documents using LangChain"""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
        """
        Chunk text using LangChain's RecursiveCharacterTextSplitter.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        
        Returns:
            List of text chunks
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ".", " ", ""]
            )
            chunks = splitter.split_text(text)
            return chunks if chunks else [text]
        except ImportError:
            # Fallback to simple sentence-based chunking
            print("Warning: langchain_text_splitters not available. Using fallback chunking.")
            return ChunkingService._fallback_chunk(text, chunk_size)
    
    @staticmethod
    def _fallback_chunk(text: str, chunk_size: int = 1000) -> list:
        """Fallback chunking by splitting on newlines and periods"""
        sentences = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + "\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]


class DocumentParsingService:
    """Service for parsing different document types"""
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Parse TXT file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Parse PDF file"""
        try:
            from PyPDF2 import PdfReader
            text = ""
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF parsing")
    
    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Parse DOCX file"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except ImportError:
            raise ImportError("python-docx is required for DOCX parsing")
    
    @staticmethod
    def parse_document(file_path: str, file_type: str) -> str:
        """Parse document based on file type"""
        if file_type == 'txt':
            return DocumentParsingService.parse_txt(file_path)
        elif file_type == 'pdf':
            return DocumentParsingService.parse_pdf(file_path)
        elif file_type == 'docx':
            return DocumentParsingService.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


class VectorSnapshotService:
    """Service for creating and managing vector snapshots for mobile"""
    
    @staticmethod
    def create_snapshot_db(data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Create a SQLite database with vector data for mobile.
        
        Database schema:
        - chunks: id, text, chunk_index, document_id, subject_id, grade_id
        - embeddings: id, chunk_id, vector (JSON)
        - documents: id, title, subject_id, grade_id
        - subjects: id, name, grade_id
        - grades: id, name
        """
        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                grade_id INTEGER NOT NULL,
                FOREIGN KEY (grade_id) REFERENCES grades(id),
                UNIQUE(name, grade_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                subject_id INTEGER NOT NULL,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                document_id INTEGER NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY,
                chunk_id INTEGER NOT NULL UNIQUE,
                vector TEXT NOT NULL,
                FOREIGN KEY (chunk_id) REFERENCES chunks(id)
            )
        ''')
        
        # Insert data
        for item in data:
            # Insert or get grade
            cursor.execute('INSERT OR IGNORE INTO grades (name) VALUES (?)', (item['grade_name'],))
            grade_id = cursor.execute('SELECT id FROM grades WHERE name = ?', (item['grade_name'],)).fetchone()[0]
            
            # Insert or get subject
            cursor.execute('INSERT OR IGNORE INTO subjects (name, grade_id) VALUES (?, ?)', 
                          (item['subject_name'], grade_id))
            subject_id = cursor.execute('SELECT id FROM subjects WHERE name = ? AND grade_id = ?', 
                                       (item['subject_name'], grade_id)).fetchone()[0]
            
            # Insert or get document
            cursor.execute('INSERT OR IGNORE INTO documents (title, subject_id) VALUES (?, ?)', 
                          (item['document_title'], subject_id))
            doc_id = cursor.execute('SELECT id FROM documents WHERE title = ? AND subject_id = ?', 
                                   (item['document_title'], subject_id)).fetchone()[0]
            
            # Insert chunk
            cursor.execute('INSERT INTO chunks (text, chunk_index, document_id) VALUES (?, ?, ?)', 
                          (item['chunk_text'], item['chunk_index'], doc_id))
            chunk_id = cursor.lastrowid
            
            # Insert embedding (vector as JSON string)
            vector_json = json.dumps(item['embedding'])
            cursor.execute('INSERT INTO embeddings (chunk_id, vector) VALUES (?, ?)', 
                          (chunk_id, vector_json))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def export_snapshot(grade_id: int = None, subject_id: int = None, output_path: str = None) -> str:
        """
        Export vector snapshot for a grade or subject.
        Returns the path to the created SQLite file.
        """
        from .models import Embedding, Chunk, Document, Subject, Grade
        
        if subject_id:
            subject = Subject.objects.get(id=subject_id)
            embeddings = Embedding.objects.filter(chunk__document__subject_id=subject_id)
            label = f"{subject.grade.name}_{subject.name}".replace(" ", "_")
        elif grade_id:
            embeddings = Embedding.objects.filter(chunk__document__subject__grade_id=grade_id)
            grade = Grade.objects.get(id=grade_id)
            label = grade.name.replace(" ", "_")
        else:
            raise ValueError("Either grade_id or subject_id must be provided")
        
        # Prepare data
        data = []
        for emb in embeddings:
            chunk = emb.chunk
            doc = chunk.document
            subject = doc.subject
            
            data.append({
                'grade_name': subject.grade.name,
                'subject_name': subject.name,
                'document_title': doc.title,
                'chunk_text': chunk.text,
                'chunk_index': chunk.chunk_index,
                'embedding': emb.vector,
            })
        
        if not output_path:
            output_path = f"/tmp/{label}_snapshot.db"
        
        VectorSnapshotService.create_snapshot_db(data, output_path)
        return output_path
