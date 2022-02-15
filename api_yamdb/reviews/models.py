from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ANONIMUS = 'anon'
    AUTHENTICATED = 'user'
    MODERATOR = 'moder'
    ADMINISTRATOR = 'admin'
    SUPERUSER = 'root'
    ROLE_CHOISES = [
        (ANONIMUS, 'Аноним'),
        (AUTHENTICATED, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMINISTRATOR, 'Администратор'),
        (SUPERUSER, 'Суперюзер Django'),
    ]
    role = models.CharField(
        max_length=5,
        choices=ROLE_CHOISES,
        default=AUTHENTICATED
    ),
    bio = models.TextField(
        'Биография',
        blank=True,
    ),

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_registration'
            )
        ]



class Title(models.Model):
    pass


class Review(models.Model):
    text = models.TextField(verbose_name='текст отзыва')
    pub_date = models.DateTimeField(verbose_name='дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews', verbose_name='автор публикации')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='наименование произведения'
    )
    score = models.IntegerField(verbose_name='оценка произведения', validators = [MinValueValidator(1), MaxValueValidator(10)])

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments', verbose_name='автор комментария')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments', verbose_name='отзыв')
    text = models.TextField(verbose_name='текст комментария')
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True
    )
    
    def __str__(self):
        return self.text

