from django.shortcuts import get_list_or_404, render, get_object_or_404
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from blog.models import Post, Category
from .constants import ON_MAIN_PAGE


User = get_user_model()


class PostCreateView(CreateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')


def profile(request, username):
    posts = Post.objects.filter(author__username=username)
    user = User.objects.get(username=username)
    paginator = Paginator(posts, ON_MAIN_PAGE)

    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/profile.html', {'page_obj': page_obj,
                                                 'profile': user})


def index(request):
    """Отвечает за рендеринг главной страницы."""
    posts = Post.published.all()
    paginator = Paginator(posts, ON_MAIN_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'page_obj': page_obj}
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
    posts = get_list_or_404(category.posts(manager='published').all())
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'category': category_slug,
        'page_obj': page_obj
    }

    return render(request, 'blog/category.html', context)
