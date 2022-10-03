from http import HTTPStatus

from django.test import Client, TestCase

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

    def test_index_url_exist_at_desired_location(self):
        """Страница '/' доступна любому пользователю."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list_url_exist_at_desired_location(self):
        """Страница '/group/<slug>/' доступна любому пользователю."""
        response = self.client.get(f'/group/{PostURLTests.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exist_at_desired_location(self):
        """Страница '/profile/<username>/' доступна любому пользователю."""
        response = self.client.get(f'/profile/{self.user}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_url_exist_at_desired_location(self):
        """Страница '/posts/<post_id>/' доступна любому пользователю."""
        response = self.client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exist_at_desired_location_author(self):
        """Страница '/posts/<post_id>/edit/' доступна только автору."""
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_url_exist_at_desired_location_authorized(self):
        """Страница '/create/' доступна только авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_has_not_found(self):
        """Страница '/unexisting_page/' не существует."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_all_url_available_author(self):
        """Все URL-адреса доступны автору."""
        code_answer = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
        }
        for address, code in code_answer.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_all_url_available_not_author(self):
        """Все URL-адреса доступны НЕ автору."""
        code_answer = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.OK,
        }
        for address, code in code_answer.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)
                response = self.authorized_client.get(
                    f'/posts/{self.post.id}/edit/', follow=True
                )
                self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_all_url_available_guest(self):
        """Все URL-адреса доступны анониму."""
        code_answer = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
        }
        for address, code in code_answer.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, code)
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
