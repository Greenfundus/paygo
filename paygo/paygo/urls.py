from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Paygo RESTAPI",
        default_version='v1',
        description="API documentation for Store management system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@paygo.com.ng"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/v1/auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),
    path('api/v1/', include('product.urls')),
    # path('accounts/password_reset/email/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/v1/', include('order.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



urlpatterns += [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), 
         name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
]
