from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import Comment, Post, User


class ProfileEditForm(UserChangeForm):
    """Редактирование профиля пользователя."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    """Создание и редактирование комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """Создание и редактирование публикаций."""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            )
        }
