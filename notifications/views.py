from django.shortcuts import render, redirect
from .models import Notification
from django.utils import timezone
from datetime import timedelta
from application.models import Application


def recruiter_notification_view(request):
    unread_count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    total_count = Notification.objects.filter(recipient=request.user).count()
    today = timezone.now().date()
    start_of_week = today - timedelta(today.weekday())

    week_count = Notification.objects.filter(
        recipient=request.user,
        created_at__date__gte=start_of_week,
    ).count()

    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True
    )

    notifications = Notification.objects.filter(recipient=request.user)

    return render(
        request,
        "notifications/recruiter_notification.html",
        {
            "unread_count": unread_count,
            "total_count": total_count,
            "week_count": week_count,
            "notifications": notifications,
        },
    )


def candidate_notification_view(request):
    unread_count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    total_count = Notification.objects.filter(recipient=request.user).count()
    today = timezone.now().date()
    start_of_week = today - timedelta(today.weekday())

    week_count = Notification.objects.filter(
        recipient=request.user,
        created_at__date__gte=start_of_week,
    ).count()

    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True
    )

    notifications = Notification.objects.filter(recipient=request.user)
    return render(
        request,
        "notifications/job_seeker_notification.html",
        {
            "total_count": total_count,
            "unread_count": unread_count,
            "week_count": week_count,
            "notifications": notifications,
        },
    )
