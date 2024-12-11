from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, ListView,
                                  UpdateView, DetailView)

from blog.constants import OBJECTS_ON_PAGE
from blog.forms import CommentForm, PostForm, ProfileBaseForm
from blog.models import Category, Comment, Post, User


# Mixins.
class ListViewMixin(ListView):
    paginate_by = OBJECTS_ON_PAGE


class UserAccessMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostMixin(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self) -> str:
        return reverse('blog:profile',
                       kwargs={'username': self.object.author.username})


class PostChangeMixin(UserAccessMixin, PostMixin):
    def handle_no_permission(self):
        """
        Если пользователь не является автором поста направляем его назад к
        просмотру поста.
        """
        return redirect('blog:post_detail', self.kwargs.get('post_id'))


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post = self.object.post
        return reverse('blog:post_detail', kwargs={'post_id': post.pk})


class CommentChangeMixin(UserAccessMixin, CommentMixin):
    pk_url_kwarg = 'comment_id'

    # Необходимо, чтобы на странице редактирования/удаления комментария,
    # при вводе в адресную строку несуществующего поста выдавало 404.
    def get_object(self, queryset=None):
        object = get_object_or_404(
            Comment,
            pk=self.kwargs.get(self.pk_url_kwarg),
            post=self.kwargs.get('post_id'),
        )
        return object


# Главная страница.
class IndexListView(ListViewMixin):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.published_with_comment.all()


# Страница категории.
class CategoryPostsListView(ListViewMixin):
    template_name = 'blog/category.html'
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'),
            is_published=True
        )
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
        return reverse(
            'blog:profile', kwargs={
                'username': self.object.username
            }
        )


class ProfileListView(ListViewMixin):
    template_name = 'blog/profile.html'
    user = None

    def get_queryset(self):
        username = self.kwargs.get('username')
        self.user = get_object_or_404(User, username=username)

        if self.request.user.username == username:
            posts = self.user.posts.comment_count()

        else:
            posts = self.user.posts(manager='published_with_comment')

        return posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


# Система постинга.
class PostCreateView(PostMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(PostChangeMixin, UpdateView):
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_success_url(self) -> str:
        print(self.pk_url_kwarg)
        return reverse('blog:post_detail',
                       kwargs={self.pk_url_kwarg: self.object.pk})


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

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not (post.is_visible or post.author == self.request.user):
            raise Http404

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': CommentForm(),
                        'comments': self.get_object().comments.all()})
        return context


# Система комментирования.
class CommentCreateView(CommentMixin, CreateView):
    form_class = CommentForm
    current_post = None

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'POST':
            # Данный обработчик должен обслуживать только POST зпросы,
            # иначе при ручном вводе данного адреса будет выдана страница,
            # причем неккоректная.
            return redirect('blog:post_detail', kwargs.get('post_id'))
        self.current_post = get_object_or_404(Post, pk=kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.current_post
        return super().form_valid(form)


class CommentUpdateView(CommentChangeMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentChangeMixin, DeleteView):
    # Конкретно без этого переопределения не пропускали тесты, требовалось
    # чтобы в контексте не было "form".
    def get_context_data(self, **kwargs):
        return {'comment': self.get_object()}
