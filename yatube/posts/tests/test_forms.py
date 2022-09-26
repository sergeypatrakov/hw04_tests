from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostFormTests(TestCase):
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
        )
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(
            username='Has_no_Posts'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        reverse_address_profile = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        reverse_address_create = reverse('posts:post_create')
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse_address_create,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse_address_profile)
        self.assertEqual(
            Post.objects.count(),
            post_count + 1
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group.id,
            ).exists()
        )

    def test_post_edit(self):
        """Проверяем, что происходит изменение поста."""
        reverse_address_profile = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )
        reverse_address_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )
        post_id = Post.objects.get(id=self.post.pk).text
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse_address_edit,
            data=form_data,
            follow=True,
        )
        self.assertEqual(post_id, 'Тестовый текст')
        self.assertRedirects(response, reverse_address_profile)
