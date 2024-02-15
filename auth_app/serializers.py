from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password", "id")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("email and password are required.")

        try:
            user = User.objects.get(email=email, password=password)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
