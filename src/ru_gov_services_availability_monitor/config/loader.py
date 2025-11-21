import yaml
from pathlib import Path
from typing import Dict, Any
from .models import GlobalConfig, ServiceConfig, RegionConfig, AgentConfig, CollectorConfig


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(config_dir: Path) -> GlobalConfig:
    services_data = load_yaml(config_dir / "services.yml")
    regions_data = load_yaml(config_dir / "regions.yml")

    # Optional configs
    agent_data = {}
    if (config_dir / "agent.yml").exists():
        agent_data = load_yaml(config_dir / "agent.yml")

    collector_data = {}
    if (config_dir / "collector.yml").exists():
        collector_data = load_yaml(config_dir / "collector.yml")

    return GlobalConfig(
        services=[ServiceConfig(**s) for s in services_data.get("services", [])],
        regions=[RegionConfig(**r) for r in regions_data.get("regions", [])],
        agent=AgentConfig(**agent_data.get("agent")) if agent_data else None,
        collector=CollectorConfig(**collector_data.get("collector")) if collector_data else None,
    )
