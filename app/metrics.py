# app/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# ---------------------------
# Basic Request Metrics
# ---------------------------

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency",
    ["endpoint"]
)

IN_PROGRESS = Gauge(
    "app_in_progress_requests",
    "Number of requests in progress"
)

# ---------------------------
# Feature Usage Metrics
# ---------------------------

USAGE_COUNT = Counter(
    "app_feature_usage_total",
    "Usage count of features",
    ["feature"]
)

# ---------------------------
# Feedback Metrics
# ---------------------------

FEEDBACK_COUNT = Counter(
    "app_feedback_total",
    "Total number of feedback items",
    ["source", "rating"]
)