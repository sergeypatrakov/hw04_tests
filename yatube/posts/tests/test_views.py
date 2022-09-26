from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author = cls.author,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user = User.objects.create_user(username='Has_no_Posts')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """View-функции используют соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}): 'posts/post_detail.html',
        }
        for reverse_name, templates in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, templates)

    def test_view_post_edit_uses_correct_template(self):
        """View-функция post_edit использует соответствующий шаблон."""
        template_name = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{int(PostPagesTests.post.pk)}'}): 'posts/create_post.html',
        }
        for reverse_name, templates in template_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, templates)

    def test_view_post_create_uses_correct_template(self):
        """View-функция post_create использует соответствующий шаблон."""
        template_name = {
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, templates in template_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, templates)


class PostContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user = User.objects.create_user(username='Has_no_Posts')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_second = User.objects.create_user(username='Second_user')
        self.authorized_client_second = Client()
        self.authorized_client_second.force_login(self.user_second)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        for post in response.context.get('page_obj'):
            self.assertIsInstance(post, Post)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)

    def test_group_posts_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        for post in response.context.get('page_obj'):
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        for post in response.context.get('page_obj'):
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        first_object = response.context.get('post')
        post_author = first_object.author
        post_text = first_object.text
        post_group = first_object.group
        post_id = Post.objects.get(pk=self.post.pk).text
        self.assertEqual(post_id, self.post.text)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.post.group)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form'
                ).fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field_name, field_type in form_fields.items():
            with self.subTest(
                field_name=field_name,
                field_type=field_type
            ):
                form_field = response.context.get(
                    'form'
                ).fields.get(field_name)
                self.assertIsInstance(form_field, field_type)

    def test_create_post_correct_create(self):
        """Проверяем, что пост появляется там, где надо."""
        response_index = self.authorized_client.get(reverse('posts:index'))
        response_group_list = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        response_profile = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        context_index = response_index.context.get('page_obj')
        context_group_list = response_group_list.context.get('page_obj')
        context_profile = response_profile.context.get('page_obj')
        self.assertNotIn(self.post.id, context_index)
        self.assertNotIn(self.post.id, context_group_list)
        self.assertNotIn(self.post.id, context_profile)
        group_second = Group.objects.create(
            title='Заголовок',
            slug='slug',
            description='Описание',
        )
        post_for_test = Post.objects.create(
            author=self.user_second,
            text='Текст',
            group=group_second,
        )
        response_index = self.authorized_client_second.get(
            reverse('posts:index')
        )
        response_group_list = self.authorized_client_second.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        response_profile = self.authorized_client_second.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        context_index = response_index.context.get('page_obj')
        context_group_list = response_group_list.context.get('page_obj')
        context_profile = response_profile.context.get('page_obj')
        self.assertIn(post_for_test, context_index)
        # self.assertIn(post_for_test, context_group_list)
        # self.assertIn(post_for_test, context_profile)
        # self.assertNotIn(post_for_test, self.group)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post_list = []
        for i in range(settings.TEST_POSTS):
            cls.post_list.append(Post(
                author=cls.author,
                text='Тестовый текст',
                group=cls.group,
            ))
        cls.post = Post.objects.bulk_create(cls.post_list)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user = User.objects.create_user(username='Nas_no_Posts')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_contains(self):
        """Проверяемм работу паджинатора."""
        pages = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            ),
        }
        for page in pages:
            with self.subTest(page=page):
                response_one = self.authorized_client.get(page)
                response_two = self.authorized_client.get(page + '?page=2')
                context_one = response_one.context.get('page_obj')
                context_two = len(response_two.context.get('page_obj'))
                post_for_two = len(self.post) - settings.NUMBER_OBJECTS
                self.assertIsInstance(context_one, Page)
                self.assertEqual(len(context_one), settings.NUMBER_OBJECTS)
                self.assertEqual(context_two, post_for_two)
