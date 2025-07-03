from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')

        cls.note = Note.objects.create( # type: ignore
            title='Test note',
            text='Test text',
            author=cls.author,
        )
    
    def test_page_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
            ('notes:list', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                if name in ['notes:add', 'notes:list']:
                    self.assertEqual(response.status_code, HTTPStatus.FOUND) # type: ignore
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (
                'notes:edit',
                'notes:detail',
                'notes:delete',
            ):
                with self.subTest(user=user, name=name):
                    if name in ['notes:edit', 'notes:detail', 'notes:delete']:
                        url = reverse(name, kwargs={'slug': self.note.slug})
                    else:
                        url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status) # type: ignore

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': self.note.slug})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

