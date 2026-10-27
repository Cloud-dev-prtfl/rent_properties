import pytest
from django.conf import settings
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    admin = User.objects.create_superuser("admin@example.com", "admin-pass-123")
    client.force_login(admin)
    return client


def test_admin_is_not_mounted_at_default_path(client):
    assert settings.ADMIN_URL_PREFIX == "ops/admin/"
    assert client.get("/admin/").status_code == 404


@pytest.mark.parametrize("name", ["admin:accounts_user_changelist", "admin:accounts_user_add"])
def test_user_admin_pages_load(admin_client, name):
    assert admin_client.get(reverse(name)).status_code == 200


def test_user_admin_change_page_loads(admin_client):
    user = UserFactory()
    url = reverse("admin:accounts_user_change", args=[user.pk])
    response = admin_client.get(url)
    assert response.status_code == 200
    assert str(user.public_id) in response.content.decode()
