from rest_framework import serializers
from .models import Grade, Subject, Document, Chunk, Embedding, VectorSnapshot


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name', 'description', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'grade', 'grade_name', 'created_at']


class ChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chunk
        fields = ['id', 'text', 'chunk_index']


class EmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embedding
        fields = ['id', 'vector', 'embedding_model']


class ChunkWithEmbeddingSerializer(serializers.ModelSerializer):
    embedding = EmbeddingSerializer(read_only=True)
    
    class Meta:
        model = Chunk
        fields = ['id', 'text', 'chunk_index', 'embedding']


class DocumentSerializer(serializers.ModelSerializer):
    chunks = ChunkWithEmbeddingSerializer(many=True, read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name = serializers.CharField(source='subject.grade.name', read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'subject', 'subject_name', 'grade_name', 'file_type', 'created_at', 'chunks']


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'subject', 'file_type']


class VectorSnapshotSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_grade = serializers.CharField(source='subject.grade.name', read_only=True)
    
    class Meta:
        model = VectorSnapshot
        fields = ['id', 'grade', 'grade_name', 'subject', 'subject_name', 'subject_grade', 
                  'snapshot_type', 'snapshot_file', 'created_at', 'updated_at']
