from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth import get_user_model
from .models import RecruiterProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "JOB_SEEKER":
            Profile.objects.create(user=instance)

        elif instance.role == "RECRUITER":
            RecruiterProfile.objects.create(user=instance)
