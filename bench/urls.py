from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("run/once/", views.RunOnceView.as_view(), name="run-once"),
    path("run/suite/", views.RunSuiteView.as_view(), name="run-suite"),
    path("runs/", views.RunListView.as_view(), name="run-list"),
    path("runs/<int:run_id>/", views.RunDetailView.as_view(), name="run-detail"),
    path("suites/<str:suite_id>/", views.SuiteDetailView.as_view(), name="suite-detail"),
    path("veris/probe/", views.VerisCliProbeView.as_view(), name="veris-probe"),
    path("veris/scenarios/", views.VerisScenariosListView.as_view(), name="veris-scenarios"),
]
