from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.permissions import (IsAdminOrOwnerOrSuperuserForUser,
                             IsAdminOrReadOnly,
                             IsAuthorOrAdminOrModeratorOrRead)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, GetTokenSerializer,
                             RegistrationsSerializer, ReviewSerializer,
                             TitleCreateSerializer, TitleSerializer,
                             UserSerializer)
from reviews.models import Category, Genre, Review, Title, User


@api_view(['POST'])
@permission_classes([permissions.AllowAny, ])
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
                f'Для пользователя {username} выпущен '
                f'confirmation_code: {token}',
                'from@example.com',
                [f'{email}'],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny, ])
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


class UserViewSet(viewsets.ModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdminOrOwnerOrSuperuserForUser, ]
    lookup_field = 'username'

    @action(detail=False, url_path='username')
    def username(self, request):
        user = get_object_or_404(User, username=self.kwargs['username'])
        serializer = self.get_serializer(user, many=False)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet модели Review. Позволяет работать с постами.
    Имеет функции: CRUD
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrModeratorOrRead, ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        # Добавил условие, чтобы в консоли не отображалась ошибка при
        # генерации документации yasg
        if getattr(self, 'swagger_fake_view', False):
            return Title.objects.none()
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet модели Comment. Позволяет работать с комментариями пользователей.
    Имеет функции: CRUD
    """
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthorOrAdminOrModeratorOrRead, ]

    def perform_create(self, serializer):
        review = get_object_or_404(Review, title_id=self.kwargs['title_id'],
                                   id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        # Добавил условие, чтобы в консоли не отображалась ошибка при
        # генерации документации yasg
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        review = get_object_or_404(
            Review, title_id=self.kwargs['title_id'],
            id=self.kwargs['review_id'],
        )
        return review.comments.all()


class ListCreateDestroyViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """
    Кастомный ViewSet для отображения списка, создания и удаления
    объектов
    """
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
    permission_classes = [IsAdminOrReadOnly, ]


class GenreViewSet(ListCreateDestroyViewSet):
    """
    ViewSet предназначен для просмотра списка категорий жанров, создания и
    удаления жанра
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]
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
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        # в зависимости от действия выбираем тот или иной сериалайзер
        if self.request.method in ['POST', 'PATCH']:
            return TitleCreateSerializer
        return TitleSerializer
