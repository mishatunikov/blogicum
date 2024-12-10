from django.contrib import admin

from blog.constants import COMMENT_DISPLAY_LENGTH
from blog.models import Category, Comment, Location, Post
from blog.utils import get_short_text


class PostInline(admin.StackedInline):
    model = Post
    extra = 1


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInline,)

    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = (
        'description',
        'slug',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = (
        'created_at',
        'is_published'
    )
    list_display_links = ('title',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = (CommentInline,)

    list_display = (
        'title',
        'short_text',
        'author',
        'pub_date',
        'location',
        'category',
        'is_published',
        'created_at',
    )

    @admin.display(description='Сокращенный текст')
    def short_text(self, obj) -> str:
        """Выводит сохращенный текст поста."""
        return get_short_text(text=obj.text)

    list_editable = (
        'author',
        'pub_date',
        'location',
        'category',
        'is_published'
    )
    search_fields = ('title',)
    list_filter = (
        'author',
        'category',
        'pub_date',
        'created_at',
        'is_published',
        'location'
    )
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (PostInline,)

    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = ('is_published',)
    list_filter = (
        'is_published',
        'created_at'
    )
    list_display_links = ('name', )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'short_comment',
        'author',
        'post',
        'created_at',
    )
    list_editable = ('author', 'post')
    list_filter = (
        'author',
        'post',
        'created_at',
    )
    list_display_links = ('short_comment', )

    @admin.display(description='Сокращенный текст')
    def short_comment(self, obj) -> str:
        """Выводит сохращенный текст комментария."""
        return get_short_text(
            text=obj.text,
            max_symbols=COMMENT_DISPLAY_LENGTH
        )


admin.site.empty_value_display = 'Не задано'
