import click
import asyncio
import uvicorn
from pathlib import Path
from .config.loader import load_config
from .agent.runner import AgentRunner
from .collector.api import app as collector_app
from .reports.incidents import generate_incident_report
from .collector.storage import Storage


@click.group()
def main():
    """RU Gov Services Availability Monitor CLI"""
    pass


@main.command()
@click.option("--config-dir", type=click.Path(exists=True), required=True, help="Path to configuration directory")
def validate_config(config_dir):
    """Validate configuration files"""
    try:
        config = load_config(Path(config_dir))
        click.echo("Configuration is valid.")
        click.echo(f"Found {len(config.services)} services and {len(config.regions)} regions.")
    except Exception as e:
        click.echo(f"Configuration error: {e}", err=True)
        exit(1)


@main.command()
@click.option("--config-dir", type=click.Path(exists=True), required=True, help="Path to configuration directory")
def run_agent(config_dir):
    """Run the monitoring agent"""
    config = load_config(Path(config_dir))
    if not config.agent:
        click.echo("Agent configuration not found.", err=True)
        exit(1)

    runner = AgentRunner(config.agent, config.services)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(runner.start())
    except KeyboardInterrupt:
        runner.stop()
        click.echo("Agent stopped.")


@main.command()
@click.option("--config-dir", type=click.Path(exists=True), required=True, help="Path to configuration directory")
def run_collector(config_dir):
    """Run the collector API"""
    config = load_config(Path(config_dir))
    if not config.collector:
        click.echo("Collector configuration not found.", err=True)
        exit(1)

    # Ensure data directory exists
    Path(config.collector.storage_path).parent.mkdir(parents=True, exist_ok=True)

    uvicorn.run(collector_app, host=config.collector.host, port=config.collector.port)


@main.command()
@click.option("--db-path", type=click.Path(exists=True), required=True, help="Path to sqlite database")
def generate_report(db_path):
    """Generate incident report from database"""
    storage = Storage(db_path)
    metrics = storage.get_metrics(limit=1000)
    report = generate_incident_report(metrics)
    click.echo(report)


if __name__ == "__main__":
    main()
