from django.contrib import admin

from .models import Post, Category, Location


class PostInline(admin.StackedInline):
    model = Post
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
        max_words = 10
        words = obj.text.split()
        shortened_text = ' '.join(words[:max_words])
        if len(words) > max_words:
            shortened_text += '...'
        return shortened_text

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


admin.site.empty_value_display = 'Не задано'
