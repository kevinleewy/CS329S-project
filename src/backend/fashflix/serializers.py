from rest_framework import serializers
from .models import OutputImage

class OutputImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutputImage
        fields = ("name", "category", "sex", "rating", "currency", "price")
