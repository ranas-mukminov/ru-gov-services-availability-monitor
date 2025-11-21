from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class ServiceConfig(BaseModel):
    id: str
    name: str
    url: HttpUrl
    expected_status: int = 200
    check_interval_seconds: int = 300
    tags: List[str] = Field(default_factory=list)


class RegionConfig(BaseModel):
    id: str
    name: str
    location: str


class AgentConfig(BaseModel):
    region_id: str
    collector_url: HttpUrl
    services: List[str]  # List of Service IDs to monitor
    max_concurrency: int = 5


class CollectorConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8080
    storage_path: str = "./data/monitor.db"
    auth_token: Optional[str] = None


class GlobalConfig(BaseModel):
    services: List[ServiceConfig]
    regions: List[RegionConfig]
    agent: Optional[AgentConfig] = None
    collector: Optional[CollectorConfig] = None
