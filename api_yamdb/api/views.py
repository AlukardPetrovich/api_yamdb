from rest_framework import viewsets
from .serializers import (CommentSerializer, ReviewSerializer)
from review.models import Review
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import get_object_or_404


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet модели Review. Позволяет работать с постами.
    Имеет функции: CRUD
    Тип доступа: чтение/авторизация
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet модели Comment. Позволяет работать с комментариями пользователей.
    Имеет функции: CRUD
    Тип доступа: чтение/авторизация
    """
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        queryset = review.comments.all()
        return queryset