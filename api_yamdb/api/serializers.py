import re

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User


class RegistrationsSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрацции нового пользователя"""
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть me')
        if not re.match(r'^[\w.@+-]', data['username']):
            raise serializers.ValidationError(
                'Имя пользователя может содержать буквы, цифры, '
                'символы ".", "@", "+", "-", " "'
            )
        return data

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class GetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор получения авторизационного токена"""
    username = serializers.CharField()
    confirmation_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code',)

    def get_confirmation_code(self, obj):
        return


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели кастомного пользователя"""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role',)


class MeSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(read_only=True)
    email = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role',)

    def update(self, instance, validated_data):
        user = get_object_or_404(User, username=instance)
        if user.role == 'user' and 'role' in validated_data:

            validated_data.pop('role')
        return super().update(instance, validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review."""
    author = SlugRelatedField(slug_field='username', read_only=True)
    text = serializers.CharField(allow_blank=True, required=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
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
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий произведений"""

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра произведения"""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор списка произведений"""
    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category',)

    def get_rating(self, obj):
        return obj.reviews.all().aggregate(Avg('score'))['score__avg']


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления произведения"""
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         slug_field='slug', many=True)
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category',)
