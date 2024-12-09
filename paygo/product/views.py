from django.db.models import Q
from django.http import Http404
from rest_framework import status,generics

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from datetime import timedelta

from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser

from drf_yasg import openapi
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.db import models

from .models import *
from .serializers import *

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.html import strip_tags


class RegisterView(APIView):
    """
    Register a new user with email and password
    """
    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'username'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description='User email address'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description='User password',
                    min_length=8
                ),
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User\'s full name',
                    min_length=2
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Successfully registered",
                examples={
                    "application/json": {
                        "token": "93144b288eb1fdccbe46d6fc0f241a51766ecd3d",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "John Doe"
                        }
                    }
                },
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "Email already registered"
                    }
                }
            )
        },
        operation_summary="Register New User",
        tags=['Authentication']
    )
    def post(self, request):
        data = request.data
        if User.objects.filter(email=data.get('email')).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
        )
        
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """
    Login user and return authentication token
    """
    @swagger_auto_schema(
        operation_description="Login with email and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description='User email address'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description='User password'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successfully logged in",
                examples={
                    "application/json": {
                        "token": "93144b288eb1fdccbe46d6fc0f241a51766ecd3d",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "John Doe"
                        }
                    }
                },
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: openapi.Response(
                description="Authentication failed",
                examples={
                    "application/json": {
                        "error": "Invalid credentials"
                    }
                }
            )
        },
        operation_summary="User Login",
        tags=['Authentication']
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Please provide both email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request=request, email=email, password=password)
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
            
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class ProtectedResetPasswordAPIView(APIView):
    """
    API View to reset password for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Reset password using token from email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['password', 'confirm_password'],
            properties={
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description='New password',
                    min_length=8
                ),
                'confirm_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description='New password',
                    min_length=8
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Password reset successful",
                examples={
                    "application/json": {
                        "message": "Password reset successful"
                    }
                }
            ),
            400: openapi.Response(
                description="Errors Beyond control occured",
                examples={
                    "application/json": {
                        "error": "Errors Beyond control occured"
                    }
                }
            )
        },
        operation_summary="Reset Password",
        tags=['Authentication']
    )
    def put(self, request, *args, **kwargs):
        # Extract the new password from the request
        new_password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({'error': 'Password and confirm password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the password
        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user = request.user
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)


class RequestPasswordResetView(APIView):
    """
    Send password reset email to user
    """
    @swagger_auto_schema(
        operation_description="Request a password reset email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description='Email address of the user'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Email sent successfully",
                examples={
                    "application/json": {
                        "message": "Password reset email has been sent."
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                        "error": "No user found with this email address."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "Invalid request method."
                    }
                }
            )
        },
        operation_summary="Request Password Reset Email",
        tags=['Authentication']
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            
            # Create password reset token
            reset_token = PasswordReset.objects.create(user=user)
            
            # Build reset URL
            reset_url = f"{settings.SITE_URL}/api/v1/auth/reset-password/confirm?token={reset_token.token}"
            
            # Create HTML email content
            html_message = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello {user.username},</p>
                <p>You have requested to reset your password. Click the link below:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>If you didn't request this, please ignore this email.</p>
                <p>This link will expire in 24 hours.</p>
            </body>
            </html>
            """
            
            # Create plain text version
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject='Password Reset Request',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset email has been sent.'
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'No user found with this email address.'},
                status=status.HTTP_404_NOT_FOUND
            )


