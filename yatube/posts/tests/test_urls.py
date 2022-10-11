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
            ('index', None, '/', 'posts/index.html'),
            (
                'group_list',
                (self.group.slug,),
                f'/group/{self.group.slug}/',
                'posts/group_list.html',
            ),
            (
                'profile',
                (self.user,),
                f'/profile/{self.user}/',
                'posts/profile.html',
            ),
            (
                'post_detail',
                (self.post.id,),
                f'/posts/{self.post.id}/',
                'posts/post_detail.html',
            ),
            (
                'post_edit',
                (self.post.id,),
                f'/posts/{self.post.id}/edit/',
                'posts/create_post.html',
            ),
            (
                'post_create',
                None,
                '/create/',
                'posts/create_post.html',
            ),
        )

    def test_unexisting_page_has_not_found(self):
        """Страница '/unexisting_page/' не существует."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_all_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, args, url, template in self.name_args_templates:
                with self.subTest(url=url):
                    response = self.author_client.get(url)
                    self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, args, url, template in self.name_args_templates:
            with self.subTest(name=name, url=url):
                self.assertEqual(url, reverse(f'posts:{name}', args=args))

    def test_all_url_available_author(self):
        """Все URL-адреса доступны автору."""
        for name, args, url, template in self.name_args_templates:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_url_available_not_author(self):
        """Все URL-адреса доступны НЕ автору."""
        for name, args, url, template in self.name_args_templates:
            with self.subTest(url=url):
                if name == 'post_edit':
                    response = self.authorized_client.get( 
                        reverse(
                            'posts:post_edit',
                            args=(self.post.id,),
                        )
                    )
                    response = self.authorized_client.get(
                        reverse(
                            'posts:post_detail',
                            args=(self.post.id,),
                        )
                    )
                else:
                    response = self.authorized_client.get('')
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    response = self.authorized_client.get(f'/group/{self.group.slug}/')
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    response = self.authorized_client.get(f'/profile/{self.user}/')
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    response = self.authorized_client.get('/create/')
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_url_available_guest(self):
        """Все URL-адреса доступны анониму."""
        login = reverse('users:login')
        for name, args, url, template in self.name_args_templates:
            if name == 'post_create':
                with self.subTest(url=url):
                    reverse_name = reverse(f'posts:{name}')
                    response = self.client.get(
                        '/create/',
                    )
                    self.assertRedirects(
                        response,
                        f'{login}?next={reverse_name}',
                    )
            elif name == 'post_edit':
                reverse_name = reverse(f'posts:{name}', args=args)
                response = self.client.get(
                    f'/posts/{self.post.id}/edit/',
                )
                self.assertRedirects(
                    response,
                    f'{login}?next={reverse_name}',
                )
            else:
                response = self.client.get('')
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.client.get(f'/group/{self.group.slug}/')
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.client.get(f'/profile/{self.user}/')
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.client.get(f'/posts/{self.post.id}/')
                self.assertEqual(response.status_code, HTTPStatus.OK)
