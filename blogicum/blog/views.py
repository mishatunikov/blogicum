from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from blog.constants import OBJECTS_ON_PAGE
from blog.forms import CommentForm, PostForm, ProfileBaseForm
from blog.models import Category, Comment, Post, User


class ListViewMixin(ListView):
    paginate_by = OBJECTS_ON_PAGE


# Главная страница.
class IndexListView(ListViewMixin):
    paginate_by = OBJECTS_ON_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.published_with_comment.all()


# Страница категории.
class CategoryPostsListView(ListViewMixin):
    template_name = 'blog/category.html'
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(Category,
                                          slug=self.kwargs['category_slug'],
                                          is_published=True)
        return self.category.posts(manager='published_with_comment').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


# Система профиля.
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = ProfileBaseForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={
                'username': self.request.user.username
            }
        )


class ProfileListView(ListViewMixin):
    template_name = 'blog/profile.html'
    user = None

    def get_queryset(self):
        username = self.kwargs['username']
        self.user = get_object_or_404(User, username=username)

        if self.request.user.username == username:
            queryset = (Post.objects
                            .comment_count()
                            .filter(author__username=username))
        else:
            queryset = (Post.published_with_comment
                            .filter(author__username=username))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


# Система постинга.
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


def detail_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()

    if post.is_visible or post.author == request.user:
        return render(request, 'blog/detail.html', {'post': post,
                                                    'comments': comments,
                                                    'form': form})
    raise Http404


# Система комментирования.
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

    # Конкретно без этого переопределения не пропускали тесты, требовалось
    # чтобы в контексте не было "form".
    def get_context_data(self, **kwargs):
        return {'comment': self.get_object()}
