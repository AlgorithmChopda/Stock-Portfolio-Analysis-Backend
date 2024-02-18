from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import serializers
from django.core.serializers import serialize

from auth_app.models import User

from .serializers import LoginSerializer, UserSerializer


@csrf_exempt
def loginAPI(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        login_serializer = LoginSerializer(data=data)

        try:
            user = login_serializer.validate(data)
            user_response = {"id": user.id, "name": user.username, "email": user.email}
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Login successful",
                    "data": user_response
                },
                status=200,
            )
        except User.DoesNotExist as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Invalid credentials",
                    "data": {},
                },
                status=401,
            )

        except serializers.ValidationError as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": e,
                    "data": {},
                },
                status=401,
            )

        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "internal server error",
                    "data": {},
                },
                status=500,
            )


@csrf_exempt
def registerAPI(request):
    if request.method == "POST":
        # TODO: add check for same email
        user_data = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse("user created successfully", safe=False)
        return JsonResponse("failed to create user", safe=False)
