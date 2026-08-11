from django.urls import path
from .views import *

urlpatterns = [
    path("register/", register_view, name="register_view"),
    path("login/", login_view, name="login_view"),
    path("logout/", logout_view, name="logout_view"),
    path(
        "recruiter-dashboard/",
        recruiter_dashboard_view,
        name="recruiter_dashboard_view",
    ),
    path(
        "job-seeker-dashboard/",
        job_seeker_dashboard_view,
        name="job_seeker_dashboard_view",
    ),
    path("profile/", profile_view, name="profile_view"),
    path("edit-profile/", edit_profile_view, name="edit_profile_view"),
    path("company/create/", create_company_view, name="create_company_view"),
    path("company/edit/", edit_company_view, name="edit_company_view"),
    path("company/<int:pk>/", company_detail_view, name="company_detail_view"),
]
