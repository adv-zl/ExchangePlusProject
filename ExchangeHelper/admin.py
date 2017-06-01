from django.contrib import admin
from .models import OrdinaryCashier, ExchangeActions, AdministratorCashCosts, \
	ExchangeRates, IncreaseOperations

admin.site.register([OrdinaryCashier, ExchangeActions, AdministratorCashCosts,
					 ExchangeRates, IncreaseOperations])
# Register your models here.
