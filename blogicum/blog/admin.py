from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Category, Comment, Location, Post

admin.site.unregister(Group)


class BaseAdmin(admin.ModelAdmin):
    """Общие настройки для админки."""

    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('title', 'description', 'name', 'text')
    readonly_fields = ('created_at',)
    ordering = ['created_at']

    def get_list_display(self, request):
        list_display = [
            field.name for field in self.model._meta.fields
            if field.name != 'id'
        ]
        if hasattr(self.model, 'is_published'):
            list_display.append('is_published')
        return list_display


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'description', 'text')


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ('post', 'author', 'created_at', 'text')
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('author', 'created_at')
    list_editable = ('text',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    list_filter = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
