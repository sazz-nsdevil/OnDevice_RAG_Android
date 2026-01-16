from django.db import models
import json

class Grade(models.Model):
    """Grade level (e.g., Grade 7, Grade 8, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Subject(models.Model):
    """Subject within a grade (e.g., Science, Mathematics)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('name', 'grade')
        ordering = ['grade', 'name']
    
    def __str__(self):
        return f"{self.grade.name} - {self.name}"


class Document(models.Model):
    """Uploaded document for knowledge base"""
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='documents')
    file_type = models.CharField(
        max_length=10, 
        choices=[('pdf', 'PDF'), ('txt', 'Text'), ('docx', 'Word')],
        default='txt'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject.grade.name} - {self.subject.name} - {self.title}"


class Chunk(models.Model):
    """Text chunks extracted from documents"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    text = models.TextField()
    chunk_index = models.IntegerField()  # Order of chunk within document
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document', 'chunk_index']
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"


class Embedding(models.Model):
    """Vector embeddings for chunks"""
    chunk = models.OneToOneField(Chunk, on_delete=models.CASCADE, related_name='embedding')
    # Store embedding as JSON list for simplicity
    vector = models.JSONField()  # List of floats
    embedding_model = models.CharField(max_length=100, default='dragonkue-KoEn-E5-Tiny')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['chunk']
    
    def __str__(self):
        return f"Embedding for {self.chunk}"


class VectorSnapshot(models.Model):
    """Exported vector snapshots for mobile download"""
    SNAPSHOT_TYPE_CHOICES = [
        ('grade', 'Grade'),
        ('subject', 'Subject'),
    ]
    
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    snapshot_type = models.CharField(max_length=20, choices=SNAPSHOT_TYPE_CHOICES)
    snapshot_file = models.FileField(upload_to='snapshots/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.snapshot_type == 'subject':
            return f"Snapshot - {self.subject}"
        return f"Snapshot - {self.grade}"
