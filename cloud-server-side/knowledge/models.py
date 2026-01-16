from django.db import models
import json


class Course(models.Model):
    """Course (e.g., SCI10, MATH09)"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Document(models.Model):
    """Document uploaded for a course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(
        max_length=10,
        choices=[('pdf', 'PDF'), ('txt', 'Text'), ('docx', 'Word')],
        default='txt'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"


class Chunk(models.Model):
    """Text chunk from document with vector embedding"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    text = models.TextField()
    chunk_index = models.IntegerField()
    # Store vector as JSON
    vector = models.JSONField()
    embedding_model = models.CharField(max_length=100, default='exp-models/dragonkue-KoEn-E5-Tiny-ONNX')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['document', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
