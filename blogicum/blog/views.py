from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm
from .mixins import (
    BasePostMixin, CommentBaseMixin, CommentObjectMixin,
    OwnerRequiredMixin, PostCreateUpdateMixin, ProfileMixin,
    PublishedPostsMixin
)
from .models import Category, Comment, Post, User


class PostDetailView(BasePostMixin, DetailView):
    """Детали поста."""

    template_name = 'blog/detail.html'
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if not post.is_published and self.request.user != post.author:
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': CommentForm(),
            'comments': self.object.comment_set.select_related('author')
        })
        return context


class ProfileView(PublishedPostsMixin, ProfileMixin, ListView):
    """Профиль пользователя"""

    def get_queryset(self):
        self.profile_user = self.get_profile_user()
        queryset = self.get_posts_queryset(self.profile_user)

        if self.request.user != self.profile_user:
            queryset = self.apply_published_filter(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'profile': self.profile_user,
            'is_owner': self.request.user == self.profile_user
        })
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(CommentBaseMixin, CreateView):
    """Создание комментария к посту."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['pk']
        )
        return super().form_valid(form)


class CommentUpdateView(CommentBaseMixin, OwnerRequiredMixin,
                        CommentObjectMixin, UpdateView):
    """Редактирование комментария."""

    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    redirect_view_name = 'blog:post_detail'
    redirect_pk_kwarg = 'pk'


class CommentDeleteView(LoginRequiredMixin, OwnerRequiredMixin,
                        CommentObjectMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    redirect_view_name = 'blog:post_detail'
    redirect_pk_kwarg = 'pk'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class PostListView(PublishedPostsMixin, ListView):
    """Список всех опубликованных постов."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(location__isnull=True) | Q(location__is_published=True)
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')


class CategoryPostsView(PublishedPostsMixin, ListView):
    """Отображение постов в категории."""

    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().get_queryset().filter(
            category=self.category
        ).filter(
            Q(location__isnull=True) | Q(location__is_published=True)
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')


class PostCreateView(BasePostMixin, PostCreateUpdateMixin, CreateView):
    """Создание нового поста."""

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(BasePostMixin, PostCreateUpdateMixin,
                     OwnerRequiredMixin, UpdateView):
    """Редактирование поста."""

    pk_url_kwarg = 'pk'
    redirect_view_name = 'blog:post_detail'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.object.pk}
        )


class PostDeleteView(BasePostMixin, LoginRequiredMixin,
                     OwnerRequiredMixin, DeleteView):
    """Удаление поста."""

    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'pk'
    redirect_view_name = 'blog:post_detail'


class ProfilePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Изменение пароля."""

    template_name = 'registration/password_change_form.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )
