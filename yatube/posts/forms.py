from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Введите текст', 'group': 'Выберите группу'}
        help_texts = {
            'text': 'Текст которым вы хотите поделиться',
            'group': 'Группа к которой ближе лежит пост'
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
