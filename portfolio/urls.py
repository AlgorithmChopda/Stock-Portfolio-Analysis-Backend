from django.urls import path
from portfolio.views import UploadFileView

urlpatterns = [
    path("upload", UploadFileView.as_view(), name="upload-file"),
]
