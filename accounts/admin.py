from django.contrib import admin
from .models import PhoneNumber, PhoneOTP


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'user', 'verified_at')
    search_fields = ('number', 'user__first_name')


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    # code_hash intentionally hidden; plain codes are never stored.
    list_display = ('number', 'purpose', 'created_at', 'expires_at', 'attempts', 'is_used')
    exclude = ('code_hash',)
    list_filter = ('purpose', 'is_used')
