from django.contrib import admin
from .models import OutputImage, User


# class OutputImageAdmin(admin.ModelAdmin):
#   list_display = (
#     "name",
#     "category",
#     "sex",
#     "rating",
#     "currency",
#     "price",
#   )

admin.site.register(User)
# admin.site.register(OutputImage, OutputImageAdmin)
