from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from review.models import Review, Comment, User

class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review."""
    author = SlugRelatedField(slug_field='username', read_only=True)
    text = serializers.CharField(allow_blank=True, required=True)

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment