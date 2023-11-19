from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        clients = []
        for user in (cls.author, cls.reader):
            client = Client()
            client.force_login(user)
            clients.append(client)
        cls.author_client, cls.reader_client = clients
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug="note-slug",
            author=cls.author
        )

    def get_logined_client(self, user):
        client = Client()
        client.force_login(user)
        return client

    def test_notes_list_for_different_users(self):
        url = reverse('notes:list')
        note_list_presence = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in note_list_presence:
            with self.subTest(
                user=user, note_in_list=note_in_list
            ):
                url = reverse('notes:list')
                client = self.get_logined_client(user)
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                object_list = response.context['object_list']
                assert (self.note in object_list) is note_in_list

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                client = self.get_logined_client(self.author)
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                assert 'form' in response.context
