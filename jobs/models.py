from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Job(models.Model):

    JOB_TYPES = (
        ("FULL_TIME", "Full Time"),
        ("PART_TIME", "Part Time"),
        ("INTERNSHIP", "Internship"),
        ("CONTRACT", "Contract"),
    )

    EXPERIENCE_LEVELS = (
        ("ENTRY_LEVEL", "Entry Level"),
        ("MID_LEVEL", "Mid Level"),
        ("SENIOR_LEVEL", "Senior Level"),
    )

    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    description = models.TextField()
    requirements = models.TextField()
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPES,
    )
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVELS,
    )

    is_active = models.BooleanField(default=True)
    application_deadline = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired(self):
        return timezone.now() >= self.application_deadline


class Saved_job(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "job"],
                name="unique_saved_job",
            )
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


class JobView(models.Model):

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="views",
    )

    viewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="job_views",
    )

    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "viewer"],
                name="unique_job_viewer",
            )
        ]

    def __str__(self):
        return f"{self.viewer.username} viewed job {self.job.title}"
