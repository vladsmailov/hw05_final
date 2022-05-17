import math
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoNameAuthor')
        cls.follower = User.objects.create_user(username='Follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.COUNT = 12
        cls.urls = (
            (reverse('posts:index')),
            (reverse('posts:group_list',
             kwargs={'slug': cls.group.slug})),
            (reverse('posts:profile', kwargs={'username': cls.user})),
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост на 100500 символов',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Проверка паджинатора"""
        Post.objects.bulk_create([Post(
            author=self.user,
            text='Пост на 100500 символов',
            group=self.group,
        )for _ in range(self.COUNT)]
        )
        total_number_of_posts = self.COUNT + 1
        total_number_of_pages = math.ceil(
            total_number_of_posts / settings.SORTING_VALUE)
        posts_per_page = []
        for page in range(total_number_of_pages + 1):
            if total_number_of_posts >= settings.SORTING_VALUE:
                posts_per_page = [(page, settings.SORTING_VALUE)]
                total_number_of_posts -= settings.SORTING_VALUE
            else:
                posts_per_page = [(page, total_number_of_posts)]
        for url in self.urls:
            for page, count in posts_per_page:
                with self.subTest(url=url):
                    response = self.guest_client.get(url, {'page': page})
                    self.assertEqual(len(
                        response.context['page_obj']),
                        count
                    )

    def test_context_for_index_group_list_profile(self):
        """Проверка контекста страниц index, group_list, profile"""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertIn(self.post, response.context.get('page_obj'))

    def test_context_for_post_detail(self):
        """Проверка контекста на странице detail одного выбранного поста"""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            args={self.post.id}
        )
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_context_for_post_create(self):
        """Проверка контекста на странице create"""

        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_context_for_post_edit(self):
        """Проверка контекста на странице edit"""

        response = self.authorized_client.get(reverse(
            'posts:post_edit', args={self.post.id}))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context.get('form').instance, self.post)

    def test_cache(self):
        """Тест кэша страницы index"""
        response_1 = self.authorized_client.get(reverse("posts:index"))
        Post.objects.get(pk=self.post.pk).delete()
        response_2 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()

    def test_follow(self):
        """Тест подписки на автора"""
        self.authorized_client.force_login(self.follower)
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        )
        )
        self.assertTrue(Follow.objects.get(
            user=self.follower,
            author=self.user.id
        )
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}
        )
        )
        self.assertFalse(Follow.objects.filter(
            user=self.follower,
            author=self.user.id
        ).exists()
        )

    def test_new_posts_for_subscribers(self):
        """Тест появления новых постов у подписчиков"""
        self.authorized_client.force_login(self.follower)
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        )
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context.get('page_obj'))
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}
        )
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context.get('page_obj'))
