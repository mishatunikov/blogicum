from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from blog.constants import COMMENT_DISPLAY_LENGTH, MAX_LENGTH_STRING
from blog.querysets import PostQuerySet, PublishedPostManager
from blog.utils import get_short_text

User = get_user_model()


class CreationBase(models.Model):
    """
    Абстрактная моделью.
    Добавляет к модели дату создания.
    """

    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-created_at', )


class PublicationBase(CreationBase):
    """
    Абстрактная моделью.
    Добавляет к модели поле is_published (True по умолчанию).
    """

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta(CreationBase.Meta):
        abstract = True


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
        upload_to='posts_images',
        blank=True
    )
    objects = PostQuerySet.as_manager()
    published = PublishedPostManager()

    @property
    def is_visible(self):
        return (self.pub_date <= timezone.now()
                and self.category.is_published
                and self.is_published)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.title


class Category(PublicationBase):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_STRING)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta(PublicationBase.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title


class Location(PublicationBase):
    name = models.CharField('Название места', max_length=MAX_LENGTH_STRING)

    class Meta(PublicationBase.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name


class Comment(CreationBase):
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return get_short_text(self.text, max_symbols=COMMENT_DISPLAY_LENGTH)
