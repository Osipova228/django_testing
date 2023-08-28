import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


def test_user_can_create_comment(author_client, author, news, form_data):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data=form_data)
    expected_redirect_url = reverse('news:detail', kwargs={'pk': news.pk})
    expected_redirect_url_with_anchor = expected_redirect_url + '#comments'
    assertRedirects(response, expected_redirect_url_with_anchor)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    expected_redirect_url = reverse('news:detail', kwargs={'pk': news.pk})
    expected_redirect_url_with_anchor = expected_redirect_url + '#comments'
    assertRedirects(response, expected_redirect_url_with_anchor)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(admin_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, comment, news):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    expected_redirect_url = reverse('news:detail', kwargs={'pk': news.pk})
    expected_redirect_url_with_anchor = expected_redirect_url + '#comments'
    assertRedirects(response, expected_redirect_url_with_anchor)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_bad_words_in_comment(author_client, news, form_data):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data['text'] = BAD_WORDS[0]
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0
