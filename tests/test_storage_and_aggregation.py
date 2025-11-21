from ru_gov_services_availability_monitor.collector.storage import Storage, Metric
import time


def test_storage_save_and_get(tmp_path):
    db_path = tmp_path / "test.db"
    storage = Storage(str(db_path))

    metric = Metric(
        service_id="s1",
        region_id="r1",
        timestamp=time.time(),
        status_code=200,
        latency_ms=100.0,
        available=True,
        error=None,
        tls_info=None,
    )

    storage.save_metric(metric)

    metrics = storage.get_metrics(service_id="s1")
    assert len(metrics) == 1
    assert metrics[0].service_id == "s1"
    assert metrics[0].available
