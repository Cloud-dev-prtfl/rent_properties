"""User model (docs/design/01-domain-model.md §3.1).

Phone fields arrive in M1 together with field-level encryption.
"""

from typing import Any, ClassVar

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.enums import ACTIVE_STATUSES, UserStatus, VerificationMethod
from apps.core.models import PublicIdModel, TimeStampedModel


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email: str | None) -> str:
        # Emails are stored fully lower-cased, so case-insensitive uniqueness needs one index.
        return (email or "").strip().lower()

    def get_by_natural_key(self, username: str | None) -> "User":
        return self.get(email=self.normalize_email(username))

    def create_user(self, email: str, password: str | None = None, **extra: Any) -> "User":
        if not email:
            raise ValueError("An email address is required.")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra: Any) -> "User":
        extra.update(
            is_staff=True,
            is_superuser=True,
            status=UserStatus.ACTIVE,
            verified_at=timezone.now(),
            verification_method=VerificationMethod.EMAIL,
        )
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin, PublicIdModel, TimeStampedModel):
    email = models.EmailField(_("email address"), max_length=254)
    full_name = models.CharField(_("full name"), max_length=150, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    status = models.CharField(
        max_length=12, choices=UserStatus.choices, default=UserStatus.UNVERIFIED
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_method = models.CharField(
        max_length=10, choices=VerificationMethod.choices, null=True, blank=True
    )
    status_reason = models.CharField(max_length=40, null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        constraints: ClassVar = [
            # Stored lower-case + plain unique index = case-insensitive uniqueness that exact
            # lookups can use (refines the lower(email) index in the domain model, register R-22).
            models.UniqueConstraint(fields=["email"], name="uq_user_email"),
            models.CheckConstraint(
                condition=Q(email=Lower("email")), name="ck_user_email_lowercase"
            ),
            models.CheckConstraint(
                condition=Q(status__in=UserStatus.values), name="ck_user_status_valid"
            ),
            models.CheckConstraint(
                condition=Q(verification_method__isnull=True)
                | Q(verification_method__in=VerificationMethod.values),
                name="ck_user_verification_method_valid",
            ),
            models.CheckConstraint(
                condition=Q(is_active=True, status__in=ACTIVE_STATUSES)
                | (Q(is_active=False) & ~Q(status__in=ACTIVE_STATUSES)),
                name="ck_user_active_matches_status",
            ),
            models.CheckConstraint(
                condition=Q(status__in=[UserStatus.UNVERIFIED, UserStatus.DELETED])
                | Q(verified_at__isnull=False),
                name="ck_user_verified_stamp",
            ),
        ]
        indexes: ClassVar = [
            models.Index(
                fields=["created_at"],
                name="ix_user_unverified_created",
                condition=Q(status=UserStatus.UNVERIFIED),
            ),
        ]

    def __str__(self) -> str:
        return str(self.public_id)

    def clean(self) -> None:
        super().clean()
        self.email = type(self).objects.normalize_email(self.email)

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None
