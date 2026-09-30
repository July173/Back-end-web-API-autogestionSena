"""
Core views for system monitoring, health checks, and service status.
"""
from django.http import JsonResponse
from django.utils import timezone
from django.db import connection


def health_check_view(request):
    """
    Lightweight health check endpoint for uptime monitoring (e.g. cron-job.org, Render).
    Verifies database connectivity without imposing heavy query overhead.
    """
    db_status = "connected"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:
        db_status = f"degraded: {str(exc)}"

    status_code = 200
    is_healthy = db_status == "connected"

    return JsonResponse({
        "status": "healthy" if is_healthy else "degraded",
        "service": "Autogestion SENA API",
        "database": db_status,
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0"
    }, status=status_code)
