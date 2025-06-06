from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import Comment, Post, User


class ProfileEditForm(UserChangeForm):
    """Редактирование профиля пользователя."""

    password = None

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)
        exclude = ('password',)


class CommentForm(forms.ModelForm):
    """Создание и редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """Создание и редактирования публикаций."""

    class Meta:
        model = Post
        fields = [
            'title', 'text', 'pub_date',
            'image', 'category', 'location', 'is_published'
        ]
        widgets = {
            'pub_date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            )
        }
