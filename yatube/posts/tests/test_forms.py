# Тесты форм

# 1 Протестировать, что при отправке валидной формы со страницы
#   создания поста reverse('posts:create_post') создается новая запись в базе данных

# 2 Протестировать, что при отправке валидной формы со страницы
#   редактирования поста reverse('posts:post_edit', args=('post_id',))
#   происходит изменение поста с post_id в базе данных

# Доп: Проверить что при запорлнении формы reverse('users:signup')
#      создается новый пользователь

import shutil
import tempfile

from ..forms import PostForm
from ..models import Group, Post
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


# Создаем временную папку для медиа-файлов
# на момент теста медиа папка будет переполнена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            slug='slug-test-1'
        )
        # Создаем форму если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        super().setUp()
        self.guest_client = Client()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Для тестирования загрузки изображений 
        # берём байт-последовательность картинки, 
        # состоящей из двух пикселей: белого и чёрного
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
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:index'),
            data=form_data,
            follow=True
        )
        # Проверяем сработал ли редирект
        self.assertRedirects(response, reverse('posts:task_added'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count+1)
        # Проверяем, что сорздалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                slug='testovy-zagolovok',
                text='Тестовый текст',
                image='tasks/small.gif'
            ).exists()
        )
