from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BenchmarkRun, TaskResult
from .serializers import RunOnceSerializer, RunSuiteSerializer
from .services.judge import score_with_openai_judge
from .services.pricing import estimate_cost_usd
from .services.providers import call_baseten, call_openai
from .services.validation import run_deterministic
from .suite_loader import load_suite


def root_landing(_request):
    """Serve `/` so visiting port 8000 is not a 404 — API + UI hints."""
    body = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AgentJamBench</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 42rem; margin: 2rem auto; padding: 0 1rem;
      line-height: 1.5; color: #111; background: #fafafa; }
    code { background: #eee; padding: 2px 6px; border-radius: 4px; }
    a { color: #2563eb; }
    ul { padding-left: 1.2rem; }
  </style>
</head>
<body>
  <h1>AgentJamBench</h1>
  <p>Django is running. JSON APIs live under <code>/api/</code>.</p>
  <p>The <strong>web dashboard</strong> is the Vite app (port <strong>5173</strong>), not this port.</p>
  <ul>
    <li><a href="/api/health/">GET /api/health/</a></li>
    <li><a href="/api/suites/default/">GET /api/suites/default/</a></li>
    <li><a href="/api/runs/">GET /api/runs/</a></li>
  </ul>
  <p>Run the UI: <code>cd frontend && npm run dev</code> →
    <a href="http://127.0.0.1:5173">http://127.0.0.1:5173</a></p>
</body>
</html>"""
    return HttpResponse(body, content_type="text/html; charset=utf-8")


def _usage_tokens(usage: dict[str, Any] | None) -> tuple[int | None, int | None]:
    if not usage or not isinstance(usage, dict):
        return None, None
    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    if pt is None and "input_tokens" in usage:
        pt = usage.get("input_tokens")
    if ct is None and "output_tokens" in usage:
        ct = usage.get("output_tokens")
    return (
        int(pt) if pt is not None else None,
        int(ct) if ct is not None else None,
    )


@method_decorator(csrf_exempt, name="dispatch")
class HealthView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request: Request) -> Response:
        return Response({"ok": True, "service": "AgentJamBench"})


@method_decorator(csrf_exempt, name="dispatch")
class RunOnceView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request: Request) -> Response:
        ser = RunOnceSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        prompt = d["prompt"]
        temperature = d["temperature"]
        max_tokens = d["max_tokens"]
        system = (d.get("system") or "").strip() or None

        if d["provider"] == "openai":
            out = call_openai(
                prompt=prompt,
                model=d["openai_model"],
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            out = call_baseten(
                prompt=prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        if not out.get("ok"):
            return Response(out, status=status.HTTP_400_BAD_REQUEST)

        usage = out.get("usage")
        pt, ct = _usage_tokens(usage if isinstance(usage, dict) else None)
        model_label = d["openai_model"] if d["provider"] == "openai" else "baseten"
        est = estimate_cost_usd(model_label, pt, ct) if d["provider"] == "openai" else None

        return Response(
            {
                "ok": True,
                "provider": d["provider"],
                "text": out.get("text"),
                "duration_ms": out.get("duration_ms"),
                "usage": usage,
                "estimated_cost_usd": est,
                "estimate_note": "OpenAI pricing table estimate; Baseten varies by deployment.",
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class SuiteDetailView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request: Request, suite_id: str) -> Response:
        try:
            data = load_suite(suite_id if suite_id != "default" else "default")
        except FileNotFoundError:
            return Response({"detail": "Suite not found"}, status=404)
        return Response(data)


@method_decorator(csrf_exempt, name="dispatch")
class RunSuiteView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request: Request) -> Response:
        ser = RunSuiteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        suite_id = d["suite_id"]
        try:
            suite = load_suite(suite_id)
        except FileNotFoundError:
            return Response({"detail": "Suite not found"}, status=404)

        tasks = suite.get("tasks") or []
        if not tasks:
            return Response({"detail": "Suite has no tasks"}, status=400)

        providers = d.get("providers") or ["openai", "baseten"]
        temperature = d["temperature"]
        max_tokens = d["max_tokens"]
        system = (d.get("system") or "").strip() or None
        openai_model = d["openai_model"]
        use_judge = d["use_judge"]
        judge_model = d["judge_model"]

        run = BenchmarkRun.objects.create(
            suite_id=suite.get("id") or suite_id,
            status="running",
            meta={
                "title": suite.get("title"),
                "providers": providers,
                "openai_model": openai_model,
                "use_judge": use_judge,
            },
        )

        results_payload: list[dict[str, Any]] = []

        try:
            for task in tasks:
                tid = str(task.get("id") or "task")
                prompt = str(task.get("prompt") or "")
                for prov in providers:
                    if prov == "openai":
                        out = call_openai(
                            prompt=prompt,
                            model=openai_model,
                            system=system,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        model_label = openai_model
                    else:
                        out = call_baseten(
                            prompt=prompt,
                            system=system,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        model_label = "baseten"

                    err = out.get("error") if not out.get("ok") else None
                    text = (out.get("text") or "") if out.get("ok") else ""
                    duration_ms = out.get("duration_ms")
                    usage = out.get("usage")

                    pt, ct = _usage_tokens(usage if isinstance(usage, dict) else None)
                    est = None
                    if prov == "openai" and out.get("ok"):
                        est = estimate_cost_usd(openai_model, pt, ct)

                    det = run_deterministic(task, text)
                    judge_data = None
                    if use_judge and out.get("ok") and text:
                        judge_data = score_with_openai_judge(
                            task_prompt=prompt,
                            assistant_text=text,
                            judge_model=judge_model,
                        )

                    tr = TaskResult.objects.create(
                        run=run,
                        task_id=tid,
                        provider=prov,
                        model_label=model_label,
                        prompt=prompt,
                        output_text=text,
                        duration_ms=duration_ms,
                        usage=usage if isinstance(usage, dict) else None,
                        estimated_cost_usd=est,
                        error=err,
                        deterministic=det,
                        judge=judge_data,
                    )

                    results_payload.append(
                        {
                            "id": tr.id,
                            "task_id": tid,
                            "provider": prov,
                            "duration_ms": duration_ms,
                            "estimated_cost_usd": est,
                            "deterministic": det,
                            "judge": judge_data,
                            "error": err,
                        }
                    )

            run.status = "completed"
            run.save(update_fields=["status"])
        except Exception as e:
            run.status = "failed"
            run.meta = {**run.meta, "error": str(e)}
            run.save(update_fields=["status", "meta"])
            return Response(
                {"detail": str(e), "run_id": run.id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        summary = _summarize_run(run.id)
        return Response({"run_id": run.id, "summary": summary, "results": results_payload})


def _summarize_run(run_id: int) -> dict[str, Any]:
    rows = list(TaskResult.objects.filter(run_id=run_id))
    by_prov: dict[str, list[TaskResult]] = defaultdict(list)
    for r in rows:
        by_prov[r.provider].append(r)

    out: dict[str, Any] = {"by_provider": {}}
    for prov, lst in by_prov.items():
        latencies = [x.duration_ms for x in lst if x.duration_ms is not None]
        costs = [x.estimated_cost_usd for x in lst if x.estimated_cost_usd is not None]
        judge_scores: list[float] = []
        det_pass = 0
        det_total = 0
        for x in lst:
            j = x.judge or {}
            if isinstance(j, dict) and j.get("ok") and isinstance(j.get("scores"), dict):
                sc = j["scores"]
                dims = [
                    float(sc[k])
                    for k in ("correctness", "instruction_following", "safety", "conciseness")
                    if k in sc and isinstance(sc[k], (int, float))
                ]
                if dims:
                    judge_scores.append(sum(dims) / len(dims))
            det = x.deterministic or {}
            if det.get("applies"):
                det_total += 1
                if det.get("pass"):
                    det_pass += 1

        avg_latency = sum(latencies) / len(latencies) if latencies else None
        sum_cost = sum(costs) if costs else None
        avg_judge = sum(judge_scores) / len(judge_scores) if judge_scores else None
        det_rate = (det_pass / det_total) if det_total else None

        out["by_provider"][prov] = {
            "n_tasks": len(lst),
            "avg_latency_ms": avg_latency,
            "sum_estimated_cost_usd": sum_cost,
            "avg_judge_rubric_0_to_5": avg_judge,
            "deterministic_pass_rate": det_rate,
        }
    return out


@method_decorator(csrf_exempt, name="dispatch")
class RunListView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request: Request) -> Response:
        try:
            limit = int(request.query_params.get("limit", 30))
        except ValueError:
            limit = 30
        limit = max(1, min(limit, 100))
        runs = BenchmarkRun.objects.all()[:limit]
        return Response(
            {
                "runs": [
                    {
                        "id": r.id,
                        "created_at": r.created_at,
                        "suite_id": r.suite_id,
                        "status": r.status,
                        "meta": r.meta,
                        "summary": _summarize_run(r.id),
                    }
                    for r in runs
                ]
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class RunDetailView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request: Request, run_id: int) -> Response:
        run = get_object_or_404(BenchmarkRun, pk=run_id)
        rows = TaskResult.objects.filter(run=run).order_by("id")
        return Response(
            {
                "run": {
                    "id": run.id,
                    "created_at": run.created_at,
                    "suite_id": run.suite_id,
                    "status": run.status,
                    "meta": run.meta,
                },
                "summary": _summarize_run(run.id),
                "results": [
                    {
                        "id": r.id,
                        "task_id": r.task_id,
                        "provider": r.provider,
                        "model_label": r.model_label,
                        "prompt": r.prompt,
                        "output_text": r.output_text,
                        "duration_ms": r.duration_ms,
                        "usage": r.usage,
                        "estimated_cost_usd": r.estimated_cost_usd,
                        "error": r.error,
                        "deterministic": r.deterministic,
                        "judge": r.judge,
                    }
                    for r in rows
                ],
            }
        )
