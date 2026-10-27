from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-created_at",)
    list_display = ("public_id", "email", "status", "is_staff", "created_at")
    list_filter = ("status", "is_staff", "is_superuser")
    search_fields = ("email", "public_id")
    readonly_fields = ("public_id", "created_at", "updated_at", "last_login", "verified_at")
    fieldsets = (
        (None, {"fields": ("public_id", "email", "password")}),
        (_("Profile"), {"fields": ("full_name",)}),
        (
            _("Status"),
            {"fields": ("status", "status_reason", "verified_at", "verification_method")},
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (_("Dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)
