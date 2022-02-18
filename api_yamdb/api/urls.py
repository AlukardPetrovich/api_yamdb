from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       get_token, registrations, ReviewViewSet, TitleViewSet,
                       UserViewset)

router = DefaultRouter()
router.register('users', UserViewset, basename='users')
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', registrations),
    path('v1/auth/token/', get_token),
]
