from rest_framework import serializers
from .models import Course, Document, Chunk


class CourseSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'description', 'document_count', 'created_at', 'updated_at']
    
    def get_document_count(self, obj):
        return obj.documents.count()


class ChunkSerializer(serializers.ModelSerializer):
    """Chunks with vectors - use for download/export only"""
    document_title = serializers.CharField(source='document.title', read_only=True)
    document_file = serializers.CharField(source='document.file.name', read_only=True)
    course_code = serializers.CharField(source='document.course.code', read_only=True)
    
    class Meta:
        model = Chunk
        fields = ['id', 'text', 'chunk_index', 'vector', 'embedding_model', 'document_title', 'document_file', 'course_code']


class ChunkSummarySerializer(serializers.ModelSerializer):
    """Chunks without vectors - for API responses"""
    document_title = serializers.CharField(source='document.title', read_only=True)
    document_file = serializers.CharField(source='document.file.name', read_only=True)
    course_code = serializers.CharField(source='document.course.code', read_only=True)
    
    class Meta:
        model = Chunk
        fields = ['id', 'text', 'chunk_index', 'embedding_model', 'document_title', 'document_file', 'course_code', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    """Document without chunks - for list/retrieve"""
    course_code = serializers.CharField(source='course.code', read_only=True)
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'course', 'course_code', 'file', 'file_type', 'chunk_count', 'created_at']
    
    def get_chunk_count(self, obj):
        return obj.chunks.count()


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Document with chunk summaries (no vectors)"""
    chunks = ChunkSummarySerializer(many=True, read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'course', 'course_code', 'file', 'file_type', 'chunk_count', 'created_at', 'chunks']
    
    def get_chunk_count(self, obj):
        return obj.chunks.count()


class DocumentUploadSerializer(serializers.ModelSerializer):
    """For uploading documents"""
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'course', 'file_type']
