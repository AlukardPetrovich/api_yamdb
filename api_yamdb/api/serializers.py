from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Review, Comment, User
from rest_framework.validators import UniqueValidator


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
    # Возможно нужен Валидатор на проверку создания только 1 поста от 1 автора

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
