import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


def catalog_path():
  return os.path.join(settings.CATALOG_DIR, "catalog")

class OutputImage(models.Model):
  name = models.CharField(max_length=120)
  path = models.TextField(blank=True, null=True) #models.FilePathField(blank=True, null=True, path=settings.CATALOG_DIR, match=".*", recursive=True)
  timestamp = models.DateTimeField(auto_now=True)
  label = models.TextField(blank=True, null=True)
  category = models.TextField(blank=True, null=True)
  sex = models.TextField(blank=True, null=True)
  rating = models.FloatField(blank=True, null=True)
  currency = models.CharField(max_length=1, default='$')
  price = models.FloatField(blank=True, null=True)
  owner = models.TextField(blank=True, null=True)

  def _str_(self):
    return self.name


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    num_projects = models.IntegerField(default=0)
    is_guest_account = models.BooleanField(default=False, null=True, blank=True)

    def is_guest(self):
        return self.is_guest_account

    @classmethod
    def return_if_guest(cls, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user if user.is_guest() else None
        except Exception:
            pass
        return None

    @classmethod
    def get_default(cls):
        try:
            user = User.objects.get(username="default_user")
        except Exception:
            user, _ = cls.objects.get_or_create(username="default_user")
        return user

    def __str__(self):
        return "User [{}]: {} {} ({})".format(
            self.id, self.first_name, self.last_name, self.username
        )
