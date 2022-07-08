from django.contrib.auth import get_user_model
from django.db import models

from .constants import SYMBOLS_PER_POST
from .validators import clean_text

User = get_user_model()


class Group(models.Model):
    """В базе данных создаётся модель для хранения информации о группах."""

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, verbose_name='Адрес')
    description = models.TextField(verbose_name='Описание')

    class Meta:

        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """В базе данных создаётся модель для хранения постов."""

    text = models.TextField(
        verbose_name='Текст поста',
        validators=[clean_text],
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:

        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:SYMBOLS_PER_POST]


class Comment(models.Model):
    """В базе данных создаётся модель для хранения комментариев."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='комментарии',
        help_text='введите комментарий к посту',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        validators=[clean_text],
        help_text='Введите текст поста',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )

    class Meta:

        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:SYMBOLS_PER_POST]


class Follow(models.Model):
    """В базе данных создаётся модель для подписки на пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='подписка',
    )

    class Meta:

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
