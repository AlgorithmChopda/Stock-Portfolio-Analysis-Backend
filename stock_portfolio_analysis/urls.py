from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin", admin.site.urls),
    path("auth/", include("auth_app.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("scrapper/", include("scrapper.urls")),
]
