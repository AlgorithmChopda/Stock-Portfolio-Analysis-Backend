from django.db import models


class File(models.Model):
    name = models.CharField(max_length=100)
    buy_price = models.FloatField()
    quantity = models.IntegerField()
    profit_loss = models.FloatField()
    sector=models.CharField(max_length=100)
    invested_value = models.FloatField()
