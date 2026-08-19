from django.urls import path
from .views import *

urlpatterns = [
    path(
        "recruiter/notifications/",
        recruiter_notification_view,
        name="recruiter_notification_view",
    ),
    path(
        "candidate/notifications/",
        candidate_notification_view,
        name="candidate_notification_view",
    ),
]
