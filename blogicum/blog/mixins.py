from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from .forms import CommentForm
from .models import Comment, Post


class BasePostMixin:
    """Базовый миксин для публикаций."""

    model = Post
    context_object_name = "post"


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
            return redirect(self.get_redirect_url(**kwargs))
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        post_id = kwargs.get('post_id') or self.kwargs.get('post_id')
        return reverse('blog:post_detail', args=[post_id])


class CommentBaseMixin(LoginRequiredMixin):
    """Миксин для работы с комментариями."""

    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse("blog:post_detail", args=[self.kwargs["post_id"]])


class CommentObjectMixin:
    """Миксин для получения конкретного комментария."""

    model = Comment
    pk_url_kwarg = "comment_id"
