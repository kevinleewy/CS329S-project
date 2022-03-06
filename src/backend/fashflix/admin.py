from django.contrib import admin
from .models import OutputImage


class OutputImageAdmin(admin.ModelAdmin):
  list_display = (
    "name",
    "category",
    "sex",
    "rating",
    "currency",
    "price",
  )

admin.site.register(OutputImage, OutputImageAdmin)
