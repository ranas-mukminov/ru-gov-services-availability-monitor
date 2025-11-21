# 📊 RU Gov Services Availability Monitor

[![CI](https://github.com/ranas-mukminov/ru-gov-services-availability-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/ranas-mukminov/ru-gov-services-availability-monitor/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

🇬🇧 English | 🇷🇺 [Русская версия](README.ru.md)

**Author:** [Ranas Mukminov](https://github.com/ranas-mukminov) | **Website:** [https://run-as-daemon.ru](https://run-as-daemon.ru)

Distributed monitoring system for tracking availability and performance of Russian federal government online services. Designed for companies, MSPs, and IT departments that depend on government portals and need proactive alerting when services degrade or become unavailable.

## Overview

RU Gov Services Availability Monitor is a lightweight, Python-based solution for passive monitoring of public government services such as Gosuslugi, Tax Service portals, and other federal websites. The system uses a distributed agent architecture to measure availability, latency, and TLS certificate health from multiple geographic locations across Russia.

Unlike traditional monitoring tools, this project is specifically tailored for:
- **Business dependency tracking**: Monitor services your operations rely on (authentication, tax reporting, license validation).
- **Multi-region visibility**: Deploy agents in different cities to detect regional outages.
- **Observability integration**: Store metrics in SQLite (MVP) with plans for Prometheus export and Grafana dashboards.
- **Legal compliance**: Passive checks only—no load testing, no circumvention, respecting robots.txt and rate limits.

## Key Features

- **Distributed agent architecture** — Run agents in Moscow, St. Petersburg, and other regions to detect localized outages.
- **Passive HTTP/HTTPS checks** — Non-intrusive GET/HEAD requests with configurable intervals (default: 60 seconds).
- **TLS certificate validation** — Track expiration dates and cipher suite changes.
- **Central collector API** — Agents report metrics to a FastAPI-based collector with SQLite storage.
- **Incident reporting** — Generate reports summarizing downtime, latency spikes, and error rates.
- **Configuration as code** — YAML-based configuration for services, regions, and agent assignments.
- **CI/CD ready** — Automated testing, linting (Black, Ruff), and security scanning (Bandit, pip-audit).
- **Low resource footprint** — Runs on minimal VMs or cloud instances (1 vCPU, 512 MB RAM per agent).

## Architecture / Components

The system consists of three main components:

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Agent (MSK)   │────────▶│                 │◀────────│   Agent (SPB)   │
│  HTTP Client    │  POST   │  Collector API  │  POST   │  HTTP Client    │
│  Periodic Checks│         │  (FastAPI)      │         │  Periodic Checks│
└─────────────────┘         └────────┬────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ SQLite Storage  │
                            │  (monitor.db)   │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Report Generator│
                            │   (CLI tool)    │
                            └─────────────────┘
```

**Components:**
1. **Agent** — Runs periodic checks against configured services, measures latency and availability, reports results to collector.
2. **Collector** — REST API that receives metrics from agents, stores them in SQLite database.
3. **Report Generator** — CLI tool to analyze stored metrics and produce incident summaries.

## Requirements

### Operating System
- **Linux**: Ubuntu 22.04/24.04, Debian 11/12, Rocky Linux 9, or any modern distribution
- **Python**: 3.10 or higher (3.11 recommended)

### System Resources
- **Agent**: 512 MB RAM, 1 vCPU, 100 MB disk space per agent
- **Collector**: 1 GB RAM, 1 vCPU, 1 GB disk space (grows with metrics retention)

### Network
- Outbound HTTPS (443) access to monitored services
- Inbound HTTP (default port 8080) for collector if agents are remote
- Recommended: firewall rules to restrict collector access to known agent IPs

### Dependencies
All Python dependencies are managed via `pyproject.toml`:
- `httpx` — Async HTTP client for service checks
- `pydantic` — Configuration validation
- `fastapi` + `uvicorn` — Collector REST API
- `click` — CLI interface
- `PyYAML` — Configuration file parsing

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ranas-mukminov/ru-gov-services-availability-monitor.git
cd ru-gov-services-availability-monitor
```

### 2. Set Up Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Configure Services and Regions
Edit configuration files in `configs/`:

```bash
# Define services to monitor
nano configs/services.yml

# Define monitoring regions
nano configs/regions.yml

# Configure agent settings
nano configs/agent.yml

# Configure collector settings
nano configs/collector.yml
```

### 4. Start the Collector
```bash
ru-gov-monitor run-collector --config-dir ./configs
```
The collector API will start on `http://0.0.0.0:8080`.

### 5. Start an Agent
In a separate terminal (or on a remote machine):
```bash
ru-gov-monitor run-agent --config-dir ./configs
```

### 6. Generate a Report
After agents have collected some metrics:
```bash
ru-gov-monitor generate-report --db-path ./data/monitor.db
```

## Detailed Installation

### Installation on Ubuntu / Debian

```bash
# Install Python 3.10+ if not already installed
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# Clone repository
git clone https://github.com/ranas-mukminov/ru-gov-services-availability-monitor.git
cd ru-gov-services-availability-monitor

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .

# Verify installation
ru-gov-monitor --help
```

### Installation on RHEL / Rocky / Alma

```bash
# Install Python 3.10+
sudo dnf install -y python3 python3-pip git

# Clone repository
git clone https://github.com/ranas-mukminov/ru-gov-services-availability-monitor.git
cd ru-gov-services-availability-monitor

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .
```

### Running as a Systemd Service

Create a systemd unit file for the collector:

```bash
sudo nano /etc/systemd/system/ru-gov-monitor-collector.service
```

```ini
[Unit]
Description=RU Gov Services Monitor Collector
After=network.target

[Service]
Type=simple
User=monitoring
WorkingDirectory=/opt/ru-gov-monitor
ExecStart=/opt/ru-gov-monitor/.venv/bin/ru-gov-monitor run-collector --config-dir /opt/ru-gov-monitor/configs
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ru-gov-monitor-collector
sudo systemctl status ru-gov-monitor-collector
```

Repeat the same process for agents, replacing `run-collector` with `run-agent`.

## Configuration

All configuration is stored in YAML files under the `configs/` directory.

### services.yml

Defines government services to monitor:

```yaml
services:
  - id: "gosuslugi"
    name: "Public Services Portal"
    url: "https://www.gosuslugi.ru"
    expected_status: 200
    tags: ["federal", "critical"]

  - id: "nalog"
    name: "Tax Service"
    url: "https://www.nalog.gov.ru"
    expected_status: 200
    tags: ["federal", "finance"]
```

**Fields:**
- `id` — Unique identifier for the service
- `name` — Human-readable name
- `url` — Full URL to check (must be publicly accessible)
- `expected_status` — Expected HTTP status code (default: 200)
- `tags` — Optional labels for filtering and reporting

### regions.yml

Defines monitoring regions:

```yaml
regions:
  - id: "msk-1"
    name: "Moscow DC 1"
    location: "Moscow, Russia"

  - id: "spb-1"
    name: "St. Petersburg DC 1"
    location: "St. Petersburg, Russia"
```

### agent.yml

Configures agent behavior:

```yaml
agent:
  region_id: "msk-1"
  collector_url: "http://collector.example.com:8080"
  services:
    - "gosuslugi"
    - "nalog"
  max_concurrency: 5
```

**Fields:**
- `region_id` — Which region this agent represents (must match `regions.yml`)
- `collector_url` — Base URL of the collector API
- `services` — List of service IDs to monitor (from `services.yml`)
- `max_concurrency` — Maximum number of concurrent checks

### collector.yml

Configures the collector API:

```yaml
collector:
  host: "0.0.0.0"
  port: 8080
  storage_path: "./data/monitor.db"
```

**Fields:**
- `host` — Bind address (use `0.0.0.0` to accept connections from remote agents)
- `port` — API port
- `storage_path` — Path to SQLite database file

## Usage & Common Tasks

### Validate Configuration

Before running agents or collectors, validate your configuration files:

```bash
ru-gov-monitor validate-config --config-dir ./configs
```

### Start Components Manually

**Collector:**
```bash
ru-gov-monitor run-collector --config-dir ./configs
```

**Agent:**
```bash
ru-gov-monitor run-agent --config-dir ./configs
```

### Generate Incident Reports

```bash
ru-gov-monitor generate-report --db-path ./data/monitor.db
```

Sample output:
```
Incident Report
===============
Service: gosuslugi
- Total checks: 1440
- Availability: 99.8%
- Average latency: 123.4ms
- Incidents: 2
  - 2025-11-20 14:23:00 - 14:25:00 (2 min) - HTTP 503
  - 2025-11-20 18:10:00 - 18:10:30 (30 sec) - Timeout
```

### Access Collector API

The collector exposes a REST API:

**Submit metrics (used by agents):**
```bash
POST http://localhost:8080/api/v1/metrics
Content-Type: application/json

{
  "service_id": "gosuslugi",
  "timestamp": "2025-11-21T12:00:00Z",
  "status_code": 200,
  "latency_ms": 123.4,
  "available": true,
  "region_id": "msk-1"
}
```

**Health check:**
```bash
curl http://localhost:8080/health
```

## Update / Upgrade

To update the monitoring system to the latest version:

```bash
cd /path/to/ru-gov-services-availability-monitor
git pull origin main
source .venv/bin/activate
pip install -e .
```

**Restart services:**
```bash
sudo systemctl restart ru-gov-monitor-collector
sudo systemctl restart ru-gov-monitor-agent
```

**Breaking changes:**
- Check [CHANGELOG.md](CHANGELOG.md) for migration notes before upgrading.
- Database schema changes may require manual migration in future versions.

## Logs, Monitoring, Troubleshooting

### Log Locations

**Systemd services:**
```bash
journalctl -u ru-gov-monitor-collector -f
journalctl -u ru-gov-monitor-agent -f
```

**Manual runs:**
Logs are printed to stdout/stderr. Redirect to a file if needed:
```bash
ru-gov-monitor run-agent --config-dir ./configs >> /var/log/ru-gov-agent.log 2>&1
```

### Common Issues

**Problem: Agent cannot connect to collector**
```
ERROR: Failed to report to collector: Connection refused
```
**Solution:**
- Check `collector_url` in `agent.yml` is correct.
- Ensure collector is running: `curl http://collector-host:8080/health`
- Verify firewall rules allow traffic on port 8080.

**Problem: Port 8080 already in use**
```
ERROR: [Errno 98] Address already in use
```
**Solution:**
- Change `port` in `collector.yml` to another value (e.g., 8081).
- Or stop the conflicting service: `sudo lsof -i :8080`

**Problem: No metrics in database**
```bash
ru-gov-monitor generate-report --db-path ./data/monitor.db
# Output: No metrics found
```
**Solution:**
- Check agent is running and configured correctly.
- Verify `collector_url` points to the running collector.
- Inspect collector logs for errors.

**Problem: TLS certificate validation errors**
```
ERROR: SSL verification failed
```
**Solution:**
- Update system CA certificates: `sudo update-ca-certificates`
- If monitoring a test service with self-signed cert, configure `--no-verify-ssl` (NOT recommended for production).

## Security Notes

> **⚠️ IMPORTANT:** This tool performs passive monitoring only. Operators are fully responsible for compliance with Russian federal law and the Terms of Service of monitored resources.

### Security Checklist

1. **Restrict collector access**: Use firewall rules or reverse proxy with authentication to prevent unauthorized metric submission.
2. **Secure agent-collector communication**: Consider using HTTPS with TLS certificates for production deployments.
3. **Rate limiting**: Configure check intervals responsibly (default 60 seconds). Do not create excessive load.
4. **Respect robots.txt**: Ensure monitored URLs are not disallowed by `robots.txt`.
5. **No secrets in configs**: Never commit real URLs or API keys to version control. Use environment variables or secret management.
6. **Apply security updates**: Regularly update Python dependencies:
   ```bash
   pip install --upgrade -e .[dev]
   pip-audit
   ```

### Legal Compliance

- This system performs HTTP GET/HEAD requests to public URLs. It does not bypass WAFs, CAPTCHAs, or authentication.
- Operators should coordinate with service owners if using this for commercial monitoring.
- See [docs/security.ru.md](docs/security.ru.md) for detailed legal considerations (Russian).

## Project Structure

```
ru-gov-services-availability-monitor/
├── configs/               # YAML configuration files
│   ├── agent.yml
│   ├── collector.yml
│   ├── regions.yml
│   └── services.yml
├── src/                   # Python source code
│   └── ru_gov_services_availability_monitor/
│       ├── agent/         # Agent logic (HTTP client, runner)
│       ├── collector/     # Collector API and storage
│       ├── config/        # Configuration models
│       ├── reports/       # Report generation
│       └── cli.py         # CLI entry point
├── tests/                 # Unit and integration tests
├── docs/                  # Additional documentation
│   └── security.ru.md
├── .github/workflows/     # CI/CD pipeline
│   └── ci.yml
├── LICENSE                # Apache-2.0 license
├── pyproject.toml         # Python project metadata
└── README.md              # This file
```

## Contributing

Contributions are welcome! To contribute:

1. **Fork the repository** on GitHub.
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow PEP 8 style (enforced by Black and Ruff).
   - Add tests for new functionality.
   - Update documentation if needed.
4. **Run checks locally**:
   ```bash
   black .
   ruff check .
   pytest
   ```
5. **Commit your changes**: Use clear, descriptive commit messages.
6. **Push and open a Pull Request** against the `main` branch.

### Code Style

- **Python**: Use Black formatter (line length 120), Ruff linter.
- **YAML**: 2-space indentation, alphabetical keys where applicable.
- **Commit messages**: Start with a verb (e.g., "Add feature", "Fix bug").

## Roadmap

Planned features for future releases:

- [ ] Prometheus exporter for metrics
- [ ] Grafana dashboard templates
- [ ] PostgreSQL/TimescaleDB support for large-scale deployments
- [ ] Web UI for configuration and visualization
- [ ] Alerting via Telegram, email, webhooks
- [ ] Response body validation (keyword matching)
- [ ] DNS resolution tracking

See [GitHub Issues](https://github.com/ranas-mukminov/ru-gov-services-availability-monitor/issues) for the full backlog.

## License

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

```
Copyright 2025 run-as-daemon.ru

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Author and Commercial Support

**Author:** [Ranas Mukminov](https://github.com/ranas-mukminov)

For production-grade monitoring setups, custom integrations, infrastructure audits, and ongoing SRE support, visit **[https://run-as-daemon.ru](https://run-as-daemon.ru)** or contact the author via GitHub.

Services offered:
- **Monitoring and observability infrastructure** — Prometheus, Grafana, Loki, distributed tracing.
- **Incident response processes** — SLO/SLA definition, on-call automation.
- **DevOps consulting** — CI/CD, infrastructure as code, security hardening.
