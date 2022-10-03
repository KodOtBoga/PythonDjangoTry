from rest_framework import serializers
from apps.library.models import *


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'description',
            'author',
            'rating',
            'published'
        )


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auth
        fields = "__all__"
    # class Meta:
    #     model = Auth
    #     fields = (
    #         'id',
    #         'email',
    #         'password'
    #     )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "last_login"
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
