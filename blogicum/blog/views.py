from django.db.models.query import QuerySet
from django.shortcuts import (get_list_or_404, redirect, render,
                              get_object_or_404)
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from blog.models import Post, Category, User
from .constants import ON_MAIN_PAGE
from blog.forms import ProfileBaseForm


class PostCreateView(CreateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')

class IndexListView(ListView):
    model = Post
    paginate_by = ON_MAIN_PAGE
    template_name = 'blog/index.html'


def edit_profile(request):
    instance = get_object_or_404(User, username=request.user)
    form = ProfileBaseForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/user.html', {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author__username=username)
    paginator = Paginator(posts, ON_MAIN_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/profile.html', {'page_obj': page_obj,
                                                 'profile': user})


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


# Класс для отображения профиля на CBV
# class ProfileListView(ListView):
#     model = Post
#     paginate_by = 10
#     template_name = 'blog/profile.html'

#     def get_queryset(self):
#         return (Post.objects
#                 .select_related('author')
#                 .filter(author__username=self.kwargs['username']))

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
#         return context
