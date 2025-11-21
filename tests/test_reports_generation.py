from ru_gov_services_availability_monitor.reports.incidents import generate_incident_report
from ru_gov_services_availability_monitor.collector.storage import Metric
import time


def test_generate_incident_report():
    metrics = [
        Metric(
            service_id="s1",
            region_id="r1",
            timestamp=time.time(),
            status_code=500,
            latency_ms=100.0,
            available=False,
            error="Server Error",
            tls_info=None,
        )
    ]

    report = generate_incident_report(metrics)
    assert "# Incident Report" in report
    assert "Service: s1" in report
    assert "Failures: 1" in report