@csrf_exempt
def custom_password_reset_confirm(request):
    token = request.GET.get('token')  # Extract token from the URL
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not password or not confirm_password:
            return render(request, 'password_reset/password_reset_confirm.html', {
                'token': token,
                'error': "Both passwords are required."
            })
            
        if password != confirm_password:
            return render(request, 'password_reset/password_reset_confirm.html', {
                'token': token,
                'error': "Passwords do not match."
            })
            
        # Retrieve the token from the database
        try:
            reset_token = PasswordReset.objects.get(
                token=token,  # Changed from key to token
                used=False,
                created_at__gte=timezone.now() - timedelta(hours=24)  # Check if token is not expired
            )
            
            user = reset_token.user  # Get the associated user
            
            # Set the new password
            user.set_password(password)
            user.save()
            
            # Mark token as used
            reset_token.used = True
            reset_token.save()
            
            return render(request, 'password_reset/password_reset_success.html')
            
        except PasswordReset.DoesNotExist:
            return render(request, 'password_reset/password_reset_confirm.html', {
                'error': "Invalid or expired token."
            })
    
    # If GET request, just show the form
    return render(request, 'password_reset/password_reset_confirm.html', {'token': token})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Get user profile details",
        responses={
            200: UserProfileSerializer(),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            )
        },
        tags=['Profile']
    )
    def get(self, request):
        user_serializer = UserSerializer(request.user)
        profile_serializer = UserProfileSerializer(request.user.profile)
        
        return Response({
            'user': user_serializer.data,
            'profile': profile_serializer.data
        })

    @swagger_auto_schema(
        operation_description="Update user profile",
        manual_parameters=[
            openapi.Parameter(
                'profile_photo',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='Profile photo file',
                required=False
            ),
            openapi.Parameter(
                'location',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='User location',
                required=False
            ),
            openapi.Parameter(
                'farm_location',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='Farm location',
                required=False
            ),
            openapi.Parameter(
                'phone_number',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='Phone number',
                required=False
            )
        ],
        responses={
            200: UserProfileSerializer(),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Invalid data provided"
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            )
        },
        tags=['Profile']
    )
    def put(self, request):
        serializer = UserProfileSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Partially update user profile",
        manual_parameters=[
            openapi.Parameter(
                'profile_photo',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='Profile photo file',
                required=False
            ),
            openapi.Parameter(
                'location',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='User location',
                required=False
            ),
            openapi.Parameter(
                'farm_location',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='Farm location',
                required=False
            ),
            openapi.Parameter(
                'phone_number',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='Phone number',
                required=False
            )
        ],
        responses={
            200: UserProfileSerializer(),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Invalid data provided"
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            )
        },
        tags=['Profile']
    )
    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreList(APIView):
    """
    List all stores or create a new store
    """
    @swagger_auto_schema(
        operation_description="List all stores",
        responses={200: StoreSerializer(many=True)}
    )
    def get(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new store",
        request_body=StoreSerializer,
        responses={201: StoreSerializer()}
    )
    def post(self, request):
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StoreDetail(APIView):
    """
    Retrieve, update or delete a store instance
    """
    def get_object(self, slug):
        return get_object_or_404(Store, slug=slug)

    @swagger_auto_schema(
        operation_description="Get store details",
        responses={200: StoreDetailSerializer()}
    )
    def get(self, request, slug):
        store = self.get_object(slug)
        serializer = StoreDetailSerializer(store)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update store details",
        request_body=StoreSerializer,
        responses={200: StoreSerializer()}
    )
    def put(self, request, slug):
        store = self.get_object(slug)
        serializer = StoreSerializer(store, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a store",
        responses={204: "No Content"}
    )
    def delete(self, request, slug):
        store = self.get_object(slug)
        store.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class StoreCategoryList(APIView):
    """
    List all categories in a store
    """
    @swagger_auto_schema(
        operation_description="List all categories in a store",
        responses={200: StoreCategorySerializer(many=True)}
    )
    def get(self, request, store_slug):
        store = get_object_or_404(Store, slug=store_slug)
        categories = Category.objects.filter(store=store)
        serializer = StoreCategorySerializer(categories, many=True)
        return Response(serializer.data)

