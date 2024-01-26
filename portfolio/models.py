from django.db import models


class File(models.Model):
    name = models.CharField(max_length=100)
    buy_price = models.IntegerField()
    quantity = models.IntegerField()
    profit_loss = models.IntegerField()
