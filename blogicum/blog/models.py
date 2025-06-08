from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class BasePublicationModel(models.Model):
    """Базовая модель для публикаций."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True

    def __str__(self):
        publication_status = f"Published: {self.is_published}"
        creation_date = f"Created at: {self.created_at:%Y-%m-%d %H:%M}"
        return f"{publication_status}, {creation_date}"


class Location(BasePublicationModel):
    """Модель местоположения."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)

    def __str__(self):
        return f"{self.name[:50]} ({self.created_at:%Y-%m-%d})"


class Category(BasePublicationModel):
    """Модель категории для публикаций."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self):
        return f"{self.title[:50]} ({self.created_at:%Y-%m-%d})"


class Post(BasePublicationModel):
    """Модель публикации."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        verbose_name='Фото',
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.pk])

    def __str__(self):
        return f"{self.title[:50]} ({self.created_at:%Y-%m-%d})"


class Comment(models.Model):
    """Модель комментария."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    text = models.TextField('Текст')
    created_at = models.DateTimeField(
        'Дата и время создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        comment_info = f'{self.author.username}: {self.text[:50]}...'
        creation_date = f'({self.created_at:%Y-%m-%d %H:%M})'
        return f'{comment_info} {creation_date}'
