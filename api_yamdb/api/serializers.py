from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review."""
    author = SlugRelatedField(slug_field='username', read_only=True)
    text = serializers.CharField(allow_blank=True, required=True)

    class Meta:
        fields = '__all__'
        model = Review

    def validate(self, data):
        """Проверка на лимит в 1 отзыв на 1 произведение."""
        author = self.context['request'].user
        title = self.context['view'].kwargs['title_id']
        if (
            self.context['request'].method == 'POST'
            and Review.objects.filter(author=author, title=title).exists()
        ):
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв к данному произведению!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
