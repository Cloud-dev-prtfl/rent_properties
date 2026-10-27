from django.db import models
from django.utils.translation import gettext_lazy as _


class UserStatus(models.TextChoices):
    UNVERIFIED = "UNVERIFIED", _("Unverified")
    ACTIVE = "ACTIVE", _("Active")
    SUSPENDED = "SUSPENDED", _("Suspended")
    DELETED = "DELETED", _("Deleted")


class VerificationMethod(models.TextChoices):
    EMAIL = "EMAIL", _("Email")
    PHONE = "PHONE", _("Phone")
    SOCIAL = "SOCIAL", _("Social sign-in")


# Statuses in which the account may log in (is_active must agree, enforced by a CHECK).
ACTIVE_STATUSES = (UserStatus.UNVERIFIED, UserStatus.ACTIVE)
