"""
Тесты edge cases для моделей блога
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from blog.models import Category, Post, Comment


class TestCategoryEdgeCases(TestCase):
    """Тесты edge cases для модели Category"""

    def test_category_slug_auto_generation(self):
        """Тест автоматической генерации slug для категории"""
        # Создаем категорию без slug
        category = Category.objects.create(
            name='Test Category Name',
            description='Test description'
        )

        # Slug должен быть автоматически сгенерирован
        self.assertTrue(category.slug)
        self.assertEqual(category.slug, 'test-category-name')

        # Проверяем, что slug уникален
        category2 = Category.objects.create(
            name='Another Category',
            description='Another description'
        )

        self.assertNotEqual(category.slug, category2.slug)

    def test_category_slug_preserved_if_provided(self):
        """Тест, что предоставленный slug сохраняется"""
        category = Category.objects.create(
            name='Test Category',
            slug='custom-slug',
            description='Test description'
        )

        self.assertEqual(category.slug, 'custom-slug')

    def test_category_name_max_length(self):
        """Тест максимальной длины имени категории"""
        # Используем длину из модели, а не фиксированную
        max_length = Category._meta.get_field('name').max_length
        max_length_name = 'A' * max_length

        category = Category.objects.create(
            name=max_length_name,
            description='Test description'
        )

        self.assertEqual(len(category.name), max_length)

    def test_post_title_max_length(self):
        """Тест максимальной длины заголовка"""
        max_length = Post._meta.get_field('title').max_length
        max_title = 'A' * max_length

        post = Post.objects.create(
            title=max_title,
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )

        self.assertEqual(len(post.title), max_length)

    def test_post_slug_unique_constraint(self):
        """Тест уникальности slug поста"""
        # Создаем первый пост
        post1 = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            slug='test-post',
            status='draft'
        )

        # Попытка создать второй пост с таким же slug должна вызвать ошибку
        with self.assertRaises(Exception):
            post2 = Post.objects.create(
                title='Test Post 2',
                author=self.user,
                category=self.category,
                excerpt='Another excerpt',
                content='Another content',
                slug='test-post',  # Тот же slug
                status='draft'
            )

    def test_category_name_unicode(self):
        """Тест категории с unicode символами"""
        category = Category.objects.create(
            name='Категория с русским названием',
            description='Описание на русском'
        )

        # Slug должен корректно сгенерироваться для кириллицы
        self.assertTrue(category.slug)
        # python-slugify транслитерирует кириллицу
        self.assertEqual(category.slug, 'kategoriya-s-russkim-nazvaniem')

    def test_category_with_special_characters(self):
        """Тест категории со специальными символами"""
        category = Category.objects.create(
            name='Category & Special! Characters@',
            description='Test with special chars'
        )

        # Специальные символы должны быть удалены из slug
        self.assertEqual(category.slug, 'category-special-characters')

    def test_category_ordering(self):
        """Тест порядка категорий (по алфавиту)"""
        categories_data = [
            ('Zebra', 'Z category'),
            ('Apple', 'A category'),
            ('Banana', 'B category'),
        ]

        for name, desc in categories_data:
            Category.objects.create(name=name, description=desc)

        # Получаем категории в порядке по умолчанию (по имени)
        categories = Category.objects.all()

        # Должны быть отсортированы по алфавиту
        self.assertEqual(categories[0].name, 'Apple')
        self.assertEqual(categories[1].name, 'Banana')
        self.assertEqual(categories[2].name, 'Zebra')

    def test_category_str_method(self):
        """Тест строкового представления категории"""
        category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )

        self.assertEqual(str(category), 'Test Category')

    def test_category_verbose_names(self):
        """Тест verbose_name модели Category"""
        self.assertEqual(Category._meta.verbose_name, 'Категория')
        self.assertEqual(Category._meta.verbose_name_plural, 'Категории')

        # Проверяем verbose_name полей
        name_field = Category._meta.get_field('name')
        self.assertEqual(name_field.verbose_name, 'Название')

        description_field = Category._meta.get_field('description')
        self.assertEqual(description_field.verbose_name, 'Описание')


class TestPostEdgeCases(TestCase):
    """Тесты edge cases для модели Post"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )

    def test_post_slug_auto_generation(self):
        """Тест автоматической генерации slug для поста"""
        # Создаем пост без slug
        post = Post.objects.create(
            title='Test Post Title',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='draft'
        )

        # Slug должен быть автоматически сгенерирован
        self.assertTrue(post.slug)
        self.assertEqual(post.slug, 'test-post-title')

    def test_post_slug_unique_constraint(self):
        """Тест уникальности slug поста"""
        # Создаем первый пост
        post1 = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            slug='test-post',  # Явно задаем slug
            status='draft'
        )

        # Попытка создать второй пост с таким же slug должна вызвать ошибку
        # или автоматически сгенерировать уникальный slug
        with self.assertRaises(Exception):  # Ожидаем ошибку
            post2 = Post.objects.create(
                title='Test Post',
                slug='test-post',  # Явно указываем тот же slug
                author=self.user,
                category=self.category,
                excerpt='Another excerpt',
                content='Another content',
                status='draft'
            )

        # В зависимости от реализации, slug должен быть уникальным
        self.assertNotEqual(post1.slug, post2.slug)

    def test_post_published_at_auto_set(self):
        """Тест автоматической установки published_at при публикации"""
        # Создаем черновик
        draft_post = Post.objects.create(
            title='Draft Post',
            author=self.user,
            category=self.category,
            excerpt='Draft excerpt',
            content='Draft content',
            status='draft'
        )

        # У черновика не должно быть published_at
        self.assertIsNone(draft_post.published_at)

        # Публикуем пост
        draft_post.status = 'published'
        draft_post.save()

        # Теперь должен быть published_at
        self.assertIsNotNone(draft_post.published_at)

        # Проверяем, что published_at примерно сейчас
        time_diff = timezone.now() - draft_post.published_at
        self.assertLess(time_diff.total_seconds(), 5)  # Разница меньше 5 секунд

    def test_post_published_at_preserved_if_exists(self):
        """Тест, что существующий published_at не перезаписывается"""
        # Устанавливаем конкретную дату в прошлом
        past_date = timezone.now() - timedelta(days=7)

        post = Post.objects.create(
            title='Post with Past Date',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published',
            published_at=past_date
        )

        # Меняем статус (но published_at уже установлен)
        post.status = 'draft'
        post.save()
        post.status = 'published'
        post.save()

        # published_at не должен измениться
        self.assertEqual(post.published_at, past_date)

    def test_post_views_increment(self):
        """Тест увеличения счетчика просмотров"""
        post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published',
            views=10
        )

        # Увеличиваем views
        post.views += 1
        post.save()

        post.refresh_from_db()
        self.assertEqual(post.views, 11)

    def test_post_with_empty_excerpt(self):
        """Тест поста с пустым excerpt"""
        post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='',  # Пустой excerpt
            content='Test content',
            status='published'
        )

        self.assertEqual(post.excerpt, '')

    def test_post_excerpt_max_length(self):
        """Тест максимальной длины excerpt"""
        # Создаем excerpt максимальной длины
        max_excerpt = 'A' * 500

        post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt=max_excerpt,
            content='Test content',
            status='published'
        )

        self.assertEqual(len(post.excerpt), 500)

    def test_post_title_max_length(self):
        """Тест максимальной длины заголовка"""
        max_title = 'A' * 250

        post = Post.objects.create(
            title=max_title,
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )

        self.assertEqual(len(post.title), 250)

    def test_post_with_tags(self):
        """Тест поста с тегами"""
        post = Post.objects.create(
            title='Test Post with Tags',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )

        # Добавляем теги
        post.tags.add('django', 'python', 'web-development')

        # Проверяем количество тегов
        self.assertEqual(post.tags.count(), 3)

        # Проверяем, что теги сохранены
        tag_names = [tag.name for tag in post.tags.all()]
        self.assertIn('django', tag_names)
        self.assertIn('python', tag_names)
        self.assertIn('web-development', tag_names)

    def test_post_ordering(self):
        """Тест порядка постов (по дате публикации, новые первыми)"""
        # Создаем посты с разными датами публикации
        posts_data = [
            ('Old Post', timezone.now() - timedelta(days=2)),
            ('New Post', timezone.now()),
            ('Middle Post', timezone.now() - timedelta(days=1)),
        ]

        for title, pub_date in posts_data:
            Post.objects.create(
                title=title,
                author=self.user,
                category=self.category,
                excerpt='Test excerpt',
                content='Test content',
                status='published',
                published_at=pub_date
            )

        # Получаем посты в порядке по умолчанию
        posts = Post.objects.filter(status='published')

        # Должны быть отсортированы по published_at (новые первыми)
        self.assertEqual(posts[0].title, 'New Post')
        self.assertEqual(posts[1].title, 'Middle Post')
        self.assertEqual(posts[2].title, 'Old Post')

    def test_post_get_absolute_url(self):
        """Тест метода get_absolute_url"""
        post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )

        url = post.get_absolute_url()

        # URL должен содержать slug поста
        self.assertIn(post.slug, url)
        # И должен соответствовать паттерну URL
        self.assertTrue(url.startswith('/') or '://' in url)

    def test_post_str_method(self):
        """Тест строкового представления поста"""
        post = Post.objects.create(
            title='Test Post Title',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='published'
        )

        self.assertEqual(str(post), 'Test Post Title')

    def test_post_verbose_names(self):
        """Тест verbose_name модели Post"""
        self.assertEqual(Post._meta.verbose_name, 'Статья')
        self.assertEqual(Post._meta.verbose_name_plural, 'Статьи')

        # Проверяем verbose_name некоторых полей
        title_field = Post._meta.get_field('title')
        self.assertEqual(title_field.verbose_name, 'Заголовок')

        status_field = Post._meta.get_field('status')
        self.assertEqual(status_field.verbose_name, 'Статус')

        views_field = Post._meta.get_field('views')
        self.assertEqual(views_field.verbose_name, 'Просмотры')

    def test_post_status_choices(self):
        """Тест вариантов статуса поста"""
        post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            status='draft'
        )

        # Проверяем доступные choices
        status_choices = dict(Post.STATUS_CHOICES)
        self.assertIn('draft', status_choices)
        self.assertIn('published', status_choices)
        self.assertEqual(status_choices['draft'], 'Черновик')
        self.assertEqual(status_choices['published'], 'Опубликовано')

        # Проверяем get_status_display
        self.assertEqual(post.get_status_display(), 'Черновик')

        # Меняем статус и проверяем снова
        post.status = 'published'
        post.save()
        self.assertEqual(post.get_status_display(), 'Опубликовано')

    def test_post_with_featured_image(self):
        """Тест поста с изображением"""
        # Для теста изображения используем SimpleUploadedFile
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Создаем тестовое изображение
        image_content = b'fake image content'
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_content,
            content_type='image/jpeg'
        )

        post = Post.objects.create(
            title='Post with Image',
            author=self.user,
            category=self.category,
            excerpt='Test excerpt',
            content='Test content',
            featured_image=image,
            status='published'
        )

        # Проверяем, что изображение сохранено
        self.assertTrue(post.featured_image)
        self.assertIn('posts/', post.featured_image.name)
        self.assertTrue(post.featured_image.name.endswith('.jpg'))


