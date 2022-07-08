from django.contrib.auth import get_user_model
from django.test import TestCase

from ..constants import SYMBOLS_PER_POST
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, пишу пост длиннее пятнадцати символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        str_names = {
            post.text[:SYMBOLS_PER_POST]: str(post),
            group.title: str(group),
        }

        for model, expected_value in str_names.items():
            with self.subTest(model=model):
                self.assertEqual(
                    model, expected_value,
                    'Ошибка метода __str__'
                )

    def test_models_have_correct_verbose(self):
        """Проверяем verbose_name модели Post"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value,
                    'Ошибка verbose_name',
                )

    def test_models_have_correct_help_text(self):
        """Проверяем help_text модели Post"""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value,
                    'Ошибка help_text, как ты посмел',
                )
