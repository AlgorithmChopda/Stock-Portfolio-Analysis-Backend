from django.urls import path
from . import views

urlpatterns = [
    path("ipodata", views.ipo_api),
    path("gainers", views.gainers),
    path("losers", views.losers),
    path("indices", views.indices),
]
