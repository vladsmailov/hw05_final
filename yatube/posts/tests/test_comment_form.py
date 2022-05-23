from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CommentForm
from ..models import Comment, Post

User = get_user_model()


class CommentFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='UnnamedAuthor')
        cls.post = Post.objects.create(
            text='Тестовый пост на 100500 символов',
            author=cls.user,
        )
        cls.form = CommentForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_create_authorisated_user(self):
        """Проверка создания комментария"""
        post_comment_count = Comment.objects.count()
        form_data = {
            'text': 'Автор пиши еще!',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), post_comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        )
        )

    def test_comment_has_corresponding_text(self):
        """Комментарий имеет соответствующий текст"""
        form_data = {
            'text': 'Автор пиши еще!',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(Comment.objects.filter(
            text=form_data['text']))

    def test_has_correct_connection(self):
        """Комментарий прикреплен к соответствующему посту"""
        form_data = {
            'text': 'Автор пиши еще!',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.id, response.context.get('comments')[0].id)
