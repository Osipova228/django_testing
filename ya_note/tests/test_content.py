from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заметка 1',
            text='Просто текст.',
            author=cls.author,
        )
        cls.url = reverse('notes:list')

    def test_news_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        object_list = response.context.get('object_list')
        self.assertIsNotNone(object_list)

        news_count = len(object_list)
        self.assertEqual(news_count, 1)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.add_url = reverse('notes:add')
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_authorized_client_has_edit__form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)

    def test_authorized_client_has_add__form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заметка 1',
            text='Просто текст.',
            author=cls.author,
        )
        cls.url = reverse('notes:list')

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            name = 'notes:list'
            url = reverse(name)
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual((self.note in object_list), status)
