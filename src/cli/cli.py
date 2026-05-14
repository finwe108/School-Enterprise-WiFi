import click
from typing import Optional
from ..core.wifi_manager import WiFiManager
from ..core.network_model import SavedProfile, SecurityType
from ..storage.database import WiFiDatabase


@click.group()
def cli():
    """WiFi Manager - Cross-platform WiFi management tool."""
    pass


@cli.command()
def scan():
    """Scan for available WiFi networks."""
    click.echo("Scanning for WiFi networks...")
    
    try:
        manager = WiFiManager.get_instance()
        networks = manager.scan_networks()
        
        if not networks:
            click.echo("No networks found.")
            return
        
        click.echo(f"\nFound {len(networks)} network(s):\n")
        
        for i, network in enumerate(networks, 1):
            signal_bar = "█" * (network.signal_strength // 10) + "░" * ((100 - network.signal_strength) // 10)
            click.echo(f"{i}. {network.ssid}")
            click.echo(f"   Signal: {signal_bar} {network.signal_strength}%")
            click.echo(f"   Security: {network.security.value}")
            click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("ssid")
@click.option("--password", "-p", prompt=True, hide_input=True, default="", help="WiFi password")
def connect(ssid: str, password: str):
    """Connect to a WiFi network."""
    click.echo(f"Connecting to {ssid}...")
    
    try:
        manager = WiFiManager.get_instance()
        db = WiFiDatabase()
        
        password_arg = password if password else None
        success = manager.connect(ssid, password_arg)
        
        if success:
            click.echo(f"✓ Successfully connected to {ssid}")
            db.record_connection(ssid, True)
        else:
            click.echo(f"✗ Failed to connect to {ssid}", err=True)
            db.record_connection(ssid, False)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
def disconnect():
    """Disconnect from current WiFi network."""
    click.echo("Disconnecting...")
    
    try:
        manager = WiFiManager.get_instance()
        success = manager.disconnect()
        
        if success:
            click.echo("✓ Successfully disconnected")
        else:
            click.echo("✗ Failed to disconnect", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
def status():
    """Show current WiFi connection status."""
    try:
        manager = WiFiManager.get_instance()
        network = manager.get_current_connection()
        
        if network:
            click.echo(f"Connected to: {network.ssid}")
            click.echo(f"Signal: {network.signal_strength}%")
        else:
            click.echo("Not connected to any network")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
def list_saved():
    """List all saved network profiles."""
    click.echo("Saved networks:\n")
    
    try:
        db = WiFiDatabase()
        profiles = db.get_all_profiles()
        
        if not profiles:
            click.echo("No saved profiles.")
            return
        
        for i, profile in enumerate(profiles, 1):
            auto_text = " (Auto-connect)" if profile.auto_connect else ""
            click.echo(f"{i}. {profile.ssid}{auto_text}")
            click.echo(f"   Security: {profile.security.value}")
            click.echo(f"   Connected: {profile.connection_count} times")
            if profile.last_connected:
                click.echo(f"   Last: {profile.last_connected}")
            click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("ssid")
def add_profile(ssid: str):
    """Save a network profile."""
    click.echo(f"Saving profile for {ssid}...")
    
    try:
        db = WiFiDatabase()
        profile = SavedProfile(
            ssid=ssid,
            security=SecurityType.UNKNOWN,
            auto_connect=False
        )
        
        if db.add_profile(profile):
            click.echo(f"✓ Profile saved for {ssid}")
        else:
            click.echo(f"✗ Profile already exists", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("ssid")
def remove_profile(ssid: str):
    """Remove a saved network profile."""
    if click.confirm(f"Remove profile for {ssid}?"):
        try:
            db = WiFiDatabase()
            manager = WiFiManager.get_instance()
            
            db.delete_profile(ssid)
            manager.forget_network(ssid)
            
            click.echo(f"✓ Profile removed for {ssid}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("ssid")
def toggle_autoconnect(ssid: str):
    """Toggle auto-connect for a saved profile."""
    try:
        db = WiFiDatabase()
        profile = db.get_profile(ssid)
        
        if not profile:
            click.echo(f"Profile not found for {ssid}", err=True)
            return
        
        profile.auto_connect = not profile.auto_connect
        db.update_profile(profile)
        
        status = "enabled" if profile.auto_connect else "disabled"
        click.echo(f"✓ Auto-connect {status} for {ssid}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()
