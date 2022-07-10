import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        uploaded_edit = SimpleUploadedFile(
            name='big.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.uploaded = uploaded
        cls.uploaded_edit = uploaded_edit
        cls.author = User.objects.create_user(username='Authornew')
        cls.group = Group.objects.create(
            title='Тестовая группа_5',
            slug='first',
            description='Тестовое описание_5',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост_5',
            author=cls.author,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='тестим комменты',
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_authorized_user_creates_post(self):
        """Валидная форма создает запись в Post для
        авторизованного пользователя.
        """
        post_count = Post.objects.count()

        form_data = {
            'text': 'Текст из формы',
            'author': self.author,
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': f'{self.author.username}'}
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.first().text, form_data['text'])
        self.assertEqual(Post.objects.first().group.id, form_data['group'])
        self.assertEqual(Post.objects.first().author, form_data['author'])
        self.assertTrue(
            Post.objects.filter(
                image='posts/small.gif',
            ).exists()
        )

    def test_authorized_user_edits_post(self):
        """Валидная форма редактирует запись в Post
        для авторизованного пользователя.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы редактирования',
            'author': self.author,
            'group': self.group.id,
            'image': self.uploaded_edit,
        }
        response = self.authorized_author.post(
            reverse(
                ('posts:post_edit'), kwargs={'post_id': f'{self.post.id}'}
            ),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
        ))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(
            Post.objects.get(id=self.post.id).text, form_data['text']
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).author, form_data['author']
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).group.id, form_data['group']
        )
        self.assertTrue(
            Post.objects.filter(
                image='posts/big.gif'
            ).exists()
        )

    def test_authorized_user_comment(self):
        """Валидная форма создает комментарий для
        авторизованного пользователя.
        """
        comment_count = Comment.objects.count()

        form_data = {
            'text': 'тестим комменты',
        }
        response = self.authorized_author.post(
            reverse('posts:add_comment', kwargs={
                'post_id': f'{self.post.id}'
            }),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={
                'post_id': f'{self.post.id}'
            })
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(
            Comment.objects.get(id=self.post.id).text, form_data['text']
        )

    def test_unauthorized_user_comment(self):
        """Валидная форма не создает комментарий для
        авторизованного пользователя.
        """
        comment_count = Comment.objects.count()

        form_data = {
            'text': 'тестим комменты_111',
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': f'{self.post.id}'
            }),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count)
