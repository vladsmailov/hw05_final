from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-profile')
        cls.user_not_the_author = User.objects.create_user(
            username='test-profile-2'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост на 100500 символов',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_not_the_author)

    def test_urls_uses_correct_names(self):
        """URL-адрес использует соответствующее имя"""
        tested_urls = {
            "/": reverse('posts:index'),
            f"/group/{self.group.slug}/": reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            f'/profile/{self.user.username}/': reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            f'/posts/{self.post.id}/': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            '/create/': reverse('posts:post_create'),
            f'/posts/{self.post.id}/edit/': reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ),
            '/follow/': reverse('posts:follow_index'),

        }
        for url, name in tested_urls.items():
            with self.subTest(name=name):
                self.assertEqual(name, url)

    def test_page_access(self):
        # sourcery skip: assign-if-exp, swap-if-expression
        """Тест страниц доступных неавторизованным пользователям"""
        names = (
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}), 200, False),
            (reverse('posts:profile',
                     kwargs={'username': self.user.username}), 200, False),
            (reverse('posts:post_detail',
                     kwargs={'post_id': self.post.id}), 200, False),
            (reverse('posts:index'), 200, False),
            (reverse('posts:post_detail', kwargs={'post_id': 0}), 404, False),
            (reverse('posts:post_create'), 200, True),
            (reverse('posts:follow_index'), 302, False),
        )
        for url, expected_status, bool_flag in names:
            if not bool_flag:
                response = self.guest_client.get(url)
            else:
                response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, expected_status)

    def test_edit(self):
        """Тест редактирования поста"""
        login_page_url = reverse("users:login")
        post_edit_page_url = reverse("posts:post_edit",
                                     kwargs={"post_id": self.post.id})
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.id}))
        response = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertRedirects(
            response, (f'{login_page_url}?next={post_edit_page_url}'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        tested_urls = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/follow.html': reverse('posts:follow_index'),
        }
        for template, url in tested_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
