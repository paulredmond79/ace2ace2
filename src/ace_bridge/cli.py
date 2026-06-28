"""ACE Bridge CLI — entry point for all bridge commands.

Usage:
    bridge --help
    bridge start --config config/config.yaml
    bridge start --config config/config.yaml --simulate
    bridge sniff-rs485 --port /dev/ttyUSB0 --baud 115200
    bridge sniff-usb
    bridge inspect-usb
    bridge decode --input captures/session.jsonl
    bridge decode-hex "AA 01 04 10"
    bridge capture --output captures/
    bridge replay --input captures/session.jsonl --simulate
    bridge status
    bridge discover
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ace_bridge.bridge.bridge import Bridge
from ace_bridge.config.loader import load_config
from ace_bridge.logging.setup import setup_logging
from ace_bridge.utils.crc import try_all_crcs
from ace_bridge.utils.hex_dump import hex_dump, parse_hex_str

app = typer.Typer(
    name="bridge",
    help="ACE Bridge — Anycubic ACE Pro ↔ ACE 2 Pro protocol bridge",
    no_args_is_help=True,
)
console = Console()
logger = logging.getLogger(__name__)


@app.command()
def start(
    config: Path | None = typer.Option(None, "--config", "-c", help="YAML config file"),
    simulate: bool = typer.Option(False, "--simulate", help="Run in simulation mode (no hardware)"),
    log_level: str = typer.Option("INFO", "--log-level", help="Log level"),
    trace_packets: bool = typer.Option(False, "--trace-packets", help="Log every raw packet"),
    read_only: bool = typer.Option(True, "--read-only/--no-read-only", help="Read-only (no TX)"),
) -> None:
    """Start the ACE Bridge.

    Runs the full bridge: RS485 upstream ↔ ACE 2 Pro emulator ↔ translator ↔ ACE Pro USB.

    Start with --simulate to test without hardware.
    Start with --read-only (default) to sniff without transmitting.
    """
    setup_logging(level=log_level)
    cfg = load_config(config)

    if simulate:
        cfg.bridge.simulate = True
    if not read_only:
        cfg.bridge.read_only = False

    console.print(
        Panel(
            f"[bold green]ACE Bridge starting[/]\n"
            f"simulate={cfg.bridge.simulate}  read_only={cfg.bridge.read_only}",
            title="ACE Bridge",
        )
    )

    bridge = Bridge(cfg)

    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted — stopping bridge[/]")


@app.command(name="sniff-rs485")
def sniff_rs485(
    port: str = typer.Option("/dev/ttyAMA0", "--port", "-p", help="RS485 serial port"),
    baud: int = typer.Option(115200, "--baud", "-b", help="Baud rate (⚠️ unknown — try multiple)"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Save to capture file"),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Sniff RS485 traffic and print hex dumps.

    Reads in receive-only mode. Does NOT transmit.

    ⚠️ Baud rate is unknown — try: 9600, 19200, 57600, 115200, 250000, 500000
    Look for clean framing (no framing errors, consistent packet lengths).
    """
    setup_logging(level=log_level)
    console.print(f"[cyan]Sniffing RS485 on {port} at {baud} baud (receive only)[/]")
    console.print("[yellow]⚠️  Baud rate may be wrong — see docs/Unknowns.md RS-1[/]")

    # TODO: Implement with RS485Driver in read-only mode + capture writer
    # For now, show the placeholder message
    console.print(
        "[red]RS485 sniff not yet implemented.[/]\n"
        "Milestone 1 (capture tooling) is required first.\n"
        "See docs/Roadmap.md"
    )
    raise typer.Exit(code=1)


