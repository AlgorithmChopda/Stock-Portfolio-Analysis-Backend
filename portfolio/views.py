import pandas as pd
from django.shortcuts import render
from rest_framework import generics
from django.http import JsonResponse

from .models import File
from .serializers import FileUploadSerializer, SaveFileSerializer


class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        reader = pd.read_csv(file)

        # TODO: store in DB
        portfolio_stock = []
        total_invested_value, profit_loss = 0

        for _, row in reader.iterrows():
            portfolio_stock.append(
                {
                    "name": row["name"],
                    "sector": row["sector"],
                    "buy_price": row["buy_price"],
                    "quantity": row["quantity"],
                    "profit_loss": row["profit_loss"],
                    "invested_value": row["invested_value"],
                }
            )
            total_invested_value += row["invested_value"]
            profit_loss += row["profit_loss"]

        return JsonResponse({"status": "success"})


# print(
#     row["name"],
#     row["sector"],
#     row["buy_price"],
#     row["quantity"],
#     row["profit_loss"],
#     row["invested_value"],
# )
# new_file = File(
#     name=row["name"],
#     sector=row["sector"],
#     quantity=row["quantity"],
#     buy_price=row["buy_price"],
#     invested_value=row["invested_value"],
#     profit_loss=row["profit_loss"],
# )
# new_file.save()
