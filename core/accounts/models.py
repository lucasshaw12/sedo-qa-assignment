from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    num_tickets_assigned = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