@app.command(name="sniff-usb")
def sniff_usb(
    vid: str | None = typer.Option(None, "--vid", help="USB Vendor ID (hex, e.g. 0x1234)"),
    pid: str | None = typer.Option(None, "--pid", help="USB Product ID (hex)"),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Sniff USB traffic from/to the ACE Pro.

    If VID/PID are not specified, lists all connected USB devices.
    ⚠️ ACE Pro VID/PID is unknown — run 'bridge inspect-usb' first.
    """
    setup_logging(level=log_level)
    console.print("[cyan]USB sniff[/]")

    if vid is None or pid is None:
        console.print("[yellow]No VID/PID specified — running inspect-usb instead[/]")
        _inspect_usb()
        return

    # TODO: Implement USB sniff with pyusb
    console.print("[red]USB sniff not yet implemented. See docs/Roadmap.md milestone 2.[/]")
    raise typer.Exit(code=1)


@app.command(name="inspect-usb")
def inspect_usb(
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """List connected USB devices and dump descriptors.

    Run with ACE Pro connected to identify its VID/PID and endpoints.
    This resolves docs/Unknowns.md USB-1, USB-2, USB-3.
    """
    setup_logging(level=log_level)
    _inspect_usb()


def _inspect_usb() -> None:
    """Internal implementation of USB device inspection."""
    try:
        import usb.core  # type: ignore[import]
        import usb.util  # type: ignore[import]
    except ImportError as exc:
        console.print("[red]pyusb not installed. Run: pip install pyusb[/]")
        raise typer.Exit(code=1) from exc

    devices = list(usb.core.find(find_all=True))
    if not devices:
        console.print("[yellow]No USB devices found.[/]")
        return

    table = Table(title="Connected USB Devices", show_lines=True)
    table.add_column("Bus", style="dim")
    table.add_column("Addr", style="dim")
    table.add_column("VID", style="cyan")
    table.add_column("PID", style="cyan")
    table.add_column("Manufacturer")
    table.add_column("Product")

    for dev in devices:
        try:
            manufacturer = usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else ""
            product = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else ""
        except Exception:
            manufacturer = product = ""
        table.add_row(
            str(dev.bus),
            str(dev.address),
            f"0x{dev.idVendor:04X}",
            f"0x{dev.idProduct:04X}",
            manufacturer,
            product,
        )

    console.print(table)
    console.print(
        "\n[yellow]Identify the ACE Pro in the list above, then update config/config.yaml "
        "with the correct VID and PID.[/]"
    )


@app.command()
def decode(
    input: Path = typer.Argument(..., help="Capture file (.jsonl)"),
    output: str | None = typer.Option(None, "--output", help="Output format: json, csv, hex"),
    interface: str | None = typer.Option(None, "--interface", "-i", help="Filter: rs485 or usb"),
    direction: str | None = typer.Option(None, "--direction", "-d", help="Filter: rx or tx"),
) -> None:
    """Decode and display a capture file.

    Shows hex dumps of all packets with timestamps, direction, and decoded fields.
    """
    if not input.exists():
        console.print(f"[red]File not found: {input}[/]")
        raise typer.Exit(code=1)

    from ace_bridge.capture.reader import read_capture
    from ace_bridge.utils.hex_dump import hex_dump

    count = 0
    for packet in read_capture(input):
        if interface and packet.interface != interface:
            continue
        if direction and packet.direction != direction:
            continue
        ts = packet.wall_time.strftime("%H:%M:%S.%f")
        label = f"[{packet.interface.upper()} {packet.direction.upper()}] {ts}"
        console.print(f"\n[bold]{label}[/]")
        console.print(hex_dump(packet.raw, label=None))
        count += 1

    console.print(f"\n[dim]{count} packets[/]")


@app.command(name="decode-hex")
def decode_hex(
    hex_string: str = typer.Argument(..., help="Hex string to decode (e.g. 'AA 01 04 10')"),
) -> None:
    """Decode a single hex string and show CRC candidates.

    Useful for quick analysis of individual captured packets.
    """
    try:
        data = parse_hex_str(hex_string)
    except ValueError as e:
        console.print(f"[red]Invalid hex string: {e}[/]")
        raise typer.Exit(code=1) from e

    console.print(hex_dump(data, label=f"Input ({len(data)} bytes)"))

    # Show all CRC candidates - helpful for identifying which algorithm is in use
    if len(data) >= 2:
        # Assume last 1-2 bytes are CRC; compute over remaining bytes
        payload_1 = data[:-1]
        data[:-2]

        table = Table(title="CRC Candidates (last byte)", show_lines=True)
        table.add_column("Algorithm")
        table.add_column("Computed")
        table.add_column("Last byte of packet")
        last = data[-1]
        for algo, val in try_all_crcs(payload_1).items():
            match = "✓" if val == last else ""
            table.add_row(algo, f"0x{val:04X}", f"0x{last:02X} {match}")
        console.print(table)


@app.command()
def capture(
    output: Path = typer.Option(Path("captures/"), "--output", "-o", help="Output directory"),
    rs485_port: str = typer.Option("/dev/ttyAMA0", "--rs485-port"),
    rs485_baud: int = typer.Option(115200, "--rs485-baud"),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Capture packets from both RS485 and USB interfaces simultaneously.

    Saves to captures/<timestamp>.jsonl
    """
    setup_logging(level=log_level)
    # TODO: Implement once RS485 and USB sniff are working (milestones 1-2)
    console.print("[red]Simultaneous capture not yet implemented. See docs/Roadmap.md.[/]")
    raise typer.Exit(code=1)


@app.command()
def replay(
    input: Path = typer.Argument(..., help="Capture file to replay"),
    simulate: bool = typer.Option(True, "--simulate/--real", help="Use simulator or real hardware"),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Replay a capture file for regression testing.

    In --simulate mode (default), packets are fed to the bridge simulator.
    In --real mode, packets are transmitted on the real interface.
    """
    setup_logging(level=log_level)
    if not input.exists():
        console.print(f"[red]File not found: {input}[/]")
        raise typer.Exit(code=1)
    # TODO: Implement replay engine (milestone 4+)
    console.print("[red]Replay not yet implemented. See docs/Roadmap.md milestone 4.[/]")
    raise typer.Exit(code=1)


@app.command()
def status(
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Show current bridge status (if bridge is running).

    ⚠️ TODO: Implement IPC between CLI and running bridge process.
    """
    console.print("[yellow]Bridge status IPC not yet implemented.[/]")
    console.print("For now, check bridge process logs.")
    raise typer.Exit(code=1)


@app.command()
def discover(
    rs485_port: str = typer.Option("/dev/ttyAMA0", "--port"),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Discover ACE devices on the RS485 bus.

    Passively listens and attempts to identify all responding devices.
    ⚠️ Requires baud rate to be correct — see docs/Unknowns.md RS-1.
    """
    setup_logging(level=log_level)
    console.print("[yellow]Discover not yet implemented. Requires RS485 protocol knowledge.[/]")
    console.print("Capture first, then implement. See docs/Roadmap.md milestone 3.")
    raise typer.Exit(code=1)


@app.command()
def simulate(
    scenario: str = typer.Option("idle", "--scenario", "-s", help="Scenario name"),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    """Run bridge in simulation mode with a scripted scenario.

    Useful for testing the emulator and translator without hardware.
    """
    setup_logging(level=log_level)
    console.print(f"[cyan]Running simulation scenario: {scenario}[/]")
    # TODO: Implement scenario runner (milestone 7)
    console.print(
        "[yellow]Simulation scenarios not yet implemented. See docs/Roadmap.md milestone 7.[/]"
    )
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
