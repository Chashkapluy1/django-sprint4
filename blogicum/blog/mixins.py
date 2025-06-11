from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from .forms import CommentForm
from .models import Comment, Post


class BasePostMixin:
    """Базовый миксин для публикаций."""

    model = Post
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'


class OwnerRequiredMixin:
    """Проверка на владельца."""

    def dispatch(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
        except Http404:
            raise
        except Exception:
            raise Http404
        if obj.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentBaseMixin(LoginRequiredMixin):
    """Миксин для работы с комментариями."""

    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentObjectMixin:
    """Миксин для получения конкретного комментария."""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
