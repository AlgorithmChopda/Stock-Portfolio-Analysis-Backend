from django.urls import path
from . import views

urlpatterns=[
    path('ipodata/',views.ipo_api),
]