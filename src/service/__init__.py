from dataclasses import dataclass
import os


@dataclass
class MetricsConfiguration:
    lower: float
    upper: float


class ServiceConfiguration:
    def __init__(self):
        self.spd_metrics = MetricsConfiguration(lower=float(os.getenv("SPD_THRESHOLD_LOWER", -0.1)),
                                                upper=float(os.getenv("SPD_THRESHOLD_UPPER", 0.1)))
        self.dir_metrics = MetricsConfiguration(lower=float(os.getenv("DIR_THRESHOLD_LOWER", 0.8)),
                                                upper=float(os.getenv("DIR_THRESHOLD_UPPER", 1.2)))
