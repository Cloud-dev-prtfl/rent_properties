import factory
from django.utils import timezone

from apps.accounts.enums import UserStatus, VerificationMethod
from apps.accounts.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Faker("name")
    password = factory.PostGenerationMethodCall("set_password", "correct-horse-battery")

    @factory.post_generation
    def _save_password(obj: User, create: bool, *_args: object, **_kwargs: object) -> None:  # noqa: N805
        if create:
            obj.save(update_fields=["password"])


class VerifiedUserFactory(UserFactory):
    status = UserStatus.ACTIVE
    verified_at = factory.LazyFunction(timezone.now)
    verification_method = VerificationMethod.EMAIL


class StaffUserFactory(VerifiedUserFactory):
    is_staff = True
