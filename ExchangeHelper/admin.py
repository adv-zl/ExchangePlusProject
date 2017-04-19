from django.contrib import admin
from .models import OrdinaryCashier, ExchangeActions

admin.site.register([OrdinaryCashier, ExchangeActions])
# Register your models here.
