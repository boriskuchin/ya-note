from django.urls import reverse
import pytest
from pytest_lazy_fixtures import lf 
from notes.forms import NoteForm

@pytest.mark.parametrize(
    'parametrized_client, note_should_be_in_list',
    (
        (lf('author_client'), True),
        (lf('not_author_client'), False),
    )
)
def test_note_in_list_for_different_users(
    note, 
    parametrized_client, 
    note_should_be_in_list,
): 
    url = reverse("notes:list")
    response = parametrized_client.get(url)
    object_list = response.context["object_list"]
    assert (note in object_list) == note_should_be_in_list


@pytest.mark.parametrize(
    'name, args',
    [
        ('notes:edit', lf('slug_for_args')),
        ('notes:add', None),
    ]
)
def test_edit_and_add_note_page_contains_form(author_client, name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context["form"], NoteForm)