from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


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
        self.author_client = Client()
        self.author_client.force_login(self.author)
 
    def check_data(self, request, is_post=False):
        response = self.author_client.get(request)
        if is_post:
            first_object = response.context.get('post')
            post_author = first_object.author
            post_text = first_object.text
            post_group = first_object.group
            post_id = Post.objects.get(pk=self.post.pk).text
            self.assertEqual(post_id, self.post.text)
            self.assertEqual(post_author, self.post.author)
            self.assertEqual(post_text, self.post.text)
            self.assertEqual(post_group, self.post.group)
            return 
        response = self.author_client.get(request)
        for post in response.context.get('page_obj'):
            self.assertIsInstance(post, Post)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)
 
    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        self.check_data(reverse('posts:index'))
 
    def test_group_posts_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        self.check_data(
            reverse(
                'posts:group_list',
                args=(self.group.slug,),
            )
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        self.check_data(
            reverse(
                'posts:profile',
                args=(self.author.username,),
            )
        )
 
    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        self.check_data(
            reverse(
                'posts:post_detail',
                args=(self.post.pk,),
            ),
            True
        )

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
        for pryanik in range(settings.TEST_POSTS):
            cls.post_list.append(Post(
                author=cls.author,
                text='Тестовый текст ' + str(pryanik),
                group=cls.group,
            ))
        cls.post = Post.objects.bulk_create(cls.post_list)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_paginator_contains(self):
        """Проверяемм работу паджинатора."""
        pages = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.author.username,)),
        )
        data = (
                ('?page=1', settings.NUMBER_OBJECTS),
                ('?page=2', settings.TEST_PAGINATOR),
        )
        for page in pages:
            with self.subTest(page=page):
                for url, number_posts in data:
                    response = self.author_client.get(page + url)
                    context = response.context.get('page_obj')
                    self.assertEqual(len(context), number_posts)
