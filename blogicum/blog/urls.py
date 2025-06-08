from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Главная страница
    path('', views.PostListView.as_view(), name='index'),

    # Страница с деталями поста
    path('posts/<int:post_id>/', views.PostDetailView.as_view(),
         name='post_detail'),

    # Страница для редактирования комментария
    path('posts/<int:post_id>/comment/<int:comment_id>/edit_comment/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),

    # Страница для удаления комментария
    path('posts/<int:post_id>/comment/<int:comment_id>/delete_comment/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),

    # Просмотр постов в категории
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(),
         name='category_posts'),

    # Страница для создания нового поста
    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),

    # Страница для удаления поста
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),

    # Страница для добавления комментария
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),

    # Страница редактирования профиля.
    path('profile/edit/', views.ProfileEditView.as_view(),
         name='edit_profile'),

    # Страница профиля пользователя.
    path('profile/<str:username>/', views.ProfileView.as_view(),
         name='profile'),

    # Редактирование поста
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
]
