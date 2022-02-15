from django.contrib.auth.models import AbstractUser
from django.db import models


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
