import pytest

from django.test.client import Client

from notes.models import Note

@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')

@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='not_author')

@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client

@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client

@pytest.fixture
def note(author):
    return Note.objects.create( # type: ignore
        title='Test note', 
        text='Test text', 
        author=author,
        slug='test-slug',
    )

@pytest.fixture
def slug_for_args(note):
    return (note.slug,)

@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    } 