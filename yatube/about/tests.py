from http import HTTPStatus

from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about__author_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/author/."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about__tech_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/tech/."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_tech_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/author/ и /about/tech/."""
        template_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in template_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
