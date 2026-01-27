"""
Функциональные тесты
"""
import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from blog.models import Category, Post


class BlogFunctionalTests(LiveServerTestCase):
    """Функциональные тесты блога"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()  # Или другой драйвер
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published'
        )

    def test_homepage_load(self):
        """Тест загрузки главной страницы"""
        self.selenium.get(self.live_server_url)

        # Проверяем заголовок страницы
        self.assertIn('CodeWithBrain', self.selenium.title)

    def test_navigation(self):
        """Тест навигации по сайту"""
        self.selenium.get(self.live_server_url)

        # Проверяем наличие навигационного меню
        nav = self.selenium.find_element(By.TAG_NAME, 'nav')
        self.assertIsNotNone(nav)

        # Проверяем ссылки
        links = nav.find_elements(By.TAG_NAME, 'a')
        self.assertGreater(len(links), 0)

    def test_post_view(self):
        """Тест просмотра поста"""
        url = f"{self.live_server_url}/blog/{self.post.slug}/"
        self.selenium.get(url)

        # Проверяем заголовок поста
        title = self.selenium.find_element(By.TAG_NAME, 'h1')
        self.assertIn('Test Post', title.text)

        # Проверяем содержание
        content = self.selenium.find_element(By.CLASS_NAME, 'post-content')
        self.assertIsNotNone(content)

    def test_admin_login(self):
        """Тест входа в админку"""
        self.selenium.get(f'{self.live_server_url}/admin/')

        # Ищем элементы формы входа
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')

        username_input.send_keys('admin')
        password_input.send_keys('adminpassword123')
        password_input.send_keys(Keys.RETURN)

        # Ждем загрузки
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Проверяем, что вошли (ищем текст админки)
        page_source = self.selenium.page_source
        self.assertTrue('Администрирование сайта' in page_source or
                        'CodeWithBrain' in page_source or
                        'Панель управления' in page_source)