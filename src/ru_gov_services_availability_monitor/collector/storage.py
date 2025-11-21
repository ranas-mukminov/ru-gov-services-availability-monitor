import sqlite3
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class Metric:
    service_id: str
    region_id: str
    timestamp: float
    status_code: Optional[int]
    latency_ms: float
    available: bool
    error: Optional[str]
    tls_info: Optional[Dict[str, Any]]


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                region_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                status_code INTEGER,
                latency_ms REAL,
                available BOOLEAN,
                error TEXT,
                tls_info TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def save_metric(self, metric: Metric):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO metrics (service_id, region_id, timestamp, status_code, latency_ms, available, error, tls_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metric.service_id,
                metric.region_id,
                metric.timestamp,
                metric.status_code,
                metric.latency_ms,
                metric.available,
                metric.error,
                json.dumps(metric.tls_info) if metric.tls_info else None,
            ),
        )
        conn.commit()
        conn.close()

    def get_metrics(self, service_id: Optional[str] = None, limit: int = 100) -> List[Metric]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        query = "SELECT * FROM metrics"
        params = []
        if service_id:
            query += " WHERE service_id = ?"
            params.append(service_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        return [
            Metric(
                service_id=row["service_id"],
                region_id=row["region_id"],
                timestamp=row["timestamp"],
                status_code=row["status_code"],
                latency_ms=row["latency_ms"],
                available=bool(row["available"]),
                error=row["error"],
                tls_info=(
                    json.loads(row["tls_info"]) if row["tls_info"] else None
                ),
            )
            for row in rows
        ]
