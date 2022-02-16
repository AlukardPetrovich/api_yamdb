from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from reviews.models import Category, Comment, Genre, Review, Title



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



class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий произведений"""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра произведения"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведения"""
    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')

    def get_rating(self, obj):
        return obj.reviews.all().aggregate(Avg('score'))['score__avg']

