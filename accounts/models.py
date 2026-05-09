"""Account models.

The project uses a custom user model from the beginning so profile fields can
be added without painful migrations later.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    display_name = models.CharField(max_length=120, blank=True)
    institution = models.CharField(max_length=180, blank=True)
    bio = models.TextField(blank=True)

    @property
    def public_name(self):
        return self.display_name or self.get_full_name() or self.username

    @property
    def initials(self):
        name = self.public_name.strip() or self.username
        parts = [part[0] for part in name.split() if part]
        return "".join(parts[:2]).upper() or self.username[:2].upper()
