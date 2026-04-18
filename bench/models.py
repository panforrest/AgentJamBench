from django.db import models


class BenchmarkRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    suite_id = models.CharField(max_length=128)
    status = models.CharField(max_length=32, default="completed")
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"BenchmarkRun({self.pk}, {self.suite_id}, {self.status})"


class TaskResult(models.Model):
    run = models.ForeignKey(
        BenchmarkRun,
        on_delete=models.CASCADE,
        related_name="results",
    )
    task_id = models.CharField(max_length=128)
    provider = models.CharField(max_length=32)
    model_label = models.CharField(max_length=256, blank=True)
    prompt = models.TextField()
    output_text = models.TextField(blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    usage = models.JSONField(null=True, blank=True)
    estimated_cost_usd = models.FloatField(null=True, blank=True)
    error = models.JSONField(null=True, blank=True)
    deterministic = models.JSONField(null=True, blank=True)
    judge = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
