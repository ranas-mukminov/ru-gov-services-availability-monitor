import asyncio
import logging
from typing import List
from ..config.models import ServiceConfig, AgentConfig
from .http_client import HttpClient, CheckResult

logger = logging.getLogger(__name__)


class AgentRunner:
    def __init__(self, config: AgentConfig, services: List[ServiceConfig]):
        self.config = config
        # Filter services based on agent config
        self.services = [s for s in services if s.id in config.services]
        self.client = HttpClient()
        self.running = False

    async def run_check(self, service: ServiceConfig):
        logger.info(f"Checking service: {service.name} ({service.url})")
        result = await self.client.check_service(service.id, str(service.url))
        await self.report_result(result)

    async def report_result(self, result: CheckResult):
        # In a real implementation, this would POST to the collector.
        # For MVP, we'll just log it or print it.
        # We will implement the collector client later.
        logger.info(f"Result for {result.service_id}: Available={result.available}, Latency={result.latency_ms:.2f}ms")

        # TODO: Send to collector
        if self.config.collector_url:
            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    payload = {
                        "service_id": result.service_id,
                        "timestamp": result.timestamp,
                        "status_code": result.status_code,
                        "latency_ms": result.latency_ms,
                        "available": result.available,
                        "error": result.error,
                        "tls_info": result.tls_info,
                        "region_id": self.config.region_id,
                    }
                    await client.post(f"{self.config.collector_url}/api/v1/metrics", json=payload)
            except Exception as e:
                logger.error(f"Failed to report to collector: {e}")

    async def start(self):
        self.running = True
        logger.info(f"Agent started in region {self.config.region_id}. Monitoring {len(self.services)} services.")

        while self.running:
            tasks = []
            for service in self.services:
                tasks.append(self.run_check(service))

            if tasks:
                await asyncio.gather(*tasks)

            # Simple sleep for now. In production, use a proper scheduler.
            await asyncio.sleep(60)  # Default loop interval

    def stop(self):
        self.running = False
