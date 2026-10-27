import pytest
from django.db import IntegrityError, transaction

from apps.accounts.enums import UserStatus, VerificationMethod
from apps.accounts.models import User
from apps.accounts.tests.factories import UserFactory, VerifiedUserFactory

pytestmark = pytest.mark.django_db


def test_create_user_normalises_email_to_lower_case():
    user = User.objects.create_user("  Jane.Doe@Example.COM ", "s3cure-passphrase")
    assert user.email == "jane.doe@example.com"
    assert user.check_password("s3cure-passphrase")


def test_new_user_starts_unverified_with_public_id():
    user = UserFactory()
    assert user.status == UserStatus.UNVERIFIED
    assert user.is_active is True
    assert user.is_verified is False
    assert str(user) == str(user.public_id)


def test_create_user_requires_email():
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user("", "pw")


def test_create_superuser_is_active_and_verified():
    admin = User.objects.create_superuser("root@example.com", "pw-for-admin-123")
    assert admin.is_staff
    assert admin.is_superuser
    assert admin.status == UserStatus.ACTIVE
    assert admin.verification_method == VerificationMethod.EMAIL
    assert admin.is_verified


def test_login_lookup_is_case_insensitive():
    user = UserFactory(email="mixed@example.com")
    assert User.objects.get_by_natural_key("MIXED@Example.com") == user


def test_email_is_unique_regardless_of_case():
    User.objects.create_user("dup@example.com", "pw")
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user("DUP@example.com", "pw")


def test_database_rejects_upper_case_email_written_directly():
    user = UserFactory()
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(email="Upper@Example.com")


def test_clean_normalises_email():
    user = User(email="Clean@Example.COM")
    user.clean()
    assert user.email == "clean@example.com"


@pytest.mark.parametrize(
    ("status", "is_active"),
    [(UserStatus.SUSPENDED, True), (UserStatus.ACTIVE, False), (UserStatus.UNVERIFIED, False)],
)
def test_is_active_must_match_status(status, is_active):
    user = VerifiedUserFactory()
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(status=status, is_active=is_active)


def test_active_status_requires_verified_timestamp():
    user = UserFactory()
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(status=UserStatus.ACTIVE)


def test_suspended_user_with_inactive_flag_is_valid():
    user = VerifiedUserFactory()
    User.objects.filter(pk=user.pk).update(status=UserStatus.SUSPENDED, is_active=False)
    user.refresh_from_db()
    assert user.status == UserStatus.SUSPENDED
