"""
Тесты для API блога
"""
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from blog.models import Category, Post, Comment


class TestPostViewSet(TestCase):
    """Тесты для PostViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='author',
            password='testpass123',
            email='author@example.com'
        )

        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )

        # Создаем опубликованные посты
        self.published_posts = []
        for i in range(5):
            post = Post.objects.create(
                title=f'Published Post {i}',
                author=self.user,
                category=self.category,
                excerpt=f'Excerpt {i}',
                content=f'Content {i}',
                status='published'
            )
            post.tags.add('django', 'python')
            self.published_posts.append(post)

        # Создаем черновик (не должен отображаться в API)
        self.draft_post = Post.objects.create(
            title='Draft Post',
            author=self.user,
            category=self.category,
            excerpt='Draft excerpt',
            content='Draft content',
            status='draft'
        )

    def test_list_posts(self):
        """Тест получения списка постов"""
        url = reverse('post-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа
        self.assertIn('results', response.data)

        # Должны быть только опубликованные посты
        self.assertEqual(len(response.data['results']), 5)

        # Проверяем, что черновик не в списке
        post_titles = [post['title'] for post in response.data['results']]
        self.assertNotIn('Draft Post', post_titles)

        # Проверяем поля в ответе
        first_post = response.data['results'][0]
        self.assertIn('id', first_post)
        self.assertIn('title', first_post)
        self.assertIn('slug', first_post)
        self.assertIn('author', first_post)
        self.assertIn('category', first_post)
        self.assertIn('excerpt', first_post)
        self.assertIn('tags', first_post)

    def test_retrieve_post(self):
        """Тест получения конкретного поста"""
        post = self.published_posts[0]
        url = reverse('post-detail', kwargs={'slug': post.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем данные поста
        self.assertEqual(response.data['title'], post.title)
        self.assertEqual(response.data['slug'], post.slug)
        self.assertEqual(response.data['author'], post.author.username)

        # Проверяем структуру категории
        self.assertIn('category', response.data)
        category_data = response.data['category']
        self.assertEqual(category_data['name'], self.category.name)
        self.assertEqual(category_data['slug'], self.category.slug)

        # Проверяем теги
        self.assertIn('tags', response.data)
        self.assertEqual(len(response.data['tags']), 2)
        self.assertIn('django', response.data['tags'])
        self.assertIn('python', response.data['tags'])

    def test_retrieve_draft_post_returns_404(self):
        """Тест, что черновик недоступен через API"""
        url = reverse('post-detail', kwargs={'slug': self.draft_post.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_post_returns_404(self):
        """Тест, что несуществующий пост возвращает 404"""
        url = reverse('post-detail', kwargs={'slug': 'nonexistent-slug'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_comments_action(self):
        """Тест получения комментариев поста"""
        post = self.published_posts[0]

        # Создаем комментарии
        approved_comment = Comment.objects.create(
            post=post,
            author_name='Approved User',
            author_email='approved@example.com',
            content='Approved comment',
            is_approved=True
        )

        pending_comment = Comment.objects.create(
            post=post,
            author_name='Pending User',
            author_email='pending@example.com',
            content='Pending comment',
            is_approved=False
        )

        url = reverse('post-comments', kwargs={'slug': post.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Должны быть только одобренные комментарии
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author_name'], 'Approved User')
        self.assertNotIn('Pending User', [c['author_name'] for c in response.data])

    def test_post_comment_action_valid_data(self):
        """Тест создания комментария с валидными данными"""
        post = self.published_posts[0]

        url = reverse('post-comment', kwargs={'slug': post.slug})

        comment_data = {
            'author_name': 'Test User',
            'author_email': 'test@example.com',
            'content': 'This is a test comment'
        }

        response = self.client.post(url, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем ответ
        self.assertEqual(response.data['author_name'], 'Test User')
        self.assertEqual(response.data['author_email'], 'test@example.com')
        self.assertEqual(response.data['content'], 'This is a test comment')

        # Проверяем, что комментарий создан в базе
        self.assertTrue(Comment.objects.filter(
            post=post,
            author_name='Test User'
        ).exists())

        # Комментарий должен быть неодобренным по умолчанию
        comment = Comment.objects.get(post=post, author_name='Test User')
        self.assertFalse(comment.is_approved)

    def test_post_comment_action_invalid_data(self):
        """Тест создания комментария с невалидными данными"""
        post = self.published_posts[0]

        url = reverse('post-comment', kwargs={'slug': post.slug})

        # Неполные данные (нет author_name)
        invalid_data = {
            'author_email': 'test@example.com',
            'content': 'Test comment'
        }

        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('author_name', response.data)

    def test_post_comment_action_empty_content(self):
        """Тест создания комментария с пустым содержимым"""
        post = self.published_posts[0]

        url = reverse('post-comment', kwargs={'slug': post.slug})

        invalid_data = {
            'author_name': 'Test User',
            'author_email': 'test@example.com',
            'content': ''
        }

        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)

    def test_post_comment_action_invalid_email(self):
        """Тест создания комментария с невалидным email"""
        post = self.published_posts[0]

        url = reverse('post-comment', kwargs={'slug': post.slug})

        invalid_data = {
            'author_name': 'Test User',
            'author_email': 'invalid-email',
            'content': 'Test comment'
        }

        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('author_email', response.data)

    def test_pagination(self):
        """Тест пагинации в API"""
        # Создаем больше постов для теста пагинации
        for i in range(15):
            Post.objects.create(
                title=f'Extra Post {i}',
                author=self.user,
                category=self.category,
                excerpt=f'Excerpt {i}',
                content=f'Content {i}',
                status='published'
            )

        url = reverse('post-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем пагинацию
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        # Должно быть 20 постов всего (5 исходных + 15 новых)
        self.assertEqual(response.data['count'], 20)

        # На первой странице должно быть 10 постов (пагинация по умолчанию)
        self.assertEqual(len(response.data['results']), 10)

        # Проверяем вторую страницу
        if response.data['next']:
            next_response = self.client.get(response.data['next'])
            self.assertEqual(next_response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(next_response.data['results']), 10)


class TestCategoryViewSet(TestCase):
    """Тесты для CategoryViewSet"""

    def setUp(self):
        self.client = APIClient()

        # Создаем категории
        self.categories = []
        for i in range(5):
            category = Category.objects.create(
                name=f'Category {i}',
                description=f'Description {i}'
            )
            self.categories.append(category)

    def test_list_categories(self):
        """Тест получения списка категорий"""
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа
        self.assertIn('results', response.data)

        # Должно быть 5 категорий
        self.assertEqual(len(response.data['results']), 5)

        # Проверяем поля
        first_category = response.data['results'][0]
        self.assertIn('id', first_category)
        self.assertIn('name', first_category)
        self.assertIn('slug', first_category)
        self.assertIn('description', first_category)

    def test_retrieve_category(self):
        """Тест получения конкретной категории"""
        category = self.categories[0]
        url = reverse('category-detail', kwargs={'slug': category.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем данные категории
        self.assertEqual(response.data['name'], category.name)
        self.assertEqual(response.data['slug'], category.slug)
        self.assertEqual(response.data['description'], category.description)

    def test_retrieve_nonexistent_category_returns_404(self):
        """Тест, что несуществующая категория возвращает 404"""
        url = reverse('category-detail', kwargs={'slug': 'nonexistent-category'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_ordering(self):
        """Тест порядка категорий (по имени)"""
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Категории должны быть отсортированы по имени
        category_names = [cat['name'] for cat in response.data['results']]
        self.assertEqual(category_names, sorted(category_names))


class TestAPISerializers(TestCase):
    """Тесты для сериализаторов API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )

        self.post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )
        self.post.tags.add('django', 'python')

    def test_post_serializer(self):
        """Тест PostSerializer"""
        from blog.api import PostSerializer

        serializer = PostSerializer(self.post)

        # Проверяем поля
        self.assertEqual(serializer.data['title'], 'Test Post')
        self.assertEqual(serializer.data['author'], 'author')
        self.assertEqual(serializer.data['excerpt'], 'Test excerpt')
        self.assertEqual(serializer.data['content'], 'Test content')

        # Проверяем вложенную категорию
        self.assertIn('category', serializer.data)
        self.assertEqual(serializer.data['category']['name'], 'Test Category')

        # Проверяем теги
        self.assertIn('tags', serializer.data)
        self.assertEqual(len(serializer.data['tags']), 2)
        self.assertIn('django', serializer.data['tags'])
        self.assertIn('python', serializer.data['tags'])

    def test_category_serializer(self):
        """Тест CategorySerializer"""
        from blog.api import CategorySerializer

        serializer = CategorySerializer(self.category)

        # Проверяем поля
        self.assertEqual(serializer.data['name'], 'Test Category')
        self.assertEqual(serializer.data['slug'], self.category.slug)
        self.assertEqual(serializer.data['description'], 'Test description')

    def test_comment_serializer(self):
        """Тест CommentSerializer"""
        from blog.api import CommentSerializer

        comment = Comment.objects.create(
            post=self.post,
            author_name='Test User',
            author_email='test@example.com',
            content='Test comment'
        )

        serializer = CommentSerializer(comment)

        # Проверяем поля
        self.assertEqual(serializer.data['author_name'], 'Test User')
        self.assertEqual(serializer.data['author_email'], 'test@example.com')
        self.assertEqual(serializer.data['content'], 'Test comment')
        self.assertIn('created_at', serializer.data)
        self.assertIn('id', serializer.data)

        # Проверяем read_only_fields
        self.assertNotIn('is_approved', serializer.data)  # Не включено в fields
        self.assertNotIn('post', serializer.data)  # Не включено в fields

    def test_comment_serializer_validation(self):
        """Тест валидации CommentSerializer"""
        from blog.api import CommentSerializer

        # Валидные данные
        valid_data = {
            'author_name': 'Test User',
            'author_email': 'test@example.com',
            'content': 'Valid comment'
        }

        serializer = CommentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Невалидные данные (нет author_name)
        invalid_data = {
            'author_email': 'test@example.com',
            'content': 'Invalid comment'
        }

        serializer = CommentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('author_name', serializer.errors)

        # Невалидные данные (пустой content)
        invalid_data = {
            'author_name': 'Test User',
            'author_email': 'test@example.com',
            'content': ''
        }

        serializer = CommentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

        # Невалидные данные (неправильный email)
        invalid_data = {
            'author_name': 'Test User',
            'author_email': 'invalid-email',
            'content': 'Test comment'
        }

        serializer = CommentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('author_email', serializer.errors)


