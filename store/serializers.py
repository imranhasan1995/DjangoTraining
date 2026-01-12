import datetime
from rest_framework import serializers
from .models import Address, Customer, Order

class CustomerSerializer(serializers.ModelSerializer):
    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone must contain only digits.")
        if len(value) < 10:
            raise serializers.ValidationError("Phone must be at least 10 digits.")
        return value
    
    def validate(self, data):
        birth_date = data.get('birth_date')

        if birth_date and birth_date > datetime.date.today():
            raise serializers.ValidationError({
                "birth_date": "Birth date cannot be in the future."
            })

        return data

    last_name = serializers.CharField(write_only=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    class Meta:
        model = Order
        fields = ['id', 'customer', 'payment_status', 'payment_status']

class AddressSerializer(serializers.ModelSerializer):
    # Nested read-only customer info
    customer = CustomerSerializer(read_only=True)
    # For POST/PUT, accept customer ID
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), write_only=True, source='customer'
    )

    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'zip', 'customer', 'customer_id']