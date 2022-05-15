from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

@cache_page(20)
def index(request):
    post_list = Post.objects.select_related("author", "group")
    paginator = Paginator(post_list, settings.SORTING_VALUE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "title": "Последнее обновление на сайте",
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related("author")
    paginator = Paginator(post_list, settings.SORTING_VALUE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "page_obj": page_obj,
    }

    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("group")
    paginator = Paginator(post_list, settings.SORTING_VALUE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    user = request.user
    following = user.is_authenticated and author.following.exists()
    context = {
        "author": author,
        "title": f"Профайл пользователя {username}",
        "page_obj": page_obj,
        "post_count": paginator.count,
        "following": following,
    }

    return render(request, "posts/profile.html", context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author", "group"),
        pk=post_id
    )
    post_count = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        "post": post,
        "group": post.group,
        "post_count": post_count,
        "form": form,
        "comments": comments,
    }
    return render(request, "posts/post_detail.html", context)

@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user.username)
    context = {"form": form, "title": "Создание"}
    return render(
        request,
        "posts/create_post.html",
        context        
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post.objects.select_related("author"), pk=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post.pk)
    form = PostForm(request.POST or None,
    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post.pk)
    context = {"form": form, "is_edit": True}
    return render(
        request,
        "posts/create_post.html",
        context  
    )

@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    post_list = Post.objects.filter(author__id__in=authors)
    paginator = Paginator(post_list, settings.SORTING_VALUE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)

@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect(
            'posts:profile',
            username=username
        )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.get(user=user, author__username=username).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))