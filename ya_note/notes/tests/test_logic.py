from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    NOTE_SLUG = 'slug'
    NEW_NOTE_SLUG = 'new-slug'
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо Крокодил')
        cls.form_data = {
            'slug': cls.NOTE_SLUG,
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }
        cls.add_url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url = reverse('notes:detail', args=(cls.NOTE_SLUG,))

    def test_anonymous_user_cant_create_note(self):
        before_notes = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, before_notes)

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        before_notes = Note.objects.count()
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        expected_notes_count = before_notes + 1
        current_notes = Note.objects.count()
        self.assertEqual(current_notes, expected_notes_count)
        new_note = Note.objects.filter(slug=self.form_data['slug']).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_user_cant_use_same_slug(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
            slug=self.NOTE_SLUG,
        )
        before_notes = Note.objects.count()
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(note.slug + WARNING),
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, before_notes)

    def test_empty_slug(self):
        before_notes = Note.objects.count()
        self.form_data.pop('slug')
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        current_notes = Note.objects.count()
        self.assertEqual(before_notes + 1, current_notes)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):

    NEW_NOTE_TITILE = 'Новый заголовок'
    NOTE_TITILE = 'Заголовок'
    NEW_NOTE_TEXT = 'Новый текст'
    NOTE_TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.notes_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TITILE
        }

    def test_author_can_delete_note(self):
        before_notes = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, before_notes - 1)

    def test_user_cant_delete_note_of_another_user(self):
        before_notes = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, before_notes)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.title, self.NEW_NOTE_TITILE)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITILE)
