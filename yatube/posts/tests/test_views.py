from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

import math

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()


class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoNameAuthor')
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост на 100500 символов',
            group=cls.group)

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
