import pandas as pd
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response

from .models import File
from .serializers import FileUploadSerializer, SaveFileSerializer


class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        reader = pd.read_csv(file)

        # TODO: to be changed
        for _, row in reader.iterrows():
            print(row["name"], row["buy_price"], row["quantity"], row["profit_loss"])
            new_file = File(
                name=row["name"],
                buy_price=row["buy_price"],
                quantity=row["quantity"],
                profit_loss=row["profit_loss"],
            )
            new_file.save()
        return Response({"status": "success"})
