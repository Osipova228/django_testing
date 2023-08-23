from datetime import timedelta
import datetime
import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        id=1,
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news, author=author, text='Текст комментария',
    )
    return comment


@pytest.fixture
def comment_with_bad_word(author, news):
    comment = Comment.objects.create(
        news=news, author=author, text='Ты редиска!'
    )
    return comment


@pytest.fixture
def created_comment(author, news):
    now = datetime.datetime.now()
    comments = []
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def date_news():
    now = datetime.datetime.now()
    news_list = []
    for i in range(2):
        news = News.objects.create(
            title=f'Заголовок {i}',
            text=f'Text {i}',
            id=i
        )
        news.date = now - timedelta(days=i)
        news.save()
        news_list.append(news)
    return news_list


@pytest.fixture
def news_pagination():
    news_pagination = []
    for i in range(1, 31):
        new = News.objects.create(
            title=f'Заголовок {i}',
            text=f'Текст заметки {i}',
            id=i,
        )
        news_pagination.append(new)
    return news_pagination


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
        'id': 0,
    }
