from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый_заголовок',
            slug='test-slug',
            description='Тестовое_описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый_текст',
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user = User.objects.create_user(username='Has_no_Posts')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.name_args_templates = (
            ('index', None, '/'),
            (
                'group_list',
                (self.group.slug,),
                f'/group/{PostURLTests.group.slug}/',
            ),
            ('profile', (self.user,), f'/profile/{self.user}/'),
            (
                'post_detail',
                (self.post.id,),
                f'/posts/{self.post.id}/',
            ),
            (
                'post_edit',
                (self.post.id,),
                f'/posts/{self.post.id}/edit/',
            ),
            ('post_create', None, '/create/'),
        )

    def test_unexisting_page_has_not_found(self):
        """Страница '/unexisting_page/' не существует."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, args, template in self.name_args_templates:
            with self.subTest(name=name, template=template):
                self.assertEqual(template, reverse(f'posts:{name}', args=args))

    def test_all_url_available_author(self):
        """Все URL-адреса доступны автору."""
        for name, args, url in self.name_args_templates:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_url_available_not_author(self):
        """Все URL-адреса доступны НЕ автору."""
        for name, args, url in self.name_args_templates:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                response = self.authorized_client.get(
                    f'/posts/{self.post.id}/edit/', follow=True
                )
                self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_all_url_available_guest(self):
        """Все URL-адреса доступны анониму."""
        for name, args, url in self.name_args_templates:
            with self.subTest(url=url):
                response = self.client.get(url)
                response = self.client.get(
                    '/create/',
                )
                self.assertRedirects(
                    response,
                    '/auth/login/?next=/create/',
                )
                response = self.client.get(
                    f'/posts/{self.post.id}/edit/',
                )
                self.assertRedirects(
                    response,
                    '/auth/login/?next=%2Fposts%2F1%2Fedit%2F',
                )
