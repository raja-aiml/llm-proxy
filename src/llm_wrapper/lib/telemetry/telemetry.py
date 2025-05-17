import time
import logging
import socket
from urllib.parse import urlparse

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server
import os


class TelemetrySetup:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TelemetrySetup, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        service_name: str,
        version: str = "1.0.0",
        otlp_endpoint: str = "http://localhost:4318/v1/traces",
        prometheus_port: int = 9464
    ):
        # Optionally disable telemetry via environment
        if os.getenv("DISABLE_TELEMETRY", "false").lower() in ("1", "true", "yes"):
            logging.getLogger(__name__).info("Telemetry disabled via DISABLE_TELEMETRY env var")
            # retain service_name for no-op tracer/meter
            self.service_name = service_name
            TelemetrySetup._initialized = True
            return
        if TelemetrySetup._initialized:
            logging.getLogger(__name__).warning("Telemetry already initialized; skipping re-init.")
            return

        self.logger = logging.getLogger(__name__)
        self.service_name = service_name
        self.version = version
        self.otlp_endpoint = otlp_endpoint
        self.prometheus_port = prometheus_port

        self.resource = Resource.create({
            "service.name": self.service_name,
            "service.version": self.version,
        })

        if not self._is_port_in_use(self.prometheus_port):
            start_http_server(self.prometheus_port)
            self.logger.info(f"Prometheus server running on port {self.prometheus_port}")
        else:
            self.logger.warning(f"Port {self.prometheus_port} is already in use. Prometheus exporter not started.")

        self._init_tracer()
        self._init_metrics()

        TelemetrySetup._initialized = True

    def _is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            return sock.connect_ex(('localhost', port)) == 0

    def _init_tracer(self):
        # Pre-flight check: skip tracer exporter if endpoint unreachable
        try:
            parsed = urlparse(self.otlp_endpoint)
            host = parsed.hostname or 'localhost'
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                if sock.connect_ex((host, port)) != 0:
                    self.logger.warning(
                        f"OTLP endpoint {self.otlp_endpoint} unreachable at {host}:{port}, tracing disabled."
                    )
                    return
        except Exception as check_err:
            self.logger.warning(
                f"Error checking OTLP endpoint reachability ({self.otlp_endpoint}): {check_err}. Proceeding with tracer init."
            )
        # Initialize tracer with OTLP exporter
        try:
            tracer_provider = TracerProvider(resource=self.resource)
            tracer_provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=self.otlp_endpoint))
            )
            trace.set_tracer_provider(tracer_provider)
            self.logger.info(f"Tracer initialized with endpoint {self.otlp_endpoint}")
        except Exception as init_err:
            self.logger.warning(f"Tracer already set or failed to initialize: {init_err}")

    def _init_metrics(self):
        try:
            reader = PrometheusMetricReader()
            meter_provider = MeterProvider(resource=self.resource, metric_readers=[reader])
            metrics.set_meter_provider(meter_provider)
            self.logger.info("Metrics initialized with Prometheus reader")
        except Exception as e:
            self.logger.warning(f"MeterProvider already set or failed to initialize: {e}")

    def get_tracer(self):
        return trace.get_tracer(self.service_name)

    def get_meter(self):
        return metrics.get_meter(self.service_name)

    def shutdown(self):
        try:
            trace.get_tracer_provider().shutdown()
        except Exception:
            pass
        try:
            metrics.get_meter_provider().shutdown()
        except Exception:
            pass

def main():
    logging.info("Starting telemetry service")
    telemetry = TelemetrySetup(
        service_name="telemetry_service",
        prometheus_port=9090,
    )
    
    tracer = telemetry.get_tracer()
    meter = telemetry.get_meter()
    
    # Tracing
    with tracer.start_as_current_span("telemetry_span"):
        logging.info("Tracing: inside telemetry_span")
    
    # Metrics
    counter = meter.create_counter(
        name="example_counter",
        description="Example counter metric",
        unit="1"
    )
    counter.add(1, {"key": "value"})
    
    logging.info("Metrics server running. Visit http://localhost:9090/metrics")
    try:
        while True:
            time.sleep(5)
            counter.add(1, {"key": "value"})
            logging.debug("Counter incremented")
    except KeyboardInterrupt:
        logging.info("Shutting down telemetry service")
        telemetry.shutdown()


if __name__ == "__main__":  # pragma: no cover
    main()