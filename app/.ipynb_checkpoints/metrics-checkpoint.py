# app/metrics.py
from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge

# -------------------------
# Core HTTP metrics
# -------------------------
REQUEST_COUNT = Counter(
    "appetite_request_count",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "appetite_request_latency_seconds",
    "Latency per endpoint in seconds",
    ["endpoint"],
)

IN_PROGRESS = Gauge(
    "appetite_requests_in_progress",
    "Number of requests currently being processed",
)

# -------------------------
# Feature usage metrics
# -------------------------
USAGE_COUNT = Counter(
    "appetite_feature_usage_total",
    "Count of feature usage",
    ["feature"],
)

# -------------------------
# Feedback metrics
# page = 'recommend' | 'quickgen'
# rating = '1'..'5'
# -------------------------
FEEDBACK_COUNT = Counter(
    "appetite_feedback_total",
    "User feedback count by page and rating",
    ["page", "rating"],
)