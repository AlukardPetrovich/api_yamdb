from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, GetTokenSerializer,
                             RegistrationsSerializer, ReviewSerializer,
                             TitleCreateSerializer, TitleSerializer,
                             UserSerialiser)
from reviews.models import Category, Genre, Review, Title, User
from .permissions import IsAuthorOrAdminOrReadOnly


@api_view(['POST'])
@permission_classes([AllowAny, ])
def registrations(request):
    if request.method == 'POST':
        serializer = RegistrationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.data['email']
            username = serializer.data['username']
            user = get_object_or_404(User, username=username)
            token = default_token_generator.make_token(user)
            send_mail(
                'Ваш confirmation_code',
                f'Для пользавателя {username} выпущен'
                f'confirmation_code:{token}',
                'from@example.com',
                [f'{email}'],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def get_token(request):
    if request.method == 'POST':
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User,
                username=serializer.data['username']
            )
            confirmation_code = request.data['confirmation_code']
            if default_token_generator.check_token(
                user,
                confirmation_code
            ) is True:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {'access': str(refresh.access_token)},
                    status=status.HTTP_200_OK
                )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewset(viewsets.ModelViewSet):
    serializer_class = UserSerialiser


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet модели Review. Позволяет работать с постами.
    Имеет функции: CRUD
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # Добавил условие, чтобы в консоли не отображалась ошибка при
        # генерации документации yasg
        if getattr(self, 'swagger_fake_view', False):
            return Title.objects.none()
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        queryset = title.reviews.all()
        return queryset

    def perform_update(self, serializer):
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet модели Comment. Позволяет работать с комментариями пользователей.
    Имеет функции: CRUD
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        # Добавил условие, чтобы в консоли не отображалась ошибка при
        # генерации документации yasg
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        review = get_object_or_404(
            Review, id=self.kwargs['review_id'],
            title=self.kwargs['title_id']
        )
        queryset = review.comments.all()
        return queryset


class ListCreateDestroyViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """
    Кастомный ViewSet для отображения списка, создания и удаления
    объектов
    """
    pass


class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Кастомный ViewSet для создания и удаления объектов"""
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    ViewSet предназначен для просмотра списка категорий (типы)
    произведений, создания и удаления категории
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = []


class GenreViewSet(ListCreateDestroyViewSet):
    """
    ViewSet предназначен для просмотра списка категорий жанров, создания и
    удаления жанра
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet предоставляет CRUD действия с произведения, к которым пишут
    отзывы (определённый фильм, книга или песенка).
    """
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')

    # def get_queryset(self):
    #     # Добавил условие, чтобы в консоли не отображалась ошибка при
    #     # генерации документации yasg
    #     if getattr(self, 'swagger_fake_view', False):
    #         return Title.objects.none()
    #     # определяю queryset для получения всех комментариев поста
    #     title_id = self.kwargs.get('titles_id')
    #     title = get_object_or_404(Title, id=title_id)
    #     return title

    def get_serializer_class(self):
        # в зависимости от действия выбираем тот или иной сериалайзер
        if self.request.method in ['POST', 'PATCH']:
            return TitleCreateSerializer
        return TitleSerializer
