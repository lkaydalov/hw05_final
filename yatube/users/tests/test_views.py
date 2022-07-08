from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class UsersViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Writer')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        User.objects.create(
            first_name='User',
            last_name='Userovich',
            email='User128@user.com',
        )

        cls.form = CreationForm()

    def test_users_pages_uses_correct_template(self):
        """Проверяем, что view-классы используют ожидаемые
        HTML-шаблоны."""
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_change'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_confirm', kwargs={
                'uidb64': '1341-', 'token': '7171how-are'
            }): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:reset_complete'
            ): 'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_sign_up_gets_user_form(self):
        """Проверяем, что signup в контексте передаёт форму для
        создания нового пользователя."""
        response = self.authorized_client.get(
            reverse('users:signup'), data={
                'first_name': 'User',
                'last_name': 'Userovich',
                'email': 'User128@user.com',
            }, follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
