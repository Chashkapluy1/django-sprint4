from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from .forms import CommentForm
from .models import Comment, Post, User


class BasePostMixin:
    """Базовый миксин для публикаций."""

    model = Post
    context_object_name = 'post'


class OwnerRequiredMixin:
    """Проверка на владельца."""

    redirect_view_name = None
    redirect_post_id_kwarg = 'post_id'

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
        post_id = kwargs.get(self.redirect_post_id_kwarg) or \
                  self.kwargs.get(self.redirect_post_id_kwarg)
        return reverse(self.redirect_view_name, kwargs={'post_id': post_id})


def apply_published_filter(posts, include_category=True,
                           include_location=True, **extra_filters):
    """Фильтрация опубликованных постов с дополнительными параметрами."""
    filter_conditions = {
        'is_published': True,
        'category__is_published': True,
        'pub_date__lte': timezone.now()
    }
    filter_conditions.update(extra_filters)
    queryset = posts.filter(**filter_conditions)
    if include_category:
        queryset = queryset.select_related('category')
    if include_location:
        queryset = queryset.select_related('location')
    return queryset


class CommentBaseMixin(LoginRequiredMixin):
    """Работа с комментариями."""

    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentObjectMixin:
    """Конкретный комментарий."""

    model = Comment
    slug_field = 'comment_id'
    slug_url_kwarg = 'comment_id'


class ProfileView(LoginRequiredMixin):
    """Представление для профиля пользователя."""

    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/profile.html'

    def get_user_and_posts(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        posts = user.posts.select_related(
            'category', 'location'
        ).annotate(
            comment_count=Count('comment')
        ).order_by('-pub_date')
        return user, posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user, posts = self.get_user_and_posts()
        context['user'] = user
        context['posts'] = posts
        return context
