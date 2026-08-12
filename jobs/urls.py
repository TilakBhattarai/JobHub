from django.urls import path
from .views import *

app_name = "jobs"


urlpatterns = [
    path("create/", create_job_view, name="create_job_view"),
    path("job-list/", job_list_view, name="job_list_view"),
    path("my-job/", my_job_view, name="my_job_view"),
    path("job-detail/<int:pk>/", job_detail_view, name="job_detail_view"),
    path("job-edit/<int:pk>/", job_edit_view, name="job_edit_view"),
    path("job-delete/<int:pk>/", job_delete_view, name="job_delete_view"),
    path("job/<int:pk>/saved/", job_saved_view, name="job_saved_view"),
    path("job/<int:pk>/unsaved/", job_unsaved_view, name="job_unsaved_view"),
    path("saved_jobs/", job_saved_list, name="job_saved_list"),
    path(
        "recruiter/jobs/<int:pk>/analytics/",
        job_analytics_view,
        name="job_analytics_view",
    ),
]
