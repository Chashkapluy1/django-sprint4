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
        return [
            field.name for field in self.model._meta.fields
            if field.name != 'id'
        ]


@admin.register(Category, Location, Post)
class DefaultAdmin(BaseAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('text', 'author__username', 'post__title',)
