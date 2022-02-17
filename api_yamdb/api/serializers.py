from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User


class RegistrationsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=30,
        min_length=6,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть me')
        return data

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    confirmation_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def get_confirmation_code(self, obj):
        return



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
    """Сериализатор списка произведений"""
    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')

    def get_rating(self, obj):
        return round(obj.reviews.all().aggregate(Avg('score'))[
                         'score__avg'], 1)


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления произведения"""
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         slug_field='slug', many=True)

    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')
