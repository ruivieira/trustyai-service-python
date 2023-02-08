from typing import Callable, Awaitable

from fastapi import FastAPI
from trustyai.metrics.fairness.group import statistical_parity_difference, disparate_impact_ratio
from trustyai.model import output
import uuid
import datetime
from .metrics.payload import DIRRequest, SPDRequest
from prometheus_fastapi_instrumentator.instrumentation import PrometheusFastApiInstrumentator

from .consumers.mock import MockDataConsumer
from .metrics.prometheus import SPD_METRIC
from . import ServiceConfiguration

CONF = ServiceConfiguration()


def setup_prometheus(app: FastAPI) -> None:  # pragma: no cover
    """
    Enables prometheus integration.
    :param app: current application.
    """
    PrometheusFastApiInstrumentator(should_group_status_codes=False).instrument(
        app,
    ).expose(app, should_gzip=True, name="prometheus_metrics")


def register_startup_event(app: FastAPI) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.
    This function uses fastAPI app to store data
    inthe state, such as db_engine.
    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        setup_prometheus(app)
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(app: FastAPI) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.
    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        pass  # noqa: WPS420

    return _shutdown


app = FastAPI(
    title="TrustyAI service",
    version="0.1",
)

# Adds startup and shutdown events.
register_startup_event(app)
register_shutdown_event(app)

CONSUMER = MockDataConsumer()


@app.post("/metrics/spd")
async def spd(request: SPDRequest):
    df = CONSUMER.as_dataframe()
    privileged = df[df[request.protectedAttribute] == request.privilegedValue]
    unprivileged = df[df[request.protectedAttribute] == request.unprivilegedValue]
    favorable = output(request.outcomeName, dtype="number", value=request.favorableOutcome)
    spd = statistical_parity_difference(privileged, unprivileged, [favorable])
    SPD_METRIC.labels("example", request.outcomeName).set(spd)
    return {
        "type": "metric",
        "name": "SPD",
        "value": spd,
        "id": uuid.uuid4(),
        "timestamp": datetime.datetime.now(),
        "thresholds": {
            "lowerBound": CONF.spd_metrics.lower,
            "upperBound": CONF.spd_metrics.upper,
            "outsideBounds": spd <= CONF.spd_metrics.lower or spd >= CONF.spd_metrics.upper
        }
    }


@app.post("/metrics/dir")
async def spd(request: DIRRequest):
    df = CONSUMER.as_dataframe()
    privileged = df[df[request.protectedAttribute] == request.privilegedValue]
    unprivileged = df[df[request.protectedAttribute] == request.unprivilegedValue]
    favorable = output(request.outcomeName, dtype="number", value=request.favorableOutcome)
    _dir = disparate_impact_ratio(privileged, unprivileged, [favorable])
    return {
        "type": "metric",
        "name": "DIR",
        "value": _dir,
        "id": uuid.uuid4(),
        "timestamp": datetime.datetime.now(),
        "thresholds": {
            "lowerBound": CONF.dir_metrics.lower,
            "upperBound": CONF.dir_metrics.upper,
            "outsideBounds": _dir <= CONF.dir_metrics.lower or _dir >= CONF.dir_metrics.upper
        }
    }
