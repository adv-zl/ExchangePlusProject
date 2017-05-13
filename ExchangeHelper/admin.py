from django.contrib import admin
from .models import OrdinaryCashier, ExchangeActions, AdministratorCashCosts

admin.site.register([OrdinaryCashier, ExchangeActions, AdministratorCashCosts])
# Register your models here.
