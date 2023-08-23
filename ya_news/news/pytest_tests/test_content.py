import pytest
from django.core.paginator import Paginator
from django.urls import reverse


@pytest.mark.django_db
def test_pagination(news_pagination):
    items_per_page = 10
    page_number = 2
    paginator = Paginator(news_pagination, items_per_page)
    page = paginator.get_page(page_number)

    assert page.has_previous()
    assert page.has_next()
    assert len(page) == items_per_page


@pytest.mark.django_db
def test_news_ordering(date_news):
    news_list = date_news
    news_dates = [news.date for news in news_list]
    assert news_dates == sorted(news_dates, reverse=True)


@pytest.mark.django_db
def test_comment_ordering(created_comment):
    comments = created_comment
    comment_dates = [comment.created for comment in comments]
    assert comment_dates == sorted(comment_dates, reverse=False)


@pytest.mark.django_db
def test_form_available_for_auth_users(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_form_for_notauth_users(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context
