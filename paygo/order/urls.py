from django.urls import path

from order import views

urlpatterns = [
    # path('checkout/', views.checkout),
    # path('orders/', views.OrdersList.as_view()),  
    path('orders/create/', views.OrderCreateView.as_view(), name='create-order'),
    path('orders/', views.OrderListView.as_view(), name='order-list'), 
    path('orders/<int:id>/', views.OrderDetailView.as_view(), name='order-list'),
    path('orders/transactions/', 
         views.TransactionHistoryListView.as_view(), 
         name='transaction-history-list'),
    path('orders/transactions/<int:id>/', 
         views.TransactionHistoryDetailView.as_view(), 
         name='transaction-history-detail'),
    path('payments/verify/', views.PaymentVerificationView.as_view(), name='verify-payment'),

    ## dashboard
    path('dashboard/', views.UserDashboardView.as_view(), name='user-dashboard'),


]