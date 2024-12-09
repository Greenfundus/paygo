from django.urls import path, include

from product import views

urlpatterns = [
    
    ## product views
    path('products/', views.Products.as_view()),
    path('products/search/', views.ProductSearchView.as_view(), name='product-search'),
    path('product/<str:identifier>/', views.Product_.as_view(), name='product'),

    ## categories views
    path('category/', views.Categorys.as_view()),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),

    ##communities
    path('communities/', views.CommunityListCreateView.as_view(), name='community-list-create'),
    path('communities/<slug:slug>/', views.CommunityDetailView.as_view(), name='community-detail'),


    path('insurers/', views.StoreList.as_view(), name='store-list'),
    path('insurers/<slug:slug>/', views.StoreDetail.as_view(), name='store-detail'),
    path('insurers/<slug:store_slug>/categories/', views.StoreCategoryList.as_view(), name='store-category-list'),
    path('insurers/<slug:store_slug>/categories/<slug:category_slug>/', views.StoreCategoryDetail.as_view(), name='store-category-detail'),
    path('insurers/<slug:store_slug>/products/', views.StoreProductList.as_view(), name='store-product-list'),

    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/request-password-reset-email/', views.RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('auth/reset-password/protected/', views.ProtectedResetPasswordAPIView.as_view(), name='reset-password'),
    path('auth/reset-password/confirm', views.custom_password_reset_confirm, name='password_reset_confirm'),

    path('profile/', views.UserProfileView.as_view(), name='user-profile'),

]