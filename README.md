# ru-gov-services-availability-monitor

Distributed monitoring system for Russian government services availability.

## Overview

This project provides a lightweight, distributed monitoring solution designed to check the availability and latency of key Russian government online services (e.g., Gosuslugi, Nalog). It is intended for companies and MSPs that rely on these services and need to track their uptime from different regions.

**Key Features:**
- **Distributed Agents**: Run lightweight agents in multiple regions/clouds.
- **Passive Monitoring**: Performs non-intrusive HTTP/TLS health checks.
- **Central Collector**: Aggregates results into a single SQLite database (MVP).
- **Reporting**: Generates incident summaries and management reports.

## Installation

Requires Python 3.10+.

```bash
# Clone the repository
git clone https://github.com/your-org/ru-gov-services-availability-monitor.git
cd ru-gov-services-availability-monitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

## Usage

### 1. Configure
Copy the example configurations:
```bash
cp -r configs/ examples/
# Edit examples/services.yml, examples/regions.yml, etc.
```

### 2. Run Collector
```bash
ru-gov-monitor run-collector --config-dir examples/
```

### 3. Run Agent
```bash
ru-gov-monitor run-agent --config-dir examples/
```

### 4. Generate Report
```bash
ru-gov-monitor generate-report --db-path ./data/monitor.db
```

## Production Use & Consulting

> This project is maintained by **run-as-daemon.ru**.
> For production-ready observability setups, SRE processes, and support integrating this monitor into your incident management, visit [https://run-as-daemon.ru](https://run-as-daemon.ru).

## License

Apache-2.0
