from django.db import models
from django.utils import timezone
from django.db.models import Count


class PostQuerySet(models.QuerySet):
    def with_union_data(self) -> 'PostQuerySet':
        return self.select_related('category')

    def is_published(self) -> 'PostQuerySet':
        return self.filter(is_published=True,
                           pub_date__lt=timezone.now(),
                           category__is_published=True)

    def comment_count(self) -> 'PostQuerySet':
        return (self.annotate(comment_count=Count('comments'))
                    .order_by('-pub_date'))


class PublishedPostManager(models.Manager):
    def get_queryset(self) -> PostQuerySet:
        return (PostQuerySet(self.model)
                .with_union_data()
                .is_published())


class PublishedPostWithCommentManager(models.Manager):
    def get_queryset(self) -> PostQuerySet:
        return (PostQuerySet(self.model)
                .with_union_data()
                .is_published()
                .comment_count())
