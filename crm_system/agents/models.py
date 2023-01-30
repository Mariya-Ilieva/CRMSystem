from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save


class User(AbstractUser):
    is_organizer = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


def profile_create(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(profile_create, sender=User)
