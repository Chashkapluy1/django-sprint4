from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
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


def filter_and_annotate_posts(posts, apply_filters=True,
                              use_select_related=True, apply_sorting=True):
    """Фильтрация, аннотирование и сортировка постов."""
    if apply_filters:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if use_select_related:
        posts = posts.select_related("category", "location", "author")
    if apply_sorting:
        posts = posts.order_by("-pub_date")
    posts = posts.annotate(comment_count=Count("comments"))
    return posts


class PostListView(ListView):
    """Список всех опубликованных постов."""

    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"
    paginate_by = PAGINATE_BY
    queryset = filter_and_annotate_posts(Post.objects.all())


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
        return filter_and_annotate_posts(self.get_category().posts.all())

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, category=self.get_category())


class PostDetailView(BasePostMixin, DetailView):
    """Детали поста."""

    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_object(self):
        post = super().get_object()
        if self.request.user == post.author:
            return post
        return super().get_object(
            queryset=Post.objects.filter(is_published=True))

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
        return reverse("blog:profile", args=[self.request.user.username])


class PostUpdateView(BasePostMixin, OwnerRequiredMixin, UpdateView):
    """Редактирование поста."""

    pk_url_kwarg = "post_id"
    form_class = PostForm
    template_name = "blog/create.html"

    def get_success_url(self):
        return reverse("blog:post_detail",
                       args=[self.kwargs[self.pk_url_kwarg]])


class PostDeleteView(BasePostMixin, LoginRequiredMixin,
                     OwnerRequiredMixin, DeleteView):
    """Удаление поста."""

    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")
    pk_url_kwarg = "post_id"


class ProfileView(BasePostMixin, ListView):
    """Профиль пользователя."""

    template_name = "blog/profile.html"
    paginate_by = PAGINATE_BY

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        author = self.get_author()
        if self.request.user == author:
            return author.posts.all()
        return filter_and_annotate_posts(author.posts.all())

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            profile=self.get_author(),
            is_owner=self.request.user == self.get_author()
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


class CommentDeleteView(LoginRequiredMixin, OwnerRequiredMixin,
                        CommentObjectMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def get_success_url(self):
        return reverse("blog:post_detail", args=[self.kwargs['post_id']])
