from django.shortcuts import render, redirect, get_object_or_404
from .forms import JobForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Job
from django.utils import timezone
from application.models import Application
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Saved_job
from .models import Job, JobView


@login_required
def create_job_view(request):
    if request.method == "POST":
        form = JobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, "Job created successfully.")
            return redirect("jobs:job_list_view")

        messages.error(
            request,
            "Job could not be created. Please check the form and try again.",
        )
    else:
        form = JobForm()
    return render(
        request,
        "jobs/create_job.html",
        {"form": form},
    )


@login_required
def job_list_view(request):
    search = request.GET.get("q")
    job_type = request.GET.get("job_type")
    experience = request.GET.get("experience")
    sort = request.GET.get("sort")

    jobs = (
        Job.objects.select_related("recruiter")
        .filter(
            is_active=True,
            application_deadline__gte=timezone.now().date(),
        )
        .order_by("-created_at")
    )

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(company_name__icontains=search)
            | Q(location__icontains=search)
        )

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    if experience:
        jobs = jobs.filter(experience_level=experience)

    if sort == "oldest":
        jobs = jobs.order_by("created_at")
    elif sort == "newest":
        jobs = jobs.order_by("-created_at")
    elif sort == "salary_low":
        jobs = jobs.order_by("salary")
    elif sort == "salary_high":
        jobs = jobs.order_by("-salary")

    paginator = Paginator(jobs, 8)
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)

    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
        },
    )


@login_required
def job_detail_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    is_applied = Application.objects.filter(
        applicant=request.user,
        job=job,
    ).exists()

    is_saved = Saved_job.objects.filter(
        user=request.user,
        job=job,
    ).exists()

    company = getattr(job.recruiter, "company", None)
    requirements = job.requirements.split("\n")

    if request.user != job.recruiter:
        has_viewed = JobView.objects.filter(job=job, viewer=request.user).exists()
        if not has_viewed:
            JobView.objects.create(
                job=job,
                viewer=request.user,
            )

    return render(
        request,
        "jobs/job_details.html",
        {
            "job": job,
            "company": company,
            "is_applied": is_applied,
            "is_saved": is_saved,
            "requirements": requirements,
        },
    )


@login_required
def my_job_view(request):
    jobs = Job.objects.filter(
        recruiter=request.user,
    ).order_by("-created_at")

    paginator = Paginator(jobs, 8)
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)
    return render(
        request,
        "jobs/my_job.html",
        {"jobs": jobs},
    )


@login_required
def job_edit_view(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Job updated successfully",
            )
            return redirect("jobs:my_job_view")
        else:
            messages.success(
                request,
                "Unable to update the job. Please try again.",
            )
    else:
        form = JobForm(instance=job)
    return render(
        request,
        "jobs/edit_job.html",
        {"form": form},
    )


@login_required
def job_delete_view(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully")
        return redirect("jobs:my_job_view")
    return render(
        request,
        "jobs/delete_job.html",
        {"job": job},
    )


@login_required
def job_saved_view(request, pk):
    if request.user.role != "JOB_SEEKER":
        messages.error(request, "Only job seekers can save jobs")
        return redirect("jobs:job_detail_view", pk=pk)

    job = get_object_or_404(Job, pk=pk)

    Saved_job.objects.get_or_create(
        user=request.user,
        job=job,
    )

    messages.success(
        request,
        "Job saved successfully",
    )

    return redirect("jobs:job_detail_view", pk=pk)


@login_required
def job_unsaved_view(request, pk):
    if request.user.role != "JOB_SEEKER":
        messages.error(
            request,
            "Only job seeker can unsave jobs",
        )
        return redirect("jobs:job_detail_view", pk=pk)

    job = get_object_or_404(Job, pk=pk)

    saved_job = Saved_job.objects.filter(
        user=request.user,
        job=job,
    )
    saved_job.delete()
    messages.success(
        request,
        "Successfully unsaved the job",
    )

    return redirect("jobs:job_detail_view", pk=pk)


@login_required
def job_saved_list(request):

    if request.user.role != "JOB_SEEKER":
        messages.error(
            request,
            "Only the job seeker can view their saved jobs",
        )
        return redirect("job_seeker_dashboard_view")

    saved_jobs = (
        Saved_job.objects.filter(user=request.user)
        .select_related("job")
        .order_by("-saved_at")
    )

    paginator = Paginator(saved_jobs, 5)
    page_no = request.GET.get("page")
    saved_jobs = paginator.get_page(page_no)

    return render(
        request,
        "jobs/saved_job.html",
        {
            "saved_jobs": saved_jobs,
        },
    )

@login_required
def job_analytics_view(request, pk):

    if request.user.role != "RECRUITER":
        messages.error(
            request,
            "Access denied. Job performance analytics are available only to recruiters.",
        )
        return redirect("job_seeker_dashboard_view")

    job = get_object_or_404(
        Job,
        pk=pk,
        recruiter=request.user,
    )
    applications = job.applications.all()
    application_count = applications.count()
    saved_job_count = Saved_job.objects.filter(job=job).count()
    job_view_count = job.views.count()
    status_pending_count = applications.filter(status="PENDING").count()
    status_accepted_count = applications.filter(status="ACCEPTED").count()
    status_rejected_count = applications.filter(status="REJECTED").count()

    if application_count > 0:
        pending_progress_width = (status_pending_count / application_count) * 100
        accepted_progress_width = (status_accepted_count / application_count) * 100
        rejected_progress_width = (status_rejected_count / application_count) * 100
    else:
        pending_progress_width = 0
        accepted_progress_width = 0
        rejected_progress_width = 0

    if job_view_count > 0:
        apply_rate = (application_count / job_view_count) * 100
    else:
        apply_rate = 0
    return render(
        request,
        "jobs/job_analytics.html",
        {
            "job": job,
            "application_count": application_count,
            "applications": applications,
            "saved_job_count": saved_job_count,
            "job_view_count": job_view_count,
            "apply_rate": apply_rate,
            "status_pending_count": status_pending_count,
            "status_accepted_count": status_accepted_count,
            "status_rejected_count": status_rejected_count,
            "pending_progress_width": pending_progress_width,
            "accepted_progress_width": accepted_progress_width,
            "rejected_progress_width": rejected_progress_width,
        },
    )
