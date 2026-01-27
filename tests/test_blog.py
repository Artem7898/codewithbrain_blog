from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Category, Post


class TestBlogViews(TestCase):
    """Тесты основных представлений блога"""

    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(username='author', password='pass')
        # Создаем категорию
        self.category = Category.objects.create(name='Test Category')
        # Создаем опубликованный пост
        self.published_post = Post.objects.create(
            title='Published Post',
            author=self.user,
            category=self.category,
            excerpt='Test',
            content='Test',
            status='published'
        )
        # Создаем черновик
        self.draft_post = Post.objects.create(
            title='Draft Post',
            author=self.user,
            category=self.category,
            excerpt='Test',
            content='Test',
            status='draft'
        )

    def test_post_list_view(self):
        """Тест списка постов"""
        # Используем правильный URL
        url = reverse('blog:post_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Проверяем, что только опубликованные посты отображаются
        self.assertContains(response, 'Published Post')
        self.assertNotContains(response, 'Draft Post')

    def test_category_view(self):
        """Тест страницы категории"""
        # Используем правильный URL
        url = reverse('blog:category_posts', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')
        self.assertContains(response, 'Published Post')

    def test_tag_view(self):
        """Тест страницы тегов"""
        # Добавляем тег к посту
        self.published_post.tags.add('django')

        # Используем правильный URL
        url = reverse('blog:tag_posts', kwargs={'tag_name': 'django'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'django')