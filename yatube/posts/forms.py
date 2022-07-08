from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для публикации новых постов и редактирования существующих."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Форма для публикации новых комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)
