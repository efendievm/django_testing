import pytest

from http import HTTPStatus
from random import choice

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={detail_url}'
    response = client.post(detail_url, data=form_data)
    assertRedirects(response, redirect_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author, author_client, news, detail_url,
                                 form_data):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(admin_client, detail_url, form_data):
    form_data['text'] = f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    response = admin_client.post(detail_url, data=form_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['text'][0] == WARNING
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND)
    ),
)
def test_user_cant_delete_comment_of_another_user(
    parametrized_client, expected_status, delete_url
):
    response = parametrized_client.delete(delete_url)
    assert response.status_code == expected_status
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, edit_url, url_to_comments, form_data, comment
):
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND)
    ),
)
def test_user_cant_edit_comment_of_another_user(
    parametrized_client, expected_status, edit_url, form_data, comment
):
    initial_comment_text = comment.text
    response = parametrized_client.post(edit_url, data=form_data)
    assert response.status_code == expected_status
    comment.refresh_from_db()
    assert comment.text == initial_comment_text
