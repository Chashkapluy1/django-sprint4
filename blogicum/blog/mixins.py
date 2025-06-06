from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Comment, Post, User


class BasePostMixin:
    """Базовый миксин для публикаций."""

    model = Post
    context_object_name = 'post'


class OwnerRequiredMixin:
    """Проверка на владельца."""

    redirect_view_name = None
    redirect_pk_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        try:
            if self.get_object().author != request.user:
                return redirect(self.get_redirect_url(**kwargs))
        except Http404:
            raise
        except Exception:
            return redirect(self.get_redirect_url(**kwargs))
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        pk = kwargs.get(self.redirect_pk_kwarg) or self.kwargs.get(
            self.redirect_pk_kwarg)
        return reverse(self.redirect_view_name, kwargs={'pk': pk})


class PublishedPostsMixin:
    """Фильтрация публикаций."""

    paginate_by = 10

    @staticmethod
    def apply_published_filter(queryset):
        return queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related('category', 'location')

    def get_queryset(self):
        return self.apply_published_filter(super().get_queryset())


class CommentBaseMixin(LoginRequiredMixin):
    """Работа с комментариями."""

    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class CommentObjectMixin:
    """Конкретный комментарий."""

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post_id=self.kwargs['pk']
        )


class ProfileMixin:
    """Профиль пользователя."""

    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/profile.html'

    def get_profile_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_posts_queryset(self, user):
        return user.posts.select_related(
            'category',
            'location'
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')


class PostCreateUpdateMixin(LoginRequiredMixin):
    """Создание и обновление постов."""

    form_class = PostForm
    template_name = 'blog/create.html'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.created_at = form.instance.created_at or timezone.now()
        return super().form_valid(form)
