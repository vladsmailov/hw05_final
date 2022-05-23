from django.contrib import admin

from .models import Group, Post, Follow, Comment

admin.site.register(Group)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    list_editable = ("group",)
    empty_value_display = "-пусто-"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("author",)
    list_filter = ("author",)
    list_editable = ("author",)
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created")
    search_fields = ("post",)
    list_filter = ("created",)
    list_editable = ("text",)
    empty_value_display = "-пусто-"
