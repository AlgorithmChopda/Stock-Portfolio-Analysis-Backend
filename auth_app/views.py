from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from auth_app.models import User

from .serializers import LoginSerializer, UserSerializer


@csrf_exempt
def loginAPI(request):
    if request.method == "POST":
        print("data : ", request)
        data = JSONParser().parse(request)
        print(data)
        login_serializer = LoginSerializer(data=data)

        try:
            if login_serializer.validate(data):
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Login successful",
                        # "data": user,
                    },
                    status=200,
                )
            else:
                return JsonResponse(
                    {
                        "status": "temp",
                        "message": "Invalid credentials",
                        "data": None,
                    },
                    status=401,
                )
        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Invalid credentials",
                    "data": None,
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
