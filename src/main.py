#!/usr/bin/env python3
import sys
import click
from .cli.cli import cli as cli_group


@click.group()
def main():
    """WiFi Manager - Cross-platform WiFi management tool."""
    pass


@main.command()
def gui():
    """Launch the graphical user interface."""
    try:
        from .gui.main_window import run_gui
        run_gui()
    except Exception as e:
        click.echo(f"Error launching GUI: {e}", err=True)
        sys.exit(1)


# Re-export CLI commands
main.add_command(cli_group, "cli")


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ["--help", "-h"]:
        click.echo("WiFi Manager - Cross-platform WiFi management")
        click.echo("\nUsage: python -m src.main [OPTIONS] COMMAND [ARGS]...")
        click.echo("\nCommands:")
        click.echo("  gui                 Launch the graphical user interface")
        click.echo("  cli scan            Scan for available networks")
        click.echo("  cli connect SSID    Connect to a network")
        click.echo("  cli disconnect      Disconnect from current network")
        click.echo("  cli status          Show connection status")
        click.echo("  cli list-saved      List saved profiles")
        click.echo("  cli add-profile     Save a network profile")
        click.echo("  cli remove-profile  Remove a saved profile")
        click.echo("  cli toggle-autoconnect  Toggle auto-connect for a profile")
    else:
        main()
