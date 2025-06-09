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

from .forms import CommentForm, PostForm
from .mixins import (
    BasePostMixin,
    CommentBaseMixin,
    CommentObjectMixin,
    OwnerRequiredMixin,
)
from .models import Category, Comment, Post, User


def apply_published_filter(posts, include_category=True,
                           include_location=True, **extra_filters):
    """Фильтрация опубликованных постов."""
    filter_conditions = {
        "is_published": True,
        "category__is_published": True,
        "pub_date__lte": timezone.now(),
    }
    filter_conditions.update(extra_filters)
    queryset = posts.filter(**filter_conditions)
    if include_category:
        queryset = queryset.select_related("category")
    if include_location:
        queryset = queryset.select_related("location")
    return queryset


class PostListView(ListView):
    """Список всех опубликованных постов."""

    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"
    paginate_by = 10

    def get_queryset(self):
        posts = Post.objects.all()
        queryset = apply_published_filter(posts)
        return queryset.annotate(comment_count=Count("comments")).order_by(
            "-pub_date"
        )


class CategoryPostsView(ListView):
    """Отображение постов в категории."""

    model = Post
    template_name = "blog/category.html"
    context_object_name = "post_list"
    paginate_by = 10

    def get_category(self):
        return get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )

    def get_queryset(self):
        category = self.get_category()
        posts = category.posts.all()
        queryset = apply_published_filter(posts)
        return queryset.annotate(comment_count=Count("comments")).order_by(
            "-pub_date"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.get_category()
        return context


class PostDetailView(BasePostMixin, DetailView):
    """Детали поста."""

    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        if not post.is_published and self.request.user != post.author:
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.get_object().comments.all()
        return context


class PostCreateView(BasePostMixin, LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user])


class PostUpdateView(BasePostMixin, OwnerRequiredMixin, UpdateView):
    """Редактирование поста."""

    pk_url_kwarg = "post_id"
    redirect_view_name = "blog:post_detail"
    form_class = PostForm
    template_name = "blog/create.html"

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={"post_id": self.kwargs["post_id"]})


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
    paginate_by = 10

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])
        posts = self.user.posts.all()
        return (
            posts.select_related("category", "location")
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "profile": self.user,
                "is_owner": self.request.user == self.user,
            }
        )
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    template_name = "blog/user.html"
    fields = ["first_name", "last_name", "username", "email"]

    def get_object(self, queryset=None):
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
        return reverse("blog:post_detail",
                       kwargs={"post_id": self.kwargs["post_id"]})
