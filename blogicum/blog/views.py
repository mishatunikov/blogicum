from django.db.models.base import Model as Model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import (get_list_or_404, redirect, render,
                              get_object_or_404)
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView

from blog.models import Comment, Post, Category, User
from .constants import ON_MAIN_PAGE
from blog.forms import CommentForm, ProfileBaseForm, PostForm


class IndexListView(ListView):
    paginate_by = ON_MAIN_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.published.all()


def edit_profile(request):
    instance = get_object_or_404(User, username=request.user)
    form = ProfileBaseForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/user.html', {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)

    if username == request.user.username:
        posts = Post.objects.filter(author__username=username)
    else:
        posts = Post.published.filter(author__username=username)

    paginator = Paginator(posts, ON_MAIN_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/profile.html', {'page_obj': page_obj,
                                                 'profile': user})


class PostMixin:
    model = Post
    template_name = 'blog/create.html'


class PostChangeMixin(UserPassesTestMixin):
    model = Post
    template_name = 'blog/create.html'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(PostChangeMixin, UpdateView):
    # model = Post
    form_class = PostForm
    # template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    # def test_func(self):
    #     object = self.get_object()
    #     return object.author == self.request.user


class PostDeleteView(PostChangeMixin, DeleteView):
    # model = Post
    # form_class = PostForm
    # template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={'username': self.object.author})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    # def test_func(self):
    #     object = self.get_object()
    #     return object.author == self.request.user


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm
        context['comments'] = self.object.comment.all()
        return context


def delete_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    form = PostForm(instance=instance)

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')

    return render(request, 'blog/create.html', {'form': form})


def post_detail(request, post_id: int):
    """Отвечает за рендеринг страницы детального отбражения поста."""
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'form': CommentForm,
        'comments': post.comment.all(),
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
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render(request, 'blog/comment.html', {'comment': comment,
                                                 'form': form})


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {'comment': comment})

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

# CBV для удаления и детального отображения постов.
# class PostDeleteView(DeleteView):
#     model = Post
#     # form_class = PostForm
#     template_name = 'blog/create.html'
#     pk_url_kwarg = 'post_id'
#     success_url = reverse_lazy('blog:index')
