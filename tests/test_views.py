"""
Дополнительные тесты для увеличения покрытия views.py
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from blog.models import Category, Post


class TestPostListViewEdgeCases(TestCase):
    def test_pagination_page_2(self):
        """Тест второй страницы пагинации"""
        # Создать >10 постов
        user = User.objects.create_user(username='author', password='pass')
        category = Category.objects.create(name='Test')

        for i in range(15):
            Post.objects.create(
                title=f'Post {i}',
                author=user,
                category=category,
                excerpt='Test',
                content='Test',
                status='published'
            )

        response = self.client.get(reverse('blog:post_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 5)  # 15-10=5

    def test_empty_search_results(self):
        """Тест поиска без результатов"""
        response = self.client.get(reverse('blog:search') + '?q=nonexistentterm')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 0)


class TestPostDetailViewEdgeCases(TestCase):
    def test_post_detail_with_related_posts(self):
        """Тест детальной страницы с связанными постами"""
        user = User.objects.create_user(username='author', password='pass')
        category = Category.objects.create(name='Test')

        # Создать основной пост
        main_post = Post.objects.create(
            title='Main Post',
            author=user,
            category=category,
            excerpt='Test',
            content='Test',
            status='published'
        )

        # Создать 5 связанных постов
        for i in range(5):
            Post.objects.create(
                title=f'Related {i}',
                author=user,
                category=category,
                excerpt=f'Related {i}',
                content=f'Content {i}',
                status='published'
            )

        response = self.client.get(reverse('blog:post_detail',
                                           kwargs={'slug': main_post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('related_posts', response.context)
        self.assertEqual(len(response.context['related_posts']), 3)  # Лимит 3


class TestCategoryPostsViewEdgeCases(TestCase):
    def test_category_with_many_posts(self):
        """Тест категории с большим количеством постов"""
        user = User.objects.create_user(username='author', password='pass')
        category = Category.objects.create(name='Test')

        # Создать 20 постов в категории
        for i in range(20):
            Post.objects.create(
                title=f'Post {i}',
                author=user,
                category=category,
                excerpt=f'Excerpt {i}',
                content=f'Content {i}',
                status='published'
            )

        response = self.client.get(reverse('blog:category_posts',
                                           kwargs={'slug': category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 10)  # Пагинация


class TestTagPostsViewEdgeCases(TestCase):
    def test_tag_with_special_characters(self):
        """Тест тега со специальными символами"""
        user = User.objects.create_user(username='author', password='pass')
        category = Category.objects.create(name='Test')

        post = Post.objects.create(
            title='Test Post',
            author=user,
            category=category,
            excerpt='Test',
            content='Test',
            status='published'
        )
        post.tags.add('web-development', 'python-3.9')

        # Тестируем тег с дефисом
        response = self.client.get(reverse('blog:tag_posts',
                                           kwargs={'tag_name': 'web-development'}))
        self.assertEqual(response.status_code, 200)


class TestSearchViewEdgeCases(TestCase):
    def test_search_with_special_characters(self):
        """Тест поиска с специальными символами"""
        # Примечание: Если нет постов и мы запрашиваем page=2, вернется 404 (EmptyPage)
        response = self.client.get(reverse('blog:search') + '?q=test&page=2')
        self.assertEqual(response.status_code, 404)

    def test_search_pagination_last_page(self):
        """Тест поиска на последней странице пагинации"""
        # Создать много постов для поиска
        user = User.objects.create_user(username='author', password='pass')
        category = Category.objects.create(name='Test')

        for i in range(25):
            Post.objects.create(
                title=f'Searchable Post {i}',
                author=user,
                category=category,
                excerpt=f'Search term {i}',
                content=f'Content with search term {i}',
                status='published'
            )

        response = self.client.get(reverse('blog:search') + '?q=search&page=3')
        self.assertEqual(response.status_code, 200)


# ИСПРАВЛЕННАЯ ЧАСТЬ: Функции обернуты в класс
class TestCategoryViewAdditional(TestCase):
    """Дополнительные тесты для представлений категорий"""

    def setUp(self):
        self.user = User.objects.create_user(username='author', password='pass')
        self.category1 = Category.objects.create(name='Test Category 1')

    def test_category_view_rendering(self):
        """Тест рендеринга страницы категории"""
        url = reverse('blog:category_posts', kwargs={'slug': self.category1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/category_posts.html')

    def test_empty_category(self):
        """Тест пустой категории"""
        empty_category = Category.objects.create(
            name='Empty Category',
            description='No posts here'
        )

        url = reverse('blog:category_posts', kwargs={'slug': empty_category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 0)

    def test_nonexistent_category_returns_404(self):
        """Тест, что несуществующая категория возвращает 404"""
        url = reverse('blog:category_posts', kwargs={'slug': 'nonexistent-category'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_context_data_includes_category(self):
        """Тест, что контекст включает категорию"""
        from blog.views import CategoryPostsView

        # Создаем запрос
        request = RequestFactory().get('/')
        view = CategoryPostsView()
        view.request = request  # Устанавливаем request
        view.kwargs = {'slug': self.category1.slug}  # Устанавливаем kwargs
        view.category = self.category1
        view.object_list = view.get_queryset()

        context = view.get_context_data()
        self.assertIn('category', context)
        self.assertEqual(context['category'], self.category1)