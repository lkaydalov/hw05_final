from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Writer')
        cls.user_not_author = User.objects.create_user(username='not_author')
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_not_author = Client()
        self.authorized_not_author.force_login(self.user_not_author)
        cache.clear()

    def test_pages_for_all_authorized_author(self):
        """Проверка  доступа авторизованного пользователя ко всем страницам."""
        pages = [
            '/',
            '/group/test-slug/',
            '/profile/Writer/',
            '/posts/1/',
            '/posts/1/edit/',
            '/create/'
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_author.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Ошибка доступа к странице {page}')

    def test_add_comment_authorized_author_(self):
        """Проверка  доступа авторизованного пользователя к комментариям."""
        resposne = self.authorized_author.get(
            reverse('posts:add_comment', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertRedirects(
            resposne, ('/posts/1/')
        )

    def test_add_comment_not_authorized_author_(self):
        """Проверка доступа гостя к комментариям."""
        resposne = self.client.get(
            reverse('posts:add_comment', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertRedirects(
            resposne, ('/auth/login/?next=/posts/1/comment/')
        )

    def test_post_edit_url_redirect_not_author(self):
        """Страница по адресу /post_edit/ перенаправит авторизованного не автора поста
        на страницу просмотра поста.
        """
        response = self.authorized_not_author.get(
            '/posts/1/edit/', follow=True,
        )
        self.assertRedirects(
            response, ('/posts/1/')
        )

    def test_unexisting_page(self):
        """Страница по адресу /unexisting_page/ возвращает ошибку 404."""
        response = self.authorized_author.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/Writer/': 'posts/profile.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_for_all_guest_clients(self):
        """Проверка доступа гостя к приватным страницам."""
        pages = {
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for page, redirects in pages.items():
            with self.subTest(page=page):
                response = self.client.get(page, follow=True)
                self.assertRedirects(response, redirects)
