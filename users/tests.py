from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import User
import json


class UserViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # создаем тестовых пользователей
        User.objects.create(
            gender='male',
            first_name='John',
            last_name='Doe',
            phone='1234567890',
            email='john@example.com',
            street='123 Main St',
            city='Anytown',
            state='CA',
            postcode='12345',
            picture_thumbnail='http://example.com/thumb.jpg',
            picture_large='http://example.com/large.jpg'
        )
        User.objects.create(
            gender='female',
            first_name='Jane',
            last_name='Smith',
            phone='0987654321',
            email='jane@example.com',
            street='456 Oak Ave',
            city='Othertown',
            state='NY',
            postcode='54321',
            picture_thumbnail='http://example.com/thumb2.jpg',
            picture_large='http://example.com/large2.jpg'
        )

    def test_user_list_view_initial_form(self):
        """видна начальная форма"""
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/index.html')
        self.assertTrue(response.context['show_form'])
        self.assertContains(response, 'Введите кол-во пользователей')

    def test_user_list_view_with_count(self):
        """Тест отображения списка пользователей с указанием количества"""
        response = self.client.get(reverse('user_list') + '?count=1')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['show_form'])
        self.assertEqual(response.context['requested_count'], 1)
        self.assertContains(response, 'Показано 1 пользователей')

    def test_user_list_pagination(self):
        """Тест пагинации"""
        # Создаем больше пользователей для теста пагинации
        for i in range(30):
            User.objects.create(
                gender='male',
                first_name=f'User{i}',
                last_name=f'Test{i}',
                phone=f'12345678{i}',
                email=f'user{i}@test.com',
                street='123 St',
                city='City',
                state='ST',
                postcode='12345',
                picture_thumbnail=f'http://example.com/thumb{i}.jpg',
                picture_large=f'http://example.com/large{i}.jpg'
            )

        response = self.client.get(reverse('user_list') + '?count=30&page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 15)  # 15 на второй странице
        self.assertContains(response, 'Страниц 2 из 2')

    def test_user_detail_view(self):
        """Тест детального просмотра пользователя"""
        user = User.objects.first()
        response = self.client.get(reverse('user_detail', args=[user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_detail.html')
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)

    def test_random_user_view(self):
        """Тест страницы случайного пользователя"""
        response = self.client.get(reverse('random_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_detail.html')

    @patch('requests.get')
    def test_load_initial_users(self, mock_get):
        """Тест загрузки начальных пользователей с мокированием API"""
        # Настраиваем mock
        mock_response = {
            'results': [{
                'gender': 'female',
                'name': {'first': 'Anna', 'last': 'Karenina'},
                'phone': '5551234567',
                'email': 'anna@example.com',
                'location': {
                    'street': {'number': 123, 'name': 'Tolstoy St'},
                    'city': 'Moscow',
                    'state': 'Moscow Oblast',
                    'postcode': '101000'
                },
                'picture': {
                    'thumbnail': 'http://example.com/anna_thumb.jpg',
                    'large': 'http://example.com/anna_large.jpg'
                }
            }]
        }
        mock_get.return_value.json.return_value = mock_response

        # Очищаем базу
        User.objects.all().delete()

        # Импортируем и вызываем функцию
        from .views import load_initial_users
        load_initial_users()

        # Проверяем результаты
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.first_name, 'Anna')
        self.assertEqual(user.last_name, 'Karenina')
        self.assertEqual(user.city, 'Moscow')

    def test_post_user_count(self):
        """Тест POST-запроса для установки количества пользователей"""
        response = self.client.post(reverse('user_list'), {'count': 5})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/?count=5'))

    def test_user_count_limits(self):
        """Тест ограничений на количество пользователей"""
        # Максимальное количество не должно превышать 1000
        response = self.client.get(reverse('user_list') + '?count=1500')
        self.assertEqual(response.context['requested_count'], 1000)

        # Минимальное количество не должно быть меньше 1
        response = self.client.get(reverse('user_list') + '?count=0')
        self.assertEqual(response.context['requested_count'], 1)  # default