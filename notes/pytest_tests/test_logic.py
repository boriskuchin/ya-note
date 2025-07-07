from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify


def test_user_can_create_note(author_client, form_data, author):
    url = reverse('notes:add')
    success_url = reverse('notes:success')
    response = author_client.post(url, data=form_data)
    assertRedirects(response, success_url)
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == author
    assert Note.objects.filter(
        title=form_data['title'],
        text=form_data['text'],
        slug=form_data['slug'],
        author=author,
    ).exists()

@pytest.mark.django_db
def test_anonim_user_cant_create_note(client, form_data):
    url = reverse('notes:add')
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'
    response = client.post(url, data=form_data)
    assertRedirects(response, redirect_url)
    assert Note.objects.count() == 0

@pytest.mark.django_db
def test_not_unique_slug(author_client, note, form_data):
    url = reverse('notes:add')
    form_data['slug'] = note.slug
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))  
    assert Note.objects.count() == 1

def test_empty_slug(author_client, form_data):
    url = reverse('notes:add')
    form_data.pop('slug')
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    expected_slug = slugify(form_data['title'])
    assert new_note.slug == expected_slug

def test_author_can_edit_note(author_client, note, form_data):
    url = reverse('notes:edit', args=(note.slug,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']

def test_other_user_cant_edit_note(not_author_client, note, form_data):
    url = reverse('notes:edit', args=(note.slug,))
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Note.objects.get(id=note.id)
    assert note_from_db.title == note.title
    assert note_from_db.text == note.text
    assert note_from_db.slug == note.slug

def test_author_can_delete_note(author_client, slug_for_args):
    url = reverse('notes:delete', args=slug_for_args)
    response = author_client.post(url)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 0 


def test_other_user_cant_delete_note(not_author_client, slug_for_args):
    url = reverse('notes:delete', args=slug_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == 1  