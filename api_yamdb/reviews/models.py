from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):

    AUTHENTICATED = 'user'
    MODERATOR = 'moderator'
    ADMINISTRATOR = 'admin'
    ROLE_CHOISES = [
        (AUTHENTICATED, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMINISTRATOR, 'Администратор'),
    ]
    role = models.CharField(
        max_length=5,
        choices=ROLE_CHOISES,
        default=AUTHENTICATED
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_registration'
            )
        ]


class Category(models.Model):
    """Модель категорий (типы) произведений («Фильмы», «Книги», «Музыка»)"""

    name = models.CharField(max_length=256, verbose_name='Имя категории')
    slug = models.SlugField(max_length=50, unique=True,
                            verbose_name='Слаг категории')

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанра произведения"""

    name = models.CharField(max_length=256, verbose_name='Имя жанра')
    slug = models.SlugField(max_length=50, unique=True,
                            verbose_name='Слаг жанра')

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Модель произведения, к которым пишут отзывы (определённый фильм, книга
    или песенка)
    """
    name = models.CharField(max_length=500, verbose_name='Название')
    year = models.PositiveIntegerField(verbose_name='Год выпуска',
                                       validators=[
                                           MinValueValidator(1000),
                                           MaxValueValidator(
                                               datetime.now().year)
                                       ])
    description = models.TextField(verbose_name='Описание', blank=True,
                                   null=True)
    genre = models.ManyToManyField(Genre,
                                   related_name='titles',
                                   verbose_name='Жанры произведения')
    category = models.ForeignKey(Category,
                                 related_name='titles',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория произведения')

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель отзыва о произведение.
    """
    text = models.TextField(verbose_name='текст отзыва')
    pub_date = models.DateTimeField(verbose_name='дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='автор публикации')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='наименование произведения'
    )
    score = models.IntegerField(verbose_name='оценка произведения',
                                validators=[
                                    MinValueValidator(1),
                                    MaxValueValidator(10)
                                ])

    def __str__(self):
        return self.text


class Comment(models.Model):
    """
    Модель комментария к отзыву.
    """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='автор комментария')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='отзыв')
    text = models.TextField(verbose_name='текст комментария')
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return self.text
