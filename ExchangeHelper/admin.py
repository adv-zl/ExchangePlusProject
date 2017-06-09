from django.contrib import admin
from .models import OrdinaryCashier, ExchangeActions, AdministratorScraps, \
	ExchangeRates, IncreaseOperations

admin.site.register([OrdinaryCashier, ExchangeActions, AdministratorScraps,
					 ExchangeRates, IncreaseOperations])
# Register your models here.
