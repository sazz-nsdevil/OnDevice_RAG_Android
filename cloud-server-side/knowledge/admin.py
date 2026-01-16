from django.contrib import admin
from .models import Grade, Subject, Document, Chunk, Embedding, VectorSnapshot


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'created_at']
    search_fields = ['name', 'grade__name']
    list_filter = ['grade']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'file_type', 'created_at']
    search_fields = ['title', 'subject__name']
    list_filter = ['file_type', 'subject__grade', 'subject']


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'created_at']
    search_fields = ['document__title', 'text']
    list_filter = ['document__subject__grade']


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ['chunk', 'embedding_model', 'created_at']
    search_fields = ['chunk__document__title']
    list_filter = ['embedding_model']


@admin.register(VectorSnapshot)
class VectorSnapshotAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'snapshot_type', 'created_at']
    list_filter = ['snapshot_type', 'grade', 'subject']
    search_fields = ['grade__name', 'subject__name']
