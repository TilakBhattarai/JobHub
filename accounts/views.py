from django.shortcuts import render, redirect, get_object_or_404
from .forms import (
    RegistrationForm,
    LoginForm,
    ProfileForm,
    RecruiterProfileForm,
    CompanyForm,
)
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from jobs.models import Job
from application.models import Application
from django.core.paginator import Paginator
from jobs.models import Saved_job
from .models import Company
from django.utils import timezone

User = get_user_model()


def register_view(request):

    if request.user.is_authenticated and request.user.role == "RECRUITER":
        return redirect("recruiter_dashboard_view")

    elif request.user.is_authenticated and request.user.role == "JOB_SEEKER":
        return redirect("job_seeker_dashboard_view")

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                role=form.cleaned_data["role"],
                password=form.cleaned_data["password1"],
            )

            messages.success(request, "Registration successful. You can now log in.")

            return redirect("login_view")

    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have successfully logged in ")
            if request.user.role == "RECRUITER":
                return redirect("recruiter_dashboard_view")
            return redirect("job_seeker_dashboard_view")
        else:
            messages.error(request, "Please enter a correct username and password.")
    else:
        form = LoginForm()
    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out")
    return redirect("login_view")


@login_required
def profile_view(request):
    company = None
    if request.user.role == "JOB_SEEKER":
        profile = request.user.profile
    elif request.user.role == "RECRUITER":
        profile = request.user.recruiterprofile
        company = getattr(request.user, "company", None)
    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "company": company,
        },
    )


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        if request.user.role == "JOB_SEEKER":
            form = ProfileForm(
                request.POST, request.FILES, instance=request.user.profile
            )
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Your profile has been updated successfully",
                )
                return redirect("profile_view")
            else:
                messages.error(request, "invalid details, please try again")
        elif request.user.role == "RECRUITER":
            form = RecruiterProfileForm(
                request.POST, request.FILES, instance=request.user.recruiterprofile
            )
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Your profile has been updated successfully",
                )
                return redirect("profile_view")
            else:
                messages.error(request, "invalid details, please try again")

    else:
        if request.user.role == "RECRUITER":
            form = RecruiterProfileForm(instance=request.user.recruiterprofile)
        elif request.user.role == "JOB_SEEKER":
            form = ProfileForm(instance=request.user.profile)
        return render(
            request,
            "accounts/edit_profile.html",
            {"form": form},
        )


@login_required
def recruiter_dashboard_view(request):
    if request.user.role != "RECRUITER":
        messages.error(
            request,
            "Access denied. Only recruiters can access the recruiter dashboard.",
        )
        return redirect("job_seeker_dashboard_view")

    total_jobs = Job.objects.filter(
        recruiter=request.user,
    ).count()

    active_jobs = Job.objects.filter(
        recruiter=request.user,
        is_active=True,
        application_deadline__gte=timezone.datetime.now(),
    ).count()
    total_applicants = Application.objects.filter(job__recruiter=request.user).count()

    accepted_candidates = Application.objects.filter(
        status="ACCEPTED", job__recruiter=request.user
    ).count()

    pending_candidates = Application.objects.filter(
        status="PENDING", job__recruiter=request.user
    ).count()

    rejected_candidates = Application.objects.filter(
        status="REJECTED", job__recruiter=request.user
    ).count()

    jobs = (
        Job.objects.filter(
            recruiter=request.user,
        )
        .prefetch_related("applications")
        .order_by("-created_at")
    )
    paginator = Paginator(jobs, 8)
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)
    return render(
        request,
        "accounts/recruiter_dashboard.html",
        {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applicants": total_applicants,
            "jobs": jobs,
            "accepted_candidates": accepted_candidates,
            "rejected_candidates": rejected_candidates,
            "pending_candidates": pending_candidates,
        },
    )