class TestCommentEdgeCases(TestCase):
    """Тесты edge cases для модели Comment"""

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

    def test_comment_creation(self):
        """Тест создания комментария"""
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test User',
            author_email='test@example.com',
            content='Test comment content',
            is_approved=True
        )

        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author_name, 'Test User')
        self.assertEqual(comment.author_email, 'test@example.com')
        self.assertEqual(comment.content, 'Test comment content')
        self.assertTrue(comment.is_approved)
        self.assertIsNotNone(comment.created_at)

    def test_comment_str_method(self):
        """Тест строкового представления комментария"""
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test User',
            author_email='test@example.com',
            content='This is a very long comment that should be truncated in the string representation',
            is_approved=True
        )

        str_repr = str(comment)

        # Должно содержать имя автора
        self.assertIn('Test User', str_repr)

        # Должно содержать первые 50 символов комментария
        self.assertIn('This is a very long comment that should be', str_repr)

        # Должно быть обрезано до 50 символов + "..."
        self.assertTrue(len(str_repr) <= len('Test User: ') + 50 + 3)  # 3 для ": " и возможного "..."

    def test_comment_ordering(self):
        """Тест порядка комментариев (новые первыми)"""
        # Создаем комментарии с разным временем создания
        comments_data = [
            ('First', 'first@example.com', 'Old comment'),
            ('Second', 'second@example.com', 'New comment'),
            ('Third', 'third@example.com', 'Middle comment'),
        ]

        for name, email, content in comments_data:
            Comment.objects.create(
                post=self.post,
                author_name=name,
                author_email=email,
                content=content,
                is_approved=True
            )

        # Получаем комментарии
        comments = Comment.objects.all()

        # Должны быть отсортированы по created_at (новые первыми)
        # Последний созданный = первый в списке
        self.assertEqual(comments[0].author_name, 'Third')
        self.assertEqual(comments[1].author_name, 'Second')
        self.assertEqual(comments[2].author_name, 'First')

    def test_comment_author_name_max_length(self):
        """Тест максимальной длины имени автора"""
        max_name = 'A' * 100

        comment = Comment.objects.create(
            post=self.post,
            author_name=max_name,
            author_email='test@example.com',
            content='Test comment',
            is_approved=True
        )

        self.assertEqual(len(comment.author_name), 100)

    def test_comment_with_empty_content(self):
        """Тест комментария с пустым содержимым"""
        # Пустое содержание должно быть разрешено (если не указано иное)
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test User',
            author_email='test@example.com',
            content='',  # Пустое содержание
            is_approved=True
        )

        self.assertEqual(comment.content, '')

    def test_comment_verbose_names(self):
        """Тест verbose_name модели Comment"""
        self.assertEqual(Comment._meta.verbose_name, 'Комментарий')
        self.assertEqual(Comment._meta.verbose_name_plural, 'Комментарии')

        # Проверяем verbose_name полей
        author_name_field = Comment._meta.get_field('author_name')
        self.assertEqual(author_name_field.verbose_name, 'Имя')

        content_field = Comment._meta.get_field('content')
        self.assertEqual(content_field.verbose_name, 'Комментарий')

        is_approved_field = Comment._meta.get_field('is_approved')
        self.assertEqual(is_approved_field.verbose_name, 'Одобрен')

    def test_comment_approved_vs_pending(self):
        """Тест фильтрации одобренных и неодобренных комментариев"""
        # Создаем одобренные и неодобренные комментарии
        approved_comments = []
        pending_comments = []

        for i in range(3):
            approved = Comment.objects.create(
                post=self.post,
                author_name=f'Approved {i}',
                author_email=f'approved{i}@example.com',
                content=f'Approved comment {i}',
                is_approved=True
            )
            approved_comments.append(approved)

            pending = Comment.objects.create(
                post=self.post,
                author_name=f'Pending {i}',
                author_email=f'pending{i}@example.com',
                content=f'Pending comment {i}',
                is_approved=False
            )
            pending_comments.append(pending)

        # Проверяем фильтрацию
        all_comments = Comment.objects.all()
        self.assertEqual(all_comments.count(), 6)

        approved_only = Comment.objects.filter(is_approved=True)
        self.assertEqual(approved_only.count(), 3)

        pending_only = Comment.objects.filter(is_approved=False)
        self.assertEqual(pending_only.count(), 3)

    def test_comment_cascade_delete(self):
        """Тест каскадного удаления поста с комментариями"""
        # Создаем комментарии к посту
        for i in range(5):
            Comment.objects.create(
                post=self.post,
                author_name=f'User {i}',
                author_email=f'user{i}@example.com',
                content=f'Comment {i}',
                is_approved=True
            )

        # Проверяем, что комментарии созданы
        self.assertEqual(Comment.objects.count(), 5)
        self.assertEqual(self.post.comments.count(), 5)

        # Удаляем пост
        self.post.delete()

        # Комментарии должны быть удалены каскадно
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_unicode_email(self):
        """Тест комментария с unicode email (интернациональным)"""
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test User',
            author_email='test@例子.测试',  # Internationalized domain name
            content='Test comment',
            is_approved=True
        )

        # Django должен нормально обрабатывать unicode в email
        self.assertEqual(comment.author_email, 'test@例子.测试')


