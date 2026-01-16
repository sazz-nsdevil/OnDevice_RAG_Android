import sqlite3
import json
from typing import List, Dict, Any
import numpy as np
import os
from pathlib import Path
import sys


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
            if not os.path.exists(tokenizer_path):
                raise FileNotFoundError(f"Tokenizer not found at {tokenizer_path}")
            self.tokenizer = Tokenizer.from_file(tokenizer_path)
            
            # Load ONNX session - search recursively for .onnx files
            onnx_model_path = self._find_onnx_model(self.model_path)
            if not onnx_model_path:
                raise FileNotFoundError(f"No ONNX model file found in {self.model_path}")
            
            self.session = ort.InferenceSession(onnx_model_path, providers=['CPUExecutionProvider'])
            print(f"ONNX model loaded successfully from: {onnx_model_path}")
            
        except ImportError as e:
            raise ImportError(f"Required packages not installed: {e}. Install with: uv pip install huggingface-hub onnxruntime tokenizers")
    
    def _find_onnx_model(self, root_path: str) -> str:
        """
        Recursively search for ONNX model files.
        Prioritizes model.onnx, then others.
        """
        import glob
        
        # First try model.onnx in root
        model_path = os.path.join(root_path, "model.onnx")
        if os.path.exists(model_path):
            return model_path
        
        # Search in onnx subdirectory
        onnx_dir = os.path.join(root_path, "onnx")
        if os.path.isdir(onnx_dir):
            model_path = os.path.join(onnx_dir, "model.onnx")
            if os.path.exists(model_path):
                return model_path
            
            # Try any .onnx file in onnx directory
            onnx_files = glob.glob(os.path.join(onnx_dir, "*.onnx"))
            if onnx_files:
                return onnx_files[0]
        
        # Recursively search all subdirectories
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith('.onnx'):
                    return os.path.join(root, file)
        
        return None
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not self.session or not self.tokenizer:
            raise RuntimeError("Model not initialized properly")
        
        try:
            # Tokenize
            encoded = self.tokenizer.encode(text)
            input_ids = np.array([encoded.ids], dtype=np.int64)
            attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
            
            # Create token_type_ids (all zeros for BERT-like models)
            token_type_ids = np.zeros_like(input_ids, dtype=np.int64)
            
            # Prepare input feed with all required inputs
            input_feed = {}
            for input_node in self.session.get_inputs():
                input_name = input_node.name
                if input_name == 'input_ids':
                    input_feed[input_name] = input_ids
                elif input_name == 'attention_mask':
                    input_feed[input_name] = attention_mask
                elif input_name == 'token_type_ids':
                    input_feed[input_name] = token_type_ids
            
            # Run ONNX inference
            output_names = [output.name for output in self.session.get_outputs()]
            embeddings = self.session.run(output_names, input_feed)
            
            # Return the last hidden state (embeddings) - first output typically
            embedding = embeddings[0]
            
            # Pool the embeddings (use mean pooling of last hidden state)
            if embedding.ndim > 2:
                # Remove batch dimension and average across sequence
                embedding = embedding[0].mean(axis=0)
            elif embedding.ndim == 2:
                embedding = embedding[0].mean(axis=0)
            
            return embedding.tolist()
        
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
    def chunk_text(text: str, chunk_size: int = 200, chunk_overlap: int = 50) -> list:
        """
        Chunk text using LangChain's RecursiveCharacterTextSplitter.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters (200 = more granular chunks)
            chunk_overlap: Overlap between chunks in characters
        
        Returns:
            List of text chunks
        """
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        print(f"\n[CHUNKING] Input text length: {len(text)} characters", flush=True)
        sys.stdout.flush()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = splitter.split_text(text)
        
        # Ensure we have chunks
        if not chunks:
            chunks = [text]
        
        # Remove any empty chunks
        chunks = [c for c in chunks if c.strip()]
        
        print(f"[CHUNKING] Total chunks created: {len(chunks)}", flush=True)
        for i, chunk in enumerate(chunks[:3]):
            print(f"  Chunk {i}: {len(chunk)} chars, preview: {chunk[:80]}...", flush=True)
        sys.stdout.flush()
        
        return chunks


class DocumentParsingService:
    """Service for parsing different document types"""
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Parse TXT file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Parse PDF file using pdfplumber for better text extraction"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                num_pages = len(pdf.pages)
                print(f"\n[PDF PARSING] Total pages: {num_pages}", flush=True)
                sys.stdout.flush()
                
                for idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                    
                    if idx < 3 or idx == num_pages - 1 or (idx + 1) % 50 == 0:
                        print(f"  Page {idx + 1}/{num_pages}: {len(page_text) if page_text else 0} chars", flush=True)
                    sys.stdout.flush()
            
            print(f"[PDF PARSING] Total extracted text: {len(text)} characters\n", flush=True)
            sys.stdout.flush()
            return text
        except ImportError:
            # Fallback to PyPDF2
            print("[PDF PARSING] pdfplumber not available, using PyPDF2", flush=True)
            try:
                from PyPDF2 import PdfReader
                text = ""
                with open(file_path, 'rb') as f:
                    reader = PdfReader(f)
                    print(f"[PDF PARSING] Total pages: {len(reader.pages)}", flush=True)
                    for idx, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                        if idx < 3 or idx == len(reader.pages) - 1:
                            print(f"  Page {idx + 1}: {len(page_text) if page_text else 0} chars", flush=True)
                    print(f"[PDF PARSING] Total extracted text: {len(text)} characters", flush=True)
                sys.stdout.flush()
                return text
            except ImportError:
                raise ImportError("Either pdfplumber or PyPDF2 is required for PDF parsing")
    
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
    """Service removed - vector exports now handled directly in views"""
    pass
