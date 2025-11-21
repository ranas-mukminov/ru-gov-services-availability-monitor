import httpx
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CheckResult:
    service_id: str
    timestamp: float
    status_code: Optional[int]
    latency_ms: float
    available: bool
    error: Optional[str] = None
    tls_info: Optional[Dict[str, Any]] = None


class HttpClient:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.headers = {"User-Agent": "ru-gov-monitor/0.1.0 (passive-check; +https://run-as-daemon.ru)"}

    async def check_service(self, service_id: str, url: str) -> CheckResult:
        start_time = time.time()
        tls_info = {}

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=True) as client:
                response = await client.get(url, headers=self.headers)
                latency = (time.time() - start_time) * 1000

                # Extract basic TLS info if HTTPS
                if url.startswith("https://"):
                    # Note: httpx doesn't expose raw socket/SSL info easily in async mode without hooks.
                    # For MVP, we might skip detailed TLS extraction or do a separate sync check if needed.
                    # Or we can use response.extensions if available in newer versions.
                    # For now, we assume if we got here, SSL is valid (verify=True).
                    tls_info = {"valid": True, "protocol": response.http_version}

                return CheckResult(
                    service_id=service_id,
                    timestamp=start_time,
                    status_code=response.status_code,
                    latency_ms=latency,
                    available=True,
                    tls_info=tls_info,
                )
        except httpx.TimeoutException:
            return CheckResult(
                service_id=service_id,
                timestamp=start_time,
                status_code=None,
                latency_ms=(time.time() - start_time) * 1000,
                available=False,
                error="Timeout",
            )
        except httpx.RequestError as e:
            return CheckResult(
                service_id=service_id,
                timestamp=start_time,
                status_code=None,
                latency_ms=(time.time() - start_time) * 1000,
                available=False,
                error=str(e),
            )
        except Exception as e:
            return CheckResult(
                service_id=service_id,
                timestamp=start_time,
                status_code=None,
                latency_ms=(time.time() - start_time) * 1000,
                available=False,
                error=f"Unexpected error: {str(e)}",
            )
