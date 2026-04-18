from django.contrib import admin

from .models import BenchmarkRun, TaskResult


@admin.register(BenchmarkRun)
class BenchmarkRunAdmin(admin.ModelAdmin):
    list_display = ("id", "suite_id", "status", "created_at")
    search_fields = ("suite_id",)


@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "task_id", "provider", "duration_ms")
    list_filter = ("provider",)