@login_required
def job_seeker_dashboard_view(request):
    if request.user.role == "RECRUITER":
        messages.error(
            request,
            "Access denied. Only recruiters can access the recruiter dashboard.",
        )
        return redirect("recruiter_dashboard_view")

    available_jobs = Job.objects.filter(is_active=True).count()

    # Use a queryset (no slice) and paginate it
    jobs_qs = Job.objects.filter(
        is_active=True, application_deadline__gte=timezone.now().date()
    ).order_by("-created_at")

    total_applied_jobs = Application.objects.filter(applicant=request.user).count()
    total_pending_jobs = Application.objects.filter(
        applicant=request.user, status="PENDING"
    ).count()

    total_accepted_jobs = Application.objects.filter(
        applicant=request.user,
        status="ACCEPTED",
    ).count()

    total_saved_jobs = (
        Saved_job.objects.filter(user=request.user)
        .select_related("job")
        .order_by("-saved_at")
        .count()
    )

    applied_job_ids = set(
        Application.objects.filter(applicant=request.user).values_list(
            "job_id", flat=True
        )
    )
    applications = (
        Application.objects.select_related("job")
        .filter(applicant=request.user)
        .order_by("-applied_at")[:5]
    )

    # Saved jobs queryset & pagination (use a distinct page param)
    saved_jobs_qs = (
        Saved_job.objects.filter(user=request.user)
        .select_related("job")
        .order_by("-saved_at")
    )
    saved_paginator = Paginator(saved_jobs_qs, 3)
    saved_page = request.GET.get("saved_page")
    saved_jobs = saved_paginator.get_page(saved_page)

    # Latest jobs pagination (use a distinct page param)
    jobs_paginator = Paginator(jobs_qs, 3)
    jobs_page = request.GET.get("jobs_page")
    jobs = jobs_paginator.get_page(jobs_page)

    return render(
        request,
        "accounts/job_seeker_dashboard.html",
        {
            "available_jobs": available_jobs,
            "total_applied_jobs": total_applied_jobs,
            "applications": applications,
            "jobs": jobs,
            "applied_job_ids": applied_job_ids,
            "saved_jobs": saved_jobs,
            "total_pending_jobs": total_pending_jobs,
            "total_accepted_jobs": total_accepted_jobs,
            "total_saved_jobs": total_saved_jobs,
        },
    )


@login_required
def create_company_view(request):
    if request.user.role != "RECRUITER":
        messages.error(request, "Only the recruiter can create the company")
        return redirect("job_seeker_dashboard_view")

    if hasattr(request.user, "Company"):
        messages.info(
            request, "You already have a company profile. You can edit it here."
        )
        return redirect(
            "recruiter_dashboard_view"
        )  # replace it with the edit company page

    # if Company.objects.filter(owner=request.user).exists() we can do this too

    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()
            messages.success(request, "Company created successfully")
            return redirect("recruiter_dashboard_view")
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = CompanyForm()

    return render(
        request,
        "accounts/create_company.html",
        {
            "form": form,
        },
    )


@login_required
def edit_company_view(request):
    if request.user.role != "RECRUITER":
        messages.error(request, "Only the recruiter can edit the company profile")
        return redirect("job_seeker_dashboard_view")

    if not hasattr(request.user, "company"):
        messages.info(
            request, "You don't have a company profile yet. Please create one first."
        )
        return redirect("create_company_view")  # replace it with the edit company page

    company = request.user.company
    if request.method == "POST":

        form = CompanyForm(request.POST, request.FILES, instance=company)

        if form.is_valid():
            form.save()
            messages.success(request, "Successsfully updated the company profile")
            return redirect("recruiter_dashboard_view")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CompanyForm(instance=company)
    return render(
        request,
        "accounts/edit_company.html",
        {
            "form": form,
        },
    )


@login_required
def company_detail_view(request, pk):
    company = get_object_or_404(Company, id=pk)
    jobs = Job.objects.filter(recruiter=company.owner)
    return render(
        request,
        "accounts/company_detail.html",
        {
            "company": company,
            "jobs": jobs,
        },
    )
