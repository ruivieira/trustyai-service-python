from prometheus_client import Gauge

SPD_METRIC = Gauge(
    "trustyai_spd",
    "Statistical Parity Difference metric",
    labelnames=("model", "outcome")
)