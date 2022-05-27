from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_comment_create(self):
        """
        Тестирование отправки валидной
        формы неавторизованным пользователем
        """
        comment_url = reverse("posts:add_comment", args={self.post.id})
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', args={self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'{reverse("users:login")}?next={comment_url}'
                             )
        self.assertFalse(
            Comment.objects.filter(
                text=form_data['text'],
            ).exists()
        )
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_comment_create_authorisated_user(self):
        """
        Проверка создания комментария,
        соответствия авторства комментария,
        прикрепления комментария к
        соответствующему посту
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Автор пиши еще!',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        )
        )
        self.assertTrue(Comment.objects.filter(
            text=form_data['text'],
            author=self.user,
            id=self.post.id,
        ).exists()
        )
