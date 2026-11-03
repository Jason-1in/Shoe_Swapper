from django.contrib import admin

# Register your models here.
from .models import Shoe, SwapRequest

admin.site.register(Shoe)
admin.site.register(SwapRequest)
