from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm, ProfileEditForm
from .mixins import (
    BasePostMixin,
    CommentBaseMixin,
    CommentObjectMixin,
    OwnerRequiredMixin,
)
from .models import Category, Comment, Post, User

PAGINATE_BY = 10


def apply_published_filter(posts, apply_filters=True):
    """Фильтрация опубликованных постов."""
    if apply_filters:
        filtered_posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    else:
        filtered_posts = posts
    filtered_posts = filtered_posts.select_related(
        "category", "location", "author"
    )
    filtered_posts = filtered_posts.annotate(comment_count=Count('comments'))
    return filtered_posts


class PostListView(ListView):
    """Список всех опубликованных постов."""

    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"
    paginate_by = PAGINATE_BY
    queryset = apply_published_filter(Post.objects.all()).annotate(
        comment_count=Count("comments")
    ).order_by("-pub_date")


class CategoryPostsView(ListView):
    """Отображение постов в категории."""

    model = Post
    template_name = "blog/category.html"
    context_object_name = "post_list"
    paginate_by = PAGINATE_BY

    def get_category(self):
        return get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )

    def get_queryset(self):
        category = self.get_category()
        if self.request.user.is_authenticated:
            author = self.request.user
        else:
            author = None
        return (
            apply_published_filter(category.posts.all())
            .filter(author=author)
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, category=self.get_category())


class PostDetailView(BasePostMixin, DetailView):
    """Детали поста."""

    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_object(self):
        post = super().get_object()
        if not post.is_published and self.request.user != post.author:
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comments=self.get_object().comments.all()
        )


class PostCreateView(BasePostMixin, LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile", args=[str(self.request.user.username)])


class PostUpdateView(BasePostMixin, OwnerRequiredMixin, UpdateView):
    """Редактирование поста."""

    pk_url_kwarg = "post_id"
    redirect_view_name = "blog:post_detail"
    form_class = PostForm
    template_name = "blog/create.html"

    def get_success_url(self):
        return reverse(self.redirect_view_name,
                       args=[self.kwargs[self.pk_url_kwarg]])


class PostDeleteView(BasePostMixin, LoginRequiredMixin,
                     OwnerRequiredMixin, DeleteView):
    """Удаление поста."""

    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")
    pk_url_kwarg = "post_id"
    redirect_view_name = "blog:post_detail"


class ProfileView(BasePostMixin, ListView):
    """Профиль пользователя."""

    template_name = "blog/profile.html"
    paginate_by = PAGINATE_BY

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        user = self.get_user()
        posts = (
            user.posts.all() if self.request.user == user
            else apply_published_filter(user.posts.all())
        )
        return posts.select_related("category", "location").annotate(
            comment_count=Count("comments")
        ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            profile=self.get_user(),
            is_owner=self.request.user == self.get_user()
        )


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    template_name = "blog/user.html"
    form_class = ProfileEditForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user.username])


class CommentCreateView(CommentBaseMixin, CreateView):
    """Создание комментария к посту."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return super().form_valid(form)


class CommentUpdateView(CommentBaseMixin, OwnerRequiredMixin,
                        CommentObjectMixin, UpdateView):
    """Редактирование комментария."""

    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"
    redirect_view_name = "blog:post_detail"
    redirect_pk_kwarg = "post_id"


class CommentDeleteView(LoginRequiredMixin, OwnerRequiredMixin,
                        CommentObjectMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"
    redirect_view_name = "blog:post_detail"
    redirect_pk_kwarg = "post_id"

    def get_success_url(self):
        return reverse(self.redirect_view_name,
                       args=[self.kwargs[self.redirect_pk_kwarg]])
