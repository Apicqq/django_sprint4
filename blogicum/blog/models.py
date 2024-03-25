from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.timezone import now

from blog.constants import STRING_MAX_LENGTH, TITLE_MAX_LENGTH
from core.models import PublishedCreatedModel

User = get_user_model()


class PostQueryset(models.QuerySet):

    def annotated(self):
        return self.annotate(comment_count=Count('comments'))

    def prefetched(self):
        return self.prefetch_related('comments')

    def select_relatable(self):
        return self.select_related('category',
                                   'author',
                                   'location')

    def category_is_published(self):
        return self.filter(category__is_published=True)

    def published(self):
        return self.filter(is_published=True)

    def pub_date(self):
        return self.filter(pub_date__lte=now())


class Post(PublishedCreatedModel):
    title = models.CharField('Заголовок', max_length=STRING_MAX_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно делать '
                  'отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True
    )
    objects = PostQueryset.as_manager()

    class Meta(PublishedCreatedModel.Meta):
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('pub_date',)

    def __str__(self):
        return self.title[:TITLE_MAX_LENGTH]

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})


class Category(PublishedCreatedModel):
    title = models.CharField('Заголовок', max_length=STRING_MAX_LENGTH)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы латиницы,'
                  ' цифры, дефис и подчёркивание.')

    class Meta(PublishedCreatedModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:TITLE_MAX_LENGTH]


class Location(PublishedCreatedModel):
    name = models.CharField('Название места', max_length=STRING_MAX_LENGTH)

    class Meta(PublishedCreatedModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:TITLE_MAX_LENGTH]


class Comment(PublishedCreatedModel):
    text = models.TextField('Текст комментария', max_length=STRING_MAX_LENGTH)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация'
    )

    class Meta:
        ordering = ('created_at',)
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:TITLE_MAX_LENGTH]

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.post.pk})
