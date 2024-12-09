from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    def get_category_name(self, obj):
            return obj.category.name if obj.category else None
    category_name = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "get_absolute_url",
            "description",
            "price",
            "get_image",
            "get_thumbnail",
            "stock_quantity",
            'category_name',
        )

        
class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "insurance_type",
            "get_absolute_url",
            "image",
            "products",
        )


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'name', 'slug', 'description', 'logo', 'address', 
                 'phone', 'email', 'get_absolute_url', 'created_at')

class StoreCategorySerializer(serializers.ModelSerializer):
    store = StoreSerializer()
    products_count = serializers.SerializerMethodField()

    def get_products_count(self, obj):
        return obj.products.count()

    class Meta:
        model = Category
        fields = ('id', 'store', 'name', 'slug', 'image', 'get_absolute_url', 
                 'products_count')

class StoreDetailSerializer(serializers.ModelSerializer):
    categories = StoreCategorySerializer(many=True, read_only=True)
    products_count = serializers.SerializerMethodField()

    def get_products_count(self, obj):
        return Product.objects.filter(category__store=obj).count()

    class Meta:
        model = Store
        fields = ('id', 'name', 'slug', 'description', 'logo', 'address', 
                 'phone', 'email', 'get_absolute_url', 'created_at', 
                 'categories', 'products_count')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')
        extra_kwargs = {'password': {'write_only': True}}

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class CommunitySerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    admin_name = serializers.CharField(source='admin.username', read_only=True)

    class Meta:
        model = Community
        fields = [
            'id', 'name', 'slug', 'image', 'website_url',
            'admin', 'admin_email', 'admin_name',
            'location', 'sector', 'created_at'
        ]
        read_only_fields = ['slug', 'created_at']
      