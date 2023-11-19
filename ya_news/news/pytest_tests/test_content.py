import pytest

from http import HTTPStatus

from django.conf import settings


@pytest.mark.usefixtures('all_news')
def test_news_count(client, home_url):
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('all_news')
def test_news_order(client, home_url):
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    news_list = list(response.context['object_list'])
    sorted_news_list = sorted(news_list,
                              key=lambda news: news.date,
                              reverse=True)
    assert news_list == sorted_news_list


@pytest.mark.usefixtures('comments')
def test_comments_order(client, detail_url):
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK
    assert 'news' in response.context
    news = response.context['news']
    all_comments = list(news.comment_set.all())
    sorted_comments = sorted(all_comments, key=lambda comment: comment.created)
    assert all_comments == sorted_comments


@pytest.mark.parametrize(
    'parametrized_client, has_form',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_client_has_form(parametrized_client, has_form, detail_url):
    response = parametrized_client.get(detail_url)
    assert response.status_code == HTTPStatus.OK
    assert ('form' in response.context) == has_form
