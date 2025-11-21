import pytest
from ru_gov_services_availability_monitor.config.loader import load_config


def test_load_config(tmp_path):
    # Create dummy configs
    (tmp_path / "services.yml").write_text("services: [{id: 's1', name: 'S1', url: 'http://s1.com'}]")
    (tmp_path / "regions.yml").write_text("regions: [{id: 'r1', name: 'R1', location: 'Loc1'}]")
    (tmp_path / "agent.yml").write_text("agent: {region_id: 'r1', collector_url: 'http://c.com', services: ['s1']}")

    config = load_config(tmp_path)

    assert len(config.services) == 1
    assert config.services[0].id == "s1"
    assert config.agent.region_id == "r1"


def test_missing_config_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path)
