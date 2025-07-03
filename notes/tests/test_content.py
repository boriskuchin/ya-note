from django.contrib.auth import get_user_model
from django.test import TestCase
from notes.models import Note
from django.test import Client
from django.urls import reverse
from http import HTTPStatus
from notes.forms import NoteForm

User = get_user_model()

class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_client = Client(user=cls.author)
        cls.auth_client.force_login(cls.author)

        cls.user = User.objects.create(username='user')
        cls.user_client = Client(user=cls.user)
        cls.user_client.force_login(cls.user)

        cls.note_list = [
            Note(
                title=f'Note {index}',
                text=f'text {index}',
                slug=f'note-{index}-slug',
                author=cls.author
            )
            for index in range(15)
        ]
        Note.objects.bulk_create(cls.note_list) # type: ignore
        

    def test_author_can_see_notes(self):
        url = reverse('notes:list')
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore
        object_list = response.context['object_list'] # type: ignore
        self.assertEqual(len(object_list), 15)

    def test_user_cant_see_notes(self):
        url = reverse('notes:list')
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore    
        object_list = response.context['object_list'] # type: ignore
        self.assertEqual(len(object_list), 0)

class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_client = Client(user=cls.author)
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create( # type: ignore
            title='Note',
            text='text',
            author=cls.author)

    def test_anonymous_client_redirected(self):
        url = reverse('notes:detail', kwargs={'slug': self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND) # type: ignore
        
    def test_authorized_client_can_see_note(self):
        url = reverse('notes:detail', kwargs={'slug': self.note.slug})
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore
        self.assertIn('note', response.context) # type: ignore
        self.assertEqual(response.context['note'], self.note) # type: ignore

class TestNoteForms(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_client = Client(user=cls.author)
        cls.auth_client.force_login(cls.author)
        
        
        cls.note = Note.objects.create( # type: ignore
            title='Note',
            text='text',
            slug='test-note',
            author=cls.author)

    def test_anonymous_user_cant_access_create_form(self):
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND) # type: ignore

    def test_authorized_user_can_access_create_form(self):
        url = reverse('notes:add')
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore
        self.assertIn('form', response.context) # type: ignore
        self.assertIsInstance(response.context['form'], NoteForm) # type: ignore

    def test_anonymous_user_cant_access_edit_form(self):
        url = reverse('notes:edit', kwargs={'slug': self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND) # type: ignore

    def test_authorized_user_can_access_edit_form(self):
        url = reverse('notes:edit', kwargs={'slug': self.note.slug})
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore
        self.assertIn('form', response.context) # type: ignore
        self.assertIsInstance(response.context['form'], NoteForm) # type: ignore

    def test_anonymous_user_cant_access_delete_form(self):
        url = reverse('notes:delete', kwargs={'slug': self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND) # type: ignore

    def test_authorized_user_can_access_delete_form(self):
        url = reverse('notes:delete', kwargs={'slug': self.note.slug})
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore
        self.assertIn('note', response.context) # type: ignore
        self.assertEqual(response.context['note'], self.note) # type: ignore
