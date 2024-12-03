from django.shortcuts import get_list_or_404, render, get_object_or_404

from blog.models import Post, Category
from .constants import ON_MAIN_PAGE


def index(request):
    """Отвечает за рендеринг главной страницы."""
    posts = Post.published.all()[:ON_MAIN_PAGE]
    context = {'post_list': posts}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id: int):
    """Отвечает за рендеринг страницы детального отбражения поста."""
    context = {
        'post': get_object_or_404(
            Post.published.all(),
            pk=post_id
        )
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug: str):
    """Отвечает за рендеринг страницы со всеми постави конкретной категории."""
    category = get_object_or_404(Category, slug=category_slug)
    posts = category.posts(manager='published').all()

    context = {
        'category': category_slug,
        'post_list': get_list_or_404(posts)
    }

    return render(request, 'blog/category.html', context)
