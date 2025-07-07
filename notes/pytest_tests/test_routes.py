from http import HTTPStatus
import pytest
from pytest_lazy_fixtures import lf
from notes.models import Note
from django.urls import reverse
from pytest_django.asserts import assertRedirects

@pytest.mark.parametrize(
    "name",
    [
        "notes:home",
        "users:login",
        "users:logout",
        "users:signup",
    ]
)
def test_page_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    "name",
    [
        "notes:list",
        "notes:add",
        "notes:success",
    ]
)
def test_page_availability_for_auth_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK

def test_note_exest(note):
    note_count = Note.objects.count() # type: ignore
    assert note_count == 1
    assert note.title == 'Test note'

@pytest.mark.django_db
def test_empty_db():
    assert Note.objects.count() == 0 # type: ignore

@pytest.mark.parametrize(
 'parametrized_client, expected_status',
 [
    (lf('author_client'), HTTPStatus.OK),
    (lf('not_author_client'), HTTPStatus.NOT_FOUND),
 ]
)
@pytest.mark.parametrize(
    "name",
    [
        "notes:detail",
        "notes:edit",
        "notes:delete",
    ]
)   
def test_availability_for_author(parametrized_client, note, name, expected_status):
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    'name, args',
    [
        ("notes:detail", lf('slug_for_args')),
        ("notes:edit", lf('slug_for_args')),
        ("notes:delete", lf('slug_for_args')),
        ("notes:list", None),
        ("notes:add", None),
        ("notes:success", None),
    ]
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)