from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from .constants import MAX_LENGTH_STRING
from .querysets import PostQuerySet, PublishedPostManager


User = get_user_model()


class PublicationBase(models.Model):
    """
    Абстрактная моделью.
    Добавляет к модели дату создания и поле is_published (True по умолчанию).
    """

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('created_at', )


class Post(PublicationBase):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_STRING)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )

    image = models.ImageField(
        'Изображение',
        upload_to='posts_image',
        blank=True
    )
    objects = PostQuerySet.as_manager()
    published = PublishedPostManager()

    @property
    def comment_count(self):
        return self.comment.count

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        # С помощью функции reverse() возвращаем URL объекта.
        return reverse('blog:profile', kwargs={'username': self.author})



class Category(PublicationBase):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_STRING)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title


class Location(PublicationBase):
    name = models.CharField('Название места', max_length=MAX_LENGTH_STRING)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comment'
        ordering = ('created_at',)
