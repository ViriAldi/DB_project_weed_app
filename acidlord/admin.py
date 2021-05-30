from django.contrib import admin

from .models import *

admin.site.register(Customer)
admin.site.register(Agronom)
admin.site.register(Strain)
admin.site.register(ShoppingCart)
admin.site.register(Order)
admin.site.register(Harvest)
admin.site.register(Harvest2Cart)