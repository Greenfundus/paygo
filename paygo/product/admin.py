from django.contrib import admin

from .models import *

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Store)
admin.site.register(UserProfile)
admin.site.register(PasswordReset)
admin.site.register(Community)