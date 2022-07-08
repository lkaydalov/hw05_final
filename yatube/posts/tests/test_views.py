import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow
from ..constants import (POSTS_PER_PAGE,
                         POSTS_PER_PAGE_TEST,
                         TEST_POSTS_QUANTITY)

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
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
            content_type='image/gif'
        )
        cls.author = User.objects.create_user(username='Writer')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """Проверяем, что view-классы используют ожидаемые
        HTML-шаблоны."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': 'test-slug',
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': f'{self.author.username}',
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': f'{self.post.id}',
            }): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.id}',
            }): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_list_page_context(self):
        """Проверяем контекст страницы групп."""
        response = self.authorized_author.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{self.group.slug}'},
        ))
        self.assertEqual(
            response.context['group'].title, self.group.title
        )
        self.assertEqual(
            response.context['group'].slug, self.group.slug
        )
        self.assertEqual(
            response.context['group'].description, self.group.description
        )

    def test_main_pages_context(self):
        """Проверяем контекст paje_obj у страниц:
        index, group_list, profile.
        """
        pages = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={
                'username': f'{self.author.username}'
            }),
            reverse('posts:group_list', kwargs={
                'slug': f'{self.group.slug}'
            }),
        ]
        for address in pages:
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertEqual(
                    response.context['page_obj'][0].text, self.post.text
                )
                self.assertEqual(
                    response.context['page_obj'][0].author.username,
                    self.author.username,
                )
                self.assertEqual(
                    response.context['page_obj'][0].group.title,
                    self.group.title,
                )
                self.assertEqual(
                    response.context['page_obj'][0].image.name,
                    'posts/small.gif',
                )

    def test_post_detail_page_context(self):
        """Проверяем контекст страницы деталей поста."""
        response = self.authorized_author.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{self.post.id}'},
        ))
        self.assertEqual(response.context['post'].id, self.post.id)
        self.assertEqual(
            response.context['post'].group.title, self.group.title
        )
        self.assertEqual(response.context['post'].group.id, self.group.id)
        self.assertEqual(response.context['post'].author, self.author)
        self.assertEqual(
            response.context['post'].image.name,
            'posts/small.gif',
        )

    def test_post_create_page_context(self):
        """Проверяем контекст страницы создания поста."""
        response = self.authorized_author.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_context(self):
        """Проверяем контекст страницы профиля."""
        resposne = self.authorized_author.get(
            reverse('posts:profile', kwargs={
                'username': f'{self.author.username}'
            })
        )
        self.assertEqual(
            resposne.context['author'].username, self.author.username
        )
        self.assertEqual(
            resposne.context['author'].posts.count, self.author.posts.count
        )
        self.assertEqual(
            resposne.context['author'].get_full_name, self.author.get_full_name
        )

    def test_post_edit_page_context(self):
        """Проверяем контекст страницы редактирования поста."""
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_cache_20_seconds(self):
        """Проверяем кэш."""
        post_cache = Post.objects.create(
            text='Тестим кеш',
            author=self.author,
            group=self.group,
        )
        response = self.authorized_author.get(reverse('posts:index'))
        posts = response.content
        post_cache.delete()
        response_old = self.authorized_author.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(posts, old_posts)
        cache.clear()
        response_new = self.authorized_author.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа_0',
            slug='test-slug_0',
            description='Тестовое описание_0',
        )

        obj = [
            Post(
                text=f'Тестовый текст {i}',
                author=cls.author,
                group=cls.group,
            )
            for i in range(TEST_POSTS_QUANTITY)
        ]

        Post.objects.bulk_create(obj)

    def test_first_page_contains_ten_records(self):
        """Первая страница index содержит десять записей."""
        response = self.authorized_author.get(reverse('posts:index'))
        self.assertEquals(
            len(response.context['page_obj']), POSTS_PER_PAGE
        )

    def test_second_page_contains_three_records(self):
        """Вторая страница index содердит три записи."""
        response = self.authorized_author.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEquals(
            len(response.context['page_obj']), POSTS_PER_PAGE_TEST
        )

    def test_first_page_group_list_contains_ten_records(self):
        """Первая страница group_list содержит десять записей."""
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEquals(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_page_group_list_contains_three_records(self):
        """Вторая страница group_list содердит три записи."""
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={
                'slug': f'{self.group.slug}'
            }) + '?page=2'
        )
        self.assertEquals(
            len(response.context['page_obj']), POSTS_PER_PAGE_TEST
        )

    def test_first_page_profile_contains_ten_records(self):
        """Первая страница profile содержит десять записей."""
        response = self.authorized_author.get(
            reverse('posts:profile', kwargs={
                'username': f'{self.author.username}'
            })
        )
        self.assertEquals(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_page_profile_contains_three_records(self):
        """Вторая страница profile содердит три записи."""
        response = self.authorized_author.get(
            reverse('posts:profile', kwargs={
                'username': f'{self.author.username}'
            }) + '?page=2'
        )
        self.assertEquals(
            len(response.context['page_obj']), POSTS_PER_PAGE_TEST
        )


class GroupViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Authornew')
        cls.authorized_author = Client()
        cls.group = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug_2',
            description='Тестовое описание_2',
        )

        Post.objects.create(
            text='Тестовый пост_2',
            author=cls.author,
            group=cls.group,
        )

        cls.group_1 = Group.objects.create(
            title='Тестовая группа_3',
            slug='test-slug_3',
            description='Тестовое описание_3',
        )

    def setUp(self):
        self.authorized_author.force_login(self.author)
        cache.clear()

    def test_post_in_index(self):
        """Пост при создании с указанной группой
        отображается на главной странице.
        """
        response = self.authorized_author.get(
            reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), Post.objects.count()
        )

    def test_post_in_profile(self):
        """Пост при создании с указанной группой
        отображается на странице profile.
        """
        response = self.authorized_author.get(
            reverse('posts:profile', kwargs={
                'username': f'{self.author.username}'
            }))
        self.assertEqual(
            len(response.context['page_obj']), Post.objects.count()
        )

    def test_post_in_group(self):
        """Пост при создании с указанной группой
        отображается на странице группы.
        """
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        self.assertEqual(
            len(response.context['page_obj']), Post.objects.count()
        )

    def test_post_not_in_else_group(self):
        """Пост при создании с указанной группой
        не отображается на странице другой группы.
        """
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={
                'slug': f'{self.group_1.slug}'
            }))
        self.assertEqual(
            len(response.context['page_obj']), self.group_1.posts.count()
        )
        Post.objects.create(
            text="Test text", author=self.author, group=self.group)
        cache.clear()
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={
                'slug': f'{self.group_1.slug}'
            }))
        self.assertEqual(
            len(response.context['page_obj']), self.group_1.posts.count()
        )


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Follower')
        cls.author_1 = User.objects.create_user(username='Follower_1')
        cls.user = User.objects.create_user(username='Following')
        cls.authorized_author = Client()
        cls.authorized_user = Client()
        cls.post_author = Post.objects.create(
            text='Лол',
            author=cls.author,
        )
        cls.post_user = Post.objects.create(
            text='Тест',
            author=cls.author_1,
        )

    def setUp(self):
        self.authorized_author.force_login(self.author)
        self.authorized_user.force_login(self.user)

    def test_profile_follow(self):
        """Авторизованный польззователь может подписываться на других
        пользователей.
        """
        count_before = Follow.objects.count()
        count_posts_before = Post.objects.filter(author__following__user=self.author).count()
        self.authorized_author.post(
            reverse('posts:profile_follow', kwargs={
                'username': f'{self.author_1.username}'
            })
        )
        count_objects_after = Follow.objects.count()
        count_posts_after = Post.objects.filter(
            author__follower__user=self.author
        ).count()
        self.assertEqual(count_before + 1, count_objects_after)
        self.assertEqual(count_posts_before + 1, count_posts_after)

    def test_profile_follow_unauthorized(self):
        """Неавторизованный польззователь не может подписываться на других
        пользователей.
        """
        count_before = Follow.objects.count()
        count_posts_before = Post.objects.filter(author__follower__user=self.author).count()
        self.client.post(
            reverse('posts:profile_follow', kwargs={
                'username': f'{self.author_1.username}'
            })
        )
        count_objects_after = Follow.objects.count()
        count_posts_after = Post.objects.filter(
            author__follower__user=self.author
        ).count()
        self.assertEqual(count_before, count_objects_after)
        self.assertEqual(count_posts_before, count_posts_after)

    def test_profile_unfollow(self):
        """Авторизованный польззователь может удалять
        других пользователей из подписок.
        """
        count_before = Follow.objects.count()
        count_posts_before = Post.objects.filter(author__follower__user=self.author).count()
        self.authorized_author.post(
            reverse('posts:profile_unfollow', kwargs={
                'username': f'{self.author_1.username}'
            })
        )
        count_objects_after = Follow.objects.count()
        count_posts_after = Post.objects.filter(
            author__follower__user=self.author
        ).count()
        self.assertEqual(count_before, count_objects_after)
        self.assertEqual(count_posts_before, count_posts_after)

    def test_new_post_appears_for_followers(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан.
        """
        Follow.objects.create(
            author=self.author_1,
            user=self.user,
        )
        Post.objects.create(
            text='Тест1',
            author=self.author_1,
        )
        response = self.authorized_user.get(reverse(
            'posts:follow_index',
        ))
        self.assertEqual(
            response.context['page_obj'][0].author.id, self.author_1.id
        )
    def test_new_post_appears_for_followers(self):
        """Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан.
        """
        Follow.objects.create(
            author=self.author,
            user=self.user,
        )
        Post.objects.create(
            text='Тест2',
            author=self.author_1,
        )
        response = self.authorized_user.get(reverse(
            'posts:follow_index',
        ))
        self.assertNotEqual(
            response.context['page_obj'][0].author.id, self.author_1.id
        )