class TestModelRelationships(TestCase):
    """Тесты связей между моделями"""

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

    def test_post_author_relationship(self):
        """Тест связи поста с автором"""
        self.assertEqual(self.post.author, self.user)

        # Проверяем обратную связь (если настроена related_name)
        # По умолчанию Django создает обратную связь user.post_set
        user_posts = self.user.post_set.all()
        self.assertIn(self.post, user_posts)

    def test_post_category_relationship(self):
        """Тест связи поста с категорией"""
        self.assertEqual(self.post.category, self.category)

        # Проверяем обратную связь
        category_posts = self.category.post_set.all()
        self.assertIn(self.post, category_posts)

        # Проверяем SET_NULL при удалении категории
        self.category.delete()

        # Обновляем пост из базы
        self.post.refresh_from_db()

        # Категория должна быть NULL
        self.assertIsNone(self.post.category)

    def test_comment_post_relationship(self):
        """Тест связи комментария с постом"""
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test User',
            author_email='test@example.com',
            content='Test comment',
            is_approved=True
        )

        self.assertEqual(comment.post, self.post)

        # Проверяем обратную связь через related_name='comments'
        post_comments = self.post.comments.all()
        self.assertIn(comment, post_comments)

    def test_cascade_delete_post_with_comments(self):
        """Тест каскадного удаления поста с комментариями"""
        # Создаем несколько комментариев
        for i in range(3):
            Comment.objects.create(
                post=self.post,
                author_name=f'User {i}',
                author_email=f'user{i}@example.com',
                content=f'Comment {i}',
                is_approved=True
            )

        # Удаляем пост
        post_id = self.post.id
        self.post.delete()

        # Проверяем, что пост удален
        self.assertFalse(Post.objects.filter(id=post_id).exists())

        # Комментарии должны быть удалены каскадно
        self.assertEqual(Comment.objects.filter(post_id=post_id).count(), 0)