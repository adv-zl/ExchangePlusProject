from django.contrib import admin
from .models import OrdinaryCashier, ExchangeActions, AdministratorCashCosts, ExchangeRates

admin.site.register([OrdinaryCashier, ExchangeActions, AdministratorCashCosts, ExchangeRates])
# Register your models here.
