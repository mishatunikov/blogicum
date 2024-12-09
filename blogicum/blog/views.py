from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import (get_list_or_404, redirect, render,
                              get_object_or_404)
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import (CreateView, UpdateView, ListView,
                                  DetailView, DeleteView)

from blog.models import Comment, Post, Category, User
from .constants import OBJECTS_ON_PAGE
from blog.forms import CommentForm, ProfileBaseForm, PostForm


class IndexListView(ListView):
    paginate_by = OBJECTS_ON_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.published.all()


@login_required
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

    paginator = Paginator(posts, OBJECTS_ON_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/profile.html', {'page_obj': page_obj,
                                                 'profile': user})


def category_posts(request, category: str):
    """Отвечает за рендеринг страницы со всеми постави конкретной категории."""
    category = get_object_or_404(Category, slug=category)
    posts = get_list_or_404(category.posts(manager='published').all())
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'blog/category.html', {'category': category,
                                                  'page_obj': page_obj})


class PostMixin(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={'username': self.object.author})


class PostChangeMixin(UserPassesTestMixin, PostMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    # Если пользователь не является автором поста направляем его назад к
    # просмотру поста.
    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs.get('post_id'))


class PostCreateView(PostMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(PostChangeMixin, UpdateView):
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(PostChangeMixin, DeleteView):
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.all()
        return context


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('blog:post_detail', kwargs={'post_id': post.pk})


class CommentChangeMixin(UserPassesTestMixin, CommentMixin):
    def test_func(self):
        object = self.get_object()
        return self.request.user == object.author

    # Необходимо, чтобы на странице редактирования/удаления комментария,
    # при вводе в адресную строку несуществующего поста выдавало 404.
    def get_object(self, queryset=None):
        object = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post=self.kwargs['post_id'],
        )
        return object


class CommentCreateView(CommentMixin, CreateView):
    form_class = CommentForm
    current_post = None

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'POST':
            # Данный обработчик должен обслуживать только POST зпросы,
            # иначе при ручном вводе данного адреса будет выдана страница,
            # причем неккоректная.
            return redirect('blog:post_detail', kwargs.get('post_id'))
        self.current_post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.current_post
        return super().form_valid(form)


class CommentUpdateView(CommentChangeMixin, UpdateView):
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(CommentChangeMixin, DeleteView):
    pk_url_kwarg = 'comment_id'