class StoreCategoryDetail(APIView):
    """
    Retrieve category details with all its products
    """
    @swagger_auto_schema(
        operation_description="Get category details with products",
        responses={200: CategorySerializer()}
    )
    def get(self, request, store_slug, category_slug):
        store = get_object_or_404(Store, slug=store_slug)
        category = get_object_or_404(Category, store=store, slug=category_slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

class StoreProductList(APIView):
    """
    List all products in a store
    """
    @swagger_auto_schema(
        operation_description="List all products in a store",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, store_slug):
        store = get_object_or_404(Store, slug=store_slug)
        products = Product.objects.filter(category__store=store)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


"""
    ## List all products in our store, and also creates
"""
class Products(APIView):
        def get(self, request, format=None):
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        
        def post(self, request, format=None):
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductSearchView(APIView):
    """
    Search for products by name or description
    """
    @swagger_auto_schema(
        operation_description="Search products by name or description",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['query'],
            properties={
                'query': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Search term for product name or description'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Search results",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'products': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'get_absolute_url': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                    'price': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'get_image': openapi.Schema(type=openapi.TYPE_STRING),
                                    'get_thumbnail': openapi.Schema(type=openapi.TYPE_STRING),
                                    'stock_quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'category_name': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        ),
                        'count': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Number of products found'
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                        'products': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "error": "Search query is required",
                        "products": []
                    }
                }
            )
        },
        operation_summary="Search Products",
        tags=['Products']
    )
    def post(self, request):
        query = request.data.get('query', '')
        
        if not query:
            return Response(
                {
                    "error": "Search query is required",
                    "products": []
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

        if not products.exists():
            return Response({
                "products": [],
                "message": "No products found matching your search"
            })

        serializer = ProductSerializer(products, many=True)
        return Response({
            "products": serializer.data,
            "count": products.count()
        })

class Product_(APIView):
        def get_object(self, identifier):
            try:
                # Check if identifier is a digit, then it's a PK; else, it's a slug
                if identifier.isdigit():
                    return Product.objects.get(pk=identifier)
                else:
                    return Product.objects.get(slug=identifier)
            except Product.DoesNotExist:
                raise Http404

        def get(self, request, identifier, format=None):
            product = self.get_object(identifier)
            serializer = ProductSerializer(product)
            return Response(serializer.data)

        def put(self, request, identifier, format=None):
            product = self.get_object(identifier)
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, identifier, format=None):
            product = self.get_object(identifier)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    ## Categories related views

class Categorys(APIView):
        def get(self, request, format=None):
            category = Category.objects.all()
            serializer = CategorySerializer(category, many=True)
            return Response(serializer.data)

class CategoryDetailView(APIView):
        def get(self, request, slug=None, format=None):
            # Filter category based on the slug obtained from the URL
            category = Category.objects.filter(slug=slug) if slug else Category.objects.all()
            serializer = CategorySerializer(category, many=True)
            return Response(serializer.data)
            
class CommunityListCreateView(generics.ListCreateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all communities",
        manual_parameters=[
            openapi.Parameter(
                'sector',
                openapi.IN_QUERY,
                description="Filter by sector",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'location',
                openapi.IN_QUERY,
                description="Filter by location",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of communities",
                schema=CommunitySerializer(many=True)
            ),
            401: 'Unauthorized'
        },
        tags=['Communities']
    )
    def get(self, request, *args, **kwargs):
        sector = request.query_params.get('sector')
        location = request.query_params.get('location')
        
        queryset = self.get_queryset()
        
        if sector:
            queryset = queryset.filter(sector__icontains=sector)
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new community",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Community name'
                ),
                'image': openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description='Community image'
                ),
                'website_url': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Community website URL'
                ),
                'location': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Community location'
                ),
                'sector': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Community sector'
                ),
            },
            required=['name', 'location', 'sector']
        ),
        responses={
            201: openapi.Response(
                description="Community created successfully",
                schema=CommunitySerializer()
            ),
            400: 'Bad Request',
            401: 'Unauthorized'
        },
        tags=['Communities']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

class CommunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    @swagger_auto_schema(
        operation_description="Retrieve a community by slug",
        responses={
            200: CommunitySerializer(),
            404: 'Not Found',
            401: 'Unauthorized'
        },
        tags=['Communities']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a community",
        request_body=CommunitySerializer,
        responses={
            200: CommunitySerializer(),
            400: 'Bad Request',
            404: 'Not Found',
            401: 'Unauthorized'
        },
        tags=['Communities']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a community",
        request_body=CommunitySerializer,
        responses={
            200: CommunitySerializer(),
            400: 'Bad Request',
            404: 'Not Found',
            401: 'Unauthorized'
        },
        tags=['Communities']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a community",
        responses={
            204: 'No Content',
            404: 'Not Found',
            401: 'Unauthorized'
        },
        tags=['Communities']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)



# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout user and invalidate token",
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                examples={
                    "application/json": {
                        "message": "Successfully logged out."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            )
        },
        operation_summary="User Logout",
        tags=['Authentication']
    )
    def post(self, request):
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Something went wrong while logging out."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

