from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       get_token, registrations, ReviewViewSet, TitleViewSet,
                       UserViewSet, MeAPI)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register(r'titles', TitleViewSet, basename='titles')
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
    path('v1/users/me/', MeAPI.as_view()),
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', registrations),
    path('v1/auth/token/', get_token),
]
