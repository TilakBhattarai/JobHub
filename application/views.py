from django.shortcuts import render, redirect, get_object_or_404
from jobs.models import Job
from .forms import ApplicationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Application
from django.http import HttpResponseForbidden


@login_required
def apply_view(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.user.role != "JOB_SEEKER":
        messages.error(
            request,
            "Only job seekers can apply for ths job",
        )
        return redirect("jobs:job_detail_view", job.id)

    if Application.objects.filter(applicant=request.user, job=job).exists():
        messages.error(
            request,
            "You have already applied for this job.",
        )
        return redirect("jobs:job_detail_view", pk=job.pk)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job = job
            application.save()
            messages.success(request, "Successfully applied for the job")
            return redirect("jobs:job_detail_view", pk=job.pk)
        else:
            messages.error(
                request,
                "Something went wrong while submitting your application. Please try again.",
            )
    else:
        form = ApplicationForm()

    return render(
        request,
        "application/apply.html",
        {
            "job": job,
            "form": form,
        },
    )


@login_required
def job_application_view(request, pk):
    if request.user.role != "RECRUITER":
        messages.error(
            request,
            "Only recruiters can view applicants.",
        )
        return redirect(
            "jobs:job_list_view",
        )
    job = get_object_or_404(
        Job,
        pk=pk,
        recruiter=request.user,
    )

    applications = (
        Application.objects.select_related("applicant")
        .filter(job=job)
        .order_by("-applied_at")
    )
    return render(
        request,
        "application/job_applications.html",
        {
            "job": job,
            "applications": applications,
        },
    )


@login_required
def my_applications(request):
    if request.user.role != "JOB_SEEKER":
        messages.error(
            request,
            "Only job seeker can view their application.",
        )
        return redirect("jobs:job_list_view")

    applications = (
        Application.objects.select_related("job")
        .filter(applicant=request.user)
        .order_by("-applied_at")
    )

    return render(
        request,
        "application/my_applications.html",
        {"applications": applications},
    )


@login_required
def accept_application(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.job.recruiter != request.user:
        return HttpResponseForbidden()

    application.status = "ACCEPTED"
    application.save()

    return redirect("recruiter_dashboard_view")


@login_required
def reject_application(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.job.recruiter != request.user:
        return HttpResponseForbidden()

    application.status = "REJECTED"
    application.save()

    return redirect("recruiter_dashboard_view")
