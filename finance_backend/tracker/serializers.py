from rest_framework import serializers
from .models import User, Catagory, Expense, Budget
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'email', 'first_name', 'last_name', 'username']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        return user
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True,style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            data['user'] = user
        else:
            raise serializers.ValidationError("Must include email and password")
        
        return data

class CatagorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Catagory
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = ['id', 'category', 'category_name', 'amount', 'description', 'date']
        read_only_fields = ['date']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_name', 'amount', 'period', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)