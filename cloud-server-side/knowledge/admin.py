from django.contrib import admin
from .models import Course, Document, Chunk


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['code', 'name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'file_type', 'created_at']
    search_fields = ['title', 'course__code']
    list_filter = ['file_type', 'course']


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ['id', 'document', 'chunk_index', 'created_at']
    search_fields = ['document__title', 'text']
    list_filter = ['document']
