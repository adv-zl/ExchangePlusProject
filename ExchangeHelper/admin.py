from django.contrib import admin
from .models import OrdinaryCashier, ExchangeActions, MoneyRequest, \
	ExchangeRates, IncreaseOperations, Scrap

admin.site.register([OrdinaryCashier, ExchangeActions, MoneyRequest, ExchangeRates, IncreaseOperations, Scrap])
# Register your models here.
