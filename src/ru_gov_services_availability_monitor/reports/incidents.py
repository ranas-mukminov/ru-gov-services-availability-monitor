from typing import List
from ..collector.storage import Metric
from datetime import datetime


def generate_incident_report(metrics: List[Metric]) -> str:
    """
    Generates a simple text report of incidents based on metrics.
    """
    report = ["# Incident Report\n"]
    report.append(f"Generated at: {datetime.now().isoformat()}\n")

    # Group by service
    services = {}
    for m in metrics:
        if m.service_id not in services:
            services[m.service_id] = []
        services[m.service_id].append(m)

    for service_id, service_metrics in services.items():
        failures = [m for m in service_metrics if not m.available]
        if failures:
            report.append(f"## Service: {service_id}")
            report.append(f"Total checks: {len(service_metrics)}")
            report.append(f"Failures: {len(failures)}")
            report.append("Recent failures:")
            for f in failures[:5]:
                report.append(
                    f"- {datetime.fromtimestamp(f.timestamp)}: {f.error or 'Unknown error'} (Region: {f.region_id})"
                )
            report.append("")

    if len(report) == 2:
        report.append("No incidents detected in the provided metrics.")

    return "\n".join(report)
