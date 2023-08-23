from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.note = Note.objects.create(
            title='Заметка 1',
            text='Просто текст.',
        )
        cls.url = reverse('note:detail', args=(cls.note.slug,))

    def test_news_count(self):
        response = self.client.get(self.url)
        object_list = response.context['object_list']
        news_count = len(object_list)
        self.assertEqual(news_count, 1)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.note = Note.objects.create(
            title='Тестовая заметка', text='Просто текст.'
        )
        cls.add_url = reverse('notes:add')
        cls.author = User.objects.create(username='Автор')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_anonymous_client_has_no_edit_form(self):
        response = self.client.get(self.edit_url)
        self.assertNotIn('form', response.context)

    def test_anonymous_client_has_no_add_form(self):
        response = self.client.get(self.add_url)
        self.assertNotIn('form', response.context)

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
        cls.note = Note.objects.create(
            title='Заметка 1',
            text='Просто текст.',
        )
        cls.url = reverse('note:list', args=(cls.note.slug,))
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:list'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
