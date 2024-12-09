
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render

from rest_framework import status, authentication, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Order, OrderItem
from .serializers import *
from datetime import timedelta,date
import datetime
from rest_framework import generics
from django.utils import timezone

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import *
from django.conf import settings

from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid
import logging
from paystackapi.transaction import Transaction
from decimal import Decimal

# Create your views here.
logger = logging.getLogger(__name__)

##sed mail custom function
def send_email(subject,body,recipient, receiver):
    site = 'Paygo NG'
    name = "Paygo NG"
    phone_number = "2348115333313"
    email = "kwickng@Paygo.ng"
    now = datetime.now(timezone.utc) + timedelta(hours=1)
    # Format the date and time as a string
    formatted_date = now.strftime('%d %B, %Y by %I%p')
    context ={
        "title": subject,
        "content":body,
        "receiver": receiver,
        "name": name,
        "phone_number":phone_number,
        "email": email,
        'date': formatted_date

        }
    html_content = render_to_string("emails.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER ,
        [recipient]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()



# @api_view(['POST'])
# def checkout(request):
#     serializer = OrderSerializer(data=request.data)
#     if serializer.is_valid():
#         # Save the order instance with the user and paid amount
#         order = serializer.save()
        
#         # Extract email from the order instance or serializer data
#         email = order.email
#         fullname = order.full_name
#         address = order.address
#         order_number = order.order_number
#         paid_amount = order.paid_amount
        
#         ##email conf
#         subject = 'Paygo NG Order Confirmation'
#         message = f"""
#         Your order from Paygo NG with order number [{order_number}], shipping to
#         [{address}] of a total amount of [{paid_amount}] has been received, and is being attended to,
#         we'll let you know, once order is shipped.
        
#         Thanks for your patronage !!
        
#         """
#         send_email(subject, message, email, fullname)
#         # Return the order data
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#     # Return errors if the data is not valid
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class OrdersList(APIView):
#     authentication_classes = [authentication.BasicAuthentication]
#     ## in production
#     ##  authentication_classes = [authentication.TokenAuthentication]

#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):
#         orders = Order.objects.all()
#         serializer = MyOrderSerializer(orders, many=True)
#         return Response(serializer.data)
    
    
# class OrderCreateView(CreateAPIView):
#     serializer_class = OrderCreateSerializer
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Create an order and initialize payment",
#         request_body=OrderCreateSerializer,
#         responses={
#             201: openapi.Response(
#                 description="Order created successfully",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'order': OrderDetailSerializer,
#                         'payment_url': openapi.Schema(
#                             type=openapi.TYPE_STRING,
#                             description='Paystack payment URL'
#                         )
#                     }
#                 )
#             )
#         }
#     )
#     def create(self, request, *args, **kwargs):
#         try:
#             with transaction.atomic():
#                 # Create order and items
#                 serializer = self.get_serializer(data=request.data)
#                 serializer.is_valid(raise_exception=True)
#                 order = serializer.save(user=request.user)

#                 # Initialize Paystack payment
#                 reference = str(uuid.uuid4())
#                 transaction = Transaction.initialize(
#                     reference=reference,
#                     amount=int(order.paid_amount * 100),  # Convert to kobo
#                     email=order.email,
#                 )

#                 if not transaction['status']:
#                     raise Exception('Failed to initialize payment')

#                 # Update order with payment reference
#                 order.payment_reference = reference
#                 order.save()

#                 # Create transaction history
#                 TransactionHistory.objects.create(
#                     profile=request.user,
#                     action=f"Order #{order.order_number} payment initiated: NGN {order.paid_amount}",
#                     action_title="Order Payment Initiated",
#                     category="Order"
#                 )

#                 # Send email notification
#                 subject = "Paygo NG Order Confirmation"
#                 message = f"""
#                 Order #{order.order_number} has been created.
                
#                 Order Details:
#                 Name: {order.full_name}
#                 Address: {order.address}, {order.lga}, {order.state}
#                 Insurance Type: {order.insurance_type}
#                 Amount: NGN {order.paid_amount}

#                 Please complete your payment using the payment link provided.
#                 Your order will be processed once payment is confirmed.
#                 """
#                 send_email(
#                     subject=subject,
#                     body=message,
#                     recipient=order.email,
#                     receiver=order.full_name
#                 )

#                 # Return response with order details and payment URL
#                 return Response({
#                     'order': OrderDetailSerializer(order).data,
#                     'payment_url': transaction['data']['authorization_url']
#                 }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             logger.error(f"Order creation error: {str(e)}")
#             return Response(
#                 {'error': 'Failed to create order'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# class OrderListView(ListAPIView):
#     serializer_class = OrderDetailSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Order.objects.filter(user=self.request.user)

# class OrderDetailView(RetrieveAPIView):
#     serializer_class = OrderDetailSerializer
#     permission_classes = [IsAuthenticated]
#     lookup_field = 'order_number'

#     def get_queryset(self):
#         return Order.objects.filter(user=self.request.user)



class OrderCreateView(CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create an order and initialize payment",
        request_body=OrderCreateSerializer,
        responses={
            201: openapi.Response(
                description="Order created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'order': OrderDetailSerializer,
                        'payment_url': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Paystack payment URL'
                        )
                    }
                )
            )
        }
    )
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Create order and items
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                order = serializer.save(user=request.user)

                # Ensure we're working with Decimal
                base_amount = Decimal(str(order.paid_amount))
                service_charge = base_amount * Decimal('0.05')

                # Calculate total
                total_amount = base_amount + service_charge

                # Round all amounts
                base_amount = base_amount.quantize(Decimal('0.01'))
                service_charge = service_charge.quantize(Decimal('0.01'))
                total_amount = total_amount.quantize(Decimal('0.01'))

                # Initialize Paystack payment
                reference = str(uuid.uuid4())
                paystack_amount = int(total_amount * Decimal('100'))

                paystack_transaction = Transaction.initialize(
                    reference=reference,
                    amount=paystack_amount,
                    email=order.email,
                )

                if not paystack_transaction['status']:
                    raise Exception('Failed to initialize payment')

                # Update order
                order.payment_reference = reference
                order.order_number = reference
                order.paid_amount = total_amount
                order.save()

                # Create transaction history
                TransactionHistory.objects.create(
                    user=request.user,
                    type='order_payment',
                    amount=str(total_amount),
                    status='pending',
                    method='paystack'
                )

                # Send email notification
                subject = "Paygo NG Order Confirmation"
                message = f"""
                Order #{order.order_number} has been created.
                
                Order Details:
                Name: {order.full_name}
                Address: {order.address}, {order.lga}, {order.state}
                Insurance Type: {order.insurance_type}
                
                Payment Breakdown:
                Base Amount: NGN {base_amount:,.2f}
                Service Charge (5%): NGN {service_charge:,.2f}
                Total Amount: NGN {total_amount:,.2f}

                Please complete your payment using this payment link provided
                : {paystack_transaction['data']['authorization_url']}
                Your order will be processed once payment is confirmed.
                """
                
                send_email(
                    subject=subject,
                    body=message,
                    recipient=order.email,
                    receiver=order.full_name
                )

                return Response({
                    'order': OrderDetailSerializer(order).data,
                    'payment_breakdown': {
                        'base_amount': str(base_amount),
                        'service_charge': str(service_charge),
                        'total_amount': str(total_amount)
                    },
                    'payment_url': paystack_transaction['data']['authorization_url']
                }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.error(f"Value Error in order creation: {str(e)}")
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Order creation error: {str(e)}")
            return Response(
                {'error': 'Failed to create order', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OrderListView(ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class TransactionHistoryListView(generics.ListAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List user's transaction history with optional filtering",
        manual_parameters=[
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="Filter by transaction type",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by transaction status",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'method',
                openapi.IN_QUERY,
                description="Filter by payment method",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description="Filter by last X days",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
        ],
        responses={
            200: TransactionHistorySerializer(many=True),
            401: 'Unauthorized'
        },
        tags=['Transactions']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = TransactionHistory.objects.filter(user=self.request.user)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(type__iexact=transaction_type)

        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status__iexact=status)

        # Filter by payment method
        method = self.request.query_params.get('method')
        if method:
            queryset = queryset.filter(method__iexact=method)

        # Filter by last X days
        days = self.request.query_params.get('days')
        if days:
            try:
                days = int(days)
                date_threshold = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(time__gte=date_threshold)
            except ValueError:
                pass

        return queryset.order_by('-time')

class TransactionHistoryDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific transaction",
        responses={
            200: TransactionHistorySerializer(),
            404: 'Not Found',
            401: 'Unauthorized'
        },
        tags=['Transactions']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return TransactionHistory.objects.filter(user=self.request.user)

class UserDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user's dashboard data including profile and recent transactions",
        responses={
            200: openapi.Response(
                description="User dashboard data retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'recent_transactions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'amount': openapi.Schema(type=openapi.TYPE_STRING),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                                    'method': openapi.Schema(type=openapi.TYPE_STRING),
                                    'time': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            401: "Unauthorized"
        },
        tags=['User Dashboard']
    )
    def get(self, request):
        try:
            serializer = UserDashboardSerializer(request.user)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {str(e)}")
            return Response(
                {'error': 'Failed to fetch dashboard data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Verify pending payment status",
        manual_parameters=[
            openapi.Parameter(
                'reference',  # This matches the URL parameter name
                openapi.IN_QUERY,
                description="Payment reference to verify",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Payment verified successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Payment verified successfully",
                        "data": {
                            "amount": "5000.00",
                            "status": "success"
                        }
                    }
                }
            ),
            400: "Bad Request",
            404: "Payment not found"
        },
        tags=['Payments']
    )
    def get(self, request):
        reference = request.query_params.get('reference')  # Changed from payment_reference to reference
        
        if not reference:
            return Response(
                {'error': 'Reference is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Changed from Payment to Order
            order = Order.objects.get(payment_reference=reference)
            
            # Verify Paystack transaction
            response = Transaction.verify(reference)
            
            if not response['status']:
                return Response({
                    'error': 'Unable to verify payment'
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                paystack_status = response['data']['status']
                
                if paystack_status == 'success':
                    # Update order payment status
                    order.payment_status = 'paid'  # Assuming you have this field in Order model
                    order.save()

                    # Create transaction history
                    TransactionHistory.objects.create(
                        user=request.user,
                        type='payment_verification',
                        amount=str(order.paid_amount),
                        status='success',
                        method='paystack'
                    )

                    # Send success email
                    subject = "Payment Successful - Paygo NG"
                    message = f"""
                    Your payment of NGN {order.paid_amount} has been verified successfully.
                    
                    Transaction Reference: {reference}
                    Amount: NGN {order.paid_amount}
                    Status: Successful
                    
                    Thank you for choosing Paygo NG!
                    """
                    
                    send_email(
                        subject=subject,
                        body=message,
                        recipient=order.email,
                        receiver=order.full_name
                    )

                    return Response({
                        'status': 'success',
                        'message': 'Payment verified successfully',
                        'data': {
                            'amount': str(order.paid_amount),
                            'status': 'success'
                        }
                    })
                else:
                    # Update order payment status to failed
                    order.payment_status = 'failed'
                    order.save()
                    
                    # Create failed transaction record
                    TransactionHistory.objects.create(
                        user=request.user,
                        type='payment_verification',
                        amount=str(order.paid_amount),
                        status='failed',
                        method='paystack'
                    )

                    return Response({
                        'status': 'failed',
                        'message': 'Payment verification failed',
                        'data': {
                            'amount': str(order.paid_amount),
                            'status': 'failed'
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:  # Changed from Payment to Order
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return Response(
                {'error': 'Failed to verify payment'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )