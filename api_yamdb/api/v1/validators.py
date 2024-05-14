from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


def name_is_not_me(username):
    if username and username.lower() == 'me':
        raise serializers.ValidationError('Имя не может быть <me>')


def username_and_email_are_unique(username, email):
    """
    Проверка на уникальность имени с email по отдельности,
    если юзер с таким именем и почтой существует,
    то ошибки нет(необходимо для повторной отправки кода подтверждения)
    """

    user_by_username = User.objects.filter(username=username).first()
    user_by_email = User.objects.filter(email=email).first()

    if user_by_username and not user_by_email:
        raise serializers.ValidationError(
            'Пользователь с таким именем уже существует'
        )
    if user_by_email and not user_by_username:
        raise serializers.ValidationError(
            'Пользователь с таким email уже существует'
        )