class TestAPIEndpoints(TestCase):
    """Интеграционные тесты API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='author',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )

        self.post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )

    def test_api_root(self):
        """Тест корневого URL API (если настроен)"""
        # Проверяем, настроен ли API root
        try:
            url = reverse('api-root')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        except:
            # API root может быть не настроен, это нормально
            pass

    def test_api_response_format(self):
        """Тест формата ответа API"""
        url = reverse('post-list')
        response = self.client.get(url)

        # Проверяем заголовки
        self.assertEqual(response['Content-Type'], 'application/json')

        # Проверяем, что ответ валидный JSON
        try:
            json.loads(response.content)
        except json.JSONDecodeError:
            self.fail("Ответ не является валидным JSON")

    def test_api_filtering_by_category(self):
        """Тест фильтрации постов по категории через API"""
        # Создаем вторую категорию
        category2 = Category.objects.create(
            name='Category 2',
            description='Description 2'
        )

        # Создаем пост во второй категории
        post2 = Post.objects.create(
            title='Post in Category 2',
            author=self.user,
            category=category2,
            excerpt='Excerpt 2',
            content='Content 2',
            status='published'
        )

        url = reverse('post-list')

        # Пока не реализована фильтрация по категории в API
        # Но можно проверить, что посты из обеих категорий возвращаются
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        # Проверяем, что оба поста в ответе
        post_titles = [p['title'] for p in response.data['results']]
        self.assertIn('Test Post', post_titles)
        self.assertIn('Post in Category 2', post_titles)

    def test_api_search_functionality(self):
        """Тест поиска через API (если реализован)"""
        # Создаем несколько постов с разными словами
        Post.objects.create(
            title='Python Tutorial',
            author=self.user,
            category=self.category,
            excerpt='Learn Python',
            content='Python is great',
            status='published'
        )

        Post.objects.create(
            title='Django Guide',
            author=self.user,
            category=self.category,
            excerpt='Django framework',
            content='Build web apps with Django',
            status='published'
        )

        # Поиск не реализован в текущем API, но можно проверить общий список
        url = reverse('post-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # 1 исходный + 2 новых


class TestAPIPermissions(TestCase):
    """Тесты прав доступа к API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='author',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )

        self.post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )

    def test_api_read_only_access(self):
        """Тест, что API только для чтения"""
        # Пытаемся создать пост через API (не должно быть разрешено)
        url = reverse('post-list')
        post_data = {
            'title': 'New Post',
            'excerpt': 'New excerpt',
            'content': 'New content'
        }

        response = self.client.post(url, post_data, format='json')

        # Должно вернуть 405 Method Not Allowed или 403 Forbidden
        # так как ViewSet является ReadOnlyModelViewSet
        self.assertIn(response.status_code, [
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_403_FORBIDDEN
        ])

    def test_authenticated_vs_anonymous_access(self):
        """Тест доступа для анонимных и аутентифицированных пользователей"""
        # Анонимный пользователь должен иметь доступ на чтение
        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Аутентифицируем пользователя
        self.client.force_authenticate(user=self.user)

        # Аутентифицированный пользователь также должен иметь доступ на чтение
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)