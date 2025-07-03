from django.contrib.auth import get_user_model
from django.test import TestCase
from notes.models import Note
from django.urls import reverse
from django.test import Client

from http import HTTPStatus


User = get_user_model()

class TestNoteCreation(TestCase):

    NOTE_TEXT = 'Note text'
    NOTE_TITLE = 'Test Note Title'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }


    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        count = Note.objects.count() # type: ignore
        self.assertEqual(count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        count = Note.objects.count() # type: ignore
        self.assertEqual(count, 1)
        note = Note.objects.get() # type: ignore
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Note text'
    UPDATED_NOTE_TEXT = 'Updated note text'
    NOTE_TITLE = 'Test Note Title'
    UPDATED_NOTE_TITLE = 'Updated Test Note Title'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='user')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.note = Note.objects.create( # type: ignore
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug='note-slug',
            author=cls.author
        )
        cls.url_to_edit = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.url_to_delete = reverse('notes:delete', kwargs={'slug': cls.note.slug})
        cls.form_data = {
            'title': cls.UPDATED_NOTE_TITLE,
            'text': cls.UPDATED_NOTE_TEXT,
        }



    def test_author_can_delete_comment(self):
        response = self.author_client.post(self.url_to_delete)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND) # type: ignore
        notes_count = Note.objects.count() # type: ignore
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.user_client.post(self.url_to_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND) # type: ignore
        notes_count = Note.objects.count() # type: ignore
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_to_edit, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.UPDATED_NOTE_TITLE)
        self.assertEqual(self.note.text, self.UPDATED_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.user_client.post(self.url_to_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND) # type: ignore
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)

