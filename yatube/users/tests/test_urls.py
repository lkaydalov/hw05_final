from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_for_all_users(self):
        """Проверка  доступа к  страницам входа, регистрации и выхода."""
        pages = ['/auth/login/', '/auth/signup/', '/auth/logout/']
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Ошибка доступа к странице {page}')

    def test_users_templates(self):
        """Страницы используют ожидаемые HTML-шаблоны."""
        templates_url = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in templates_url.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)
