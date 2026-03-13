#!/usr/bin/env python3
"""
R3D HUNT3R - CTF AI Agent CLI for SecDojo
Powered by OpenRouter (Free Tier)
"""

import os
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.columns import Columns
from rich import box

sys.path.insert(0, str(Path(__file__).parent))
from core.agent import (
    CTFAgent, load_labs, save_labs,
    FREE_MODELS, CHAT_MODELS, ALL_MODELS,
    list_sessions, delete_session
)

console = Console()

BANNER = """[bold red]
  ██████╗ ██████╗ ██████╗     ██╗  ██╗██╗   ██╗███╗   ██╗████████╗██████╗ ██████╗ 
 ██╔══██╗╚════██╗██╔══██╗    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝╚════██╗██╔══██╗
 ██████╔╝ █████╔╝██║  ██║    ███████║██║   ██║██╔██╗ ██║   ██║    █████╔╝██████╔╝
 ██╔══██╗ ╚═══██╗██║  ██║    ██╔══██║██║   ██║██║╚██╗██║   ██║    ╚═══██╗██╔══██╗
 ██║  ██║██████╔╝██████╔╝    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ██████╔╝██║  ██║
 ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝
[/bold red][dim]  CTF AI Agent — SecDojo Edition  |  Powered by OpenRouter (Free Tier)[/dim]
"""

STATUS_COLORS = {"solved": "green", "in_progress": "yellow", "not_started": "red"}
STATUS_ICONS  = {"solved": "✓", "in_progress": "⚡", "not_started": "○"}
LEVEL_COLORS  = {"basic": "blue", "intermediate": "yellow", "advanced": "red"}


def print_banner():
    console.print(BANNER)


def get_agent():
    try:
        return CTFAgent()
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)


def show_home_menu():
    print_banner()

    features = [
        ("[bold red]1[/bold red]  [white]CHAT[/white]",
         "[dim]Interactive AI session\nMemory across messages\nSave & resume sessions[/dim]"),
        ("[bold red]2[/bold red]  [white]ASK[/white]",
         "[dim]One-shot quick question\nNo session needed\nFast single answer[/dim]"),
        ("[bold red]3[/bold red]  [white]RECON[/white]",
         "[dim]Full recon plan for target\nnmap → enum → attack\nAll models in parallel[/dim]"),
        ("[bold red]4[/bold red]  [white]ANALYZE[/white]",
         "[dim]Paste tool output\nFinds attack vectors\nnmap/gobuster/linpeas...[/dim]"),
        ("[bold red]5[/bold red]  [white]EXPLOIT[/white]",
         "[dim]CVE lookup by service\nExploitDB + Metasploit\nExact exploit commands[/dim]"),
        ("[bold red]6[/bold red]  [white]PAYLOAD[/white]",
         "[dim]Reverse shells & webshells\nPrivesc one-liners\nMultiple variants + b64[/dim]"),
        ("[bold red]7[/bold red]  [white]WORDLIST[/white]",
         "[dim]Best wordlists per target\nTool + wordlist combos\nHashcat rules & strategy[/dim]"),
        ("[bold red]8[/bold red]  [white]SEARCH[/white]",
         "[dim]HackTricks knowledge\nGTFOBins entries\nTechnique deep-dives[/dim]"),
        ("[bold red]9[/bold red]  [white]HINT[/white]",
         "[dim]AI hints per SecDojo lab\nMethodology & tools\nNo spoilers mode[/dim]"),
        ("[bold red]10[/bold red] [white]LABS[/white]",
         "[dim]Track lab progress\nStore flags & notes\nProgress dashboard[/dim]"),
        ("[bold red]11[/bold red] [white]SESSION[/white]",
         "[dim]Save/load chat sessions\nResume lab investigations\nTeam-shareable history[/dim]"),
        ("[bold red]12[/bold red] [white]MODELS[/white]",
         "[dim]List active AI models\nOpenRouter free tier\nSee strengths & usage[/dim]"),
    ]

    panels = [Panel(f"{title}\n\n{desc}", border_style="red", padding=(0, 1), width=26) for title, desc in features]
    console.print(Columns(panels, equal=True, expand=False))

    console.print("\n[bold]QUICK REFERENCE:[/bold]")
    ex = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    ex.add_column("Command", style="bold red", min_width=50)
    ex.add_column("Description", style="dim")

    rows = [
        ("python3 cyberowl.py chat",                              "Interactive session (fast mode)"),
        ("python3 cyberowl.py chat -p",                          "Interactive session (all models)"),
        ("python3 cyberowl.py chat --resume my-session",         "Resume a saved session"),
        ("python3 cyberowl.py ask \"how to privesc linux\"",      "Quick one-shot question"),
        ("python3 cyberowl.py recon 10.10.10.50",                "Full recon plan"),
        ("python3 cyberowl.py recon 10.10.10.50 -l AD105",       "Recon with lab context"),
        ("python3 cyberowl.py analyze nmap -f scan.txt",         "Analyze nmap file"),
        ("python3 cyberowl.py analyze gobuster",                 "Paste gobuster output"),
        ("python3 cyberowl.py exploit \"Apache 2.4.49\"",        "Find CVEs + exploits"),
        ("python3 cyberowl.py payload reverse-shell -H 10.0.0.1 -P 4444", "Generate reverse shell"),
        ("python3 cyberowl.py payload privesc --os linux",       "Linux privesc one-liners"),
        ("python3 cyberowl.py wordlist web-directories",         "Best wordlists for web enum"),
        ("python3 cyberowl.py wordlist AD-passwords",            "AD password attack strategy"),
        ("python3 cyberowl.py search \"kerberoasting\"",         "HackTricks/GTFOBins lookup"),
        ("python3 cyberowl.py hint AD105",                       "AI hints for a lab"),
        ("python3 cyberowl.py labs",                             "Show all labs & progress"),
        ("python3 cyberowl.py lab AD105 -s solved",              "Mark lab as solved"),
        ("python3 cyberowl.py session list",                     "List saved sessions"),
        ("python3 cyberowl.py session delete my-session",        "Delete a session"),
        ("python3 cyberowl.py models",                           "List active AI models"),
    ]
    for cmd, desc in rows:
        ex.add_row(cmd, desc)
    console.print(ex)
    console.print(
        "\n[dim]Tip: [bold white]-p / --parallel[/bold white] on any command fires ALL models simultaneously "
        "(best for recon, analyze, exploit, payload — slower but more thorough)[/dim]\n"
    )


def show_labs_table():
    data = load_labs()
    labs_data = data["labs"]
    table = Table(title="SecDojo Labs — R3D HUNT3R", box=box.ROUNDED, border_style="red", header_style="bold red")
    table.add_column("Lab",      style="bold white", min_width=12)
    table.add_column("Level",    min_width=12)
    table.add_column("Category", min_width=16)
    table.add_column("Status",   min_width=14)
    table.add_column("Flags",    min_width=16)
    table.add_column("Notes",    min_width=20)

    solved = in_progress = not_started = 0
    for name, info in labs_data.items():
        sc = STATUS_COLORS.get(info["status"], "white")
        si = STATUS_ICONS.get(info["status"], "?")
        lc = LEVEL_COLORS.get(info["level"], "white")
        fl = ("[green]local✓[/green]" if info["flags"].get("local") else "[dim]local✗[/dim]") + \
             (" | [green]root✓[/green]" if info["flags"].get("proof") else " | [dim]root✗[/dim]")
        table.add_row(
            name,
            f"[{lc}]{info['level']}[/{lc}]",
            info["category"],
            f"[{sc}]{si} {info['status']}[/{sc}]",
            fl,
            (info["notes"][:28] + "…") if len(info["notes"]) > 28 else info["notes"] or "[dim]-[/dim]"
        )
        if info["status"] == "solved": solved += 1
        elif info["status"] == "in_progress": in_progress += 1
        else: not_started += 1

    console.print(table)
    console.print(
        f"\n[bold]Progress:[/bold] [green]{solved}/{len(labs_data)} solved[/green] | "
        f"[yellow]{in_progress} in progress[/yellow] | "
        f"[red]{not_started} not started[/red]\n"
    )


# ═══════════════════════════ CLI ═══════════════════════════

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """R3D HUNT3R — CTF AI Agent for SecDojo"""
    if ctx.invoked_subcommand is None:
        show_home_menu()


# ── CHAT ──────────────────────────────────────────────────

@cli.command()
@click.option("--parallel", "-p", is_flag=True, help="Use ALL models simultaneously")
@click.option("--resume", "-r", default=None, metavar="NAME", help="Resume a saved session")
def chat(parallel, resume):
    """Interactive AI session with session save/resume"""
    print_banner()
    agent = get_agent()

    if resume:
        try:
            count = agent.load_session(resume)
            console.print(f"[green]✓ Resumed session '[bold]{resume}[/bold]' — {count} messages loaded.[/green]\n")
        except FileNotFoundError as e:
            console.print(f"[red]❌ {e}[/red]")
            return

    mode = f"[bold red]ALL {len(ALL_MODELS)} models[/bold red]" if parallel else "[green]fast mode[/green]"
    console.print(Panel(
        f"[bold white]R3D HUNT3R — Interactive Mode[/bold white]  [{mode}]\n"
        "[dim]Commands: /save [name]  /load <name>  /reset  /labs  /parallel  /fast  /exit[/dim]",
        border_style="red"
    ))
    console.print(f"\n[bold red]>[/bold red] [dim]What are we hunting?[/dim]\n")

    use_parallel = parallel

    while True:
        try:
            user_input = Prompt.ask("[bold red]>[/bold red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Stay sharp.[/dim]")
            break

        stripped = user_input.strip()
        if not stripped:
            continue

        lower = stripped.lower()

        if lower in ["/exit", "/quit"]:
            console.print("[dim]Stay sharp.[/dim]")
            break
        elif lower == "/reset":
            agent.reset_conversation()
            console.print("[green]✓ Conversation cleared.[/green]\n")
            continue
        elif lower == "/labs":
            show_labs_table()
            continue
        elif lower == "/parallel":
            use_parallel = True
            console.print(f"[green]✓ ALL {len(ALL_MODELS)} models active.[/green]\n")
            continue
        elif lower == "/fast":
            use_parallel = False
            console.print("[green]✓ Fast mode (single model).[/green]\n")
            continue
        elif lower.startswith("/save"):
            parts = stripped.split(maxsplit=1)
            name = parts[1] if len(parts) > 1 else None
            saved_name = agent.save_session(name)
            console.print(f"[green]✓ Session saved as '[bold]{saved_name}[/bold]'.[/green]\n")
            continue
        elif lower.startswith("/load"):
            parts = stripped.split(maxsplit=1)
            if len(parts) < 2:
                console.print("[yellow]Usage: /load <session-name>[/yellow]\n")
                continue
            try:
                count = agent.load_session(parts[1])
                console.print(f"[green]✓ Loaded '[bold]{parts[1]}[/bold]' — {count} messages.[/green]\n")
            except FileNotFoundError as e:
                console.print(f"[red]❌ {e}[/red]\n")
            continue

        spinner = "Firing all models..." if use_parallel else "Thinking..."
        with console.status(f"[bold red]{spinner}[/bold red]", spinner="dots"):
            response = agent.chat(stripped, parallel=use_parallel)

        console.print(f"\n[bold red]R3D HUNT3R[/bold red]")
        console.print(Panel(Markdown(response), border_style="red", padding=(0, 1)))
        console.print()


# ── ASK ───────────────────────────────────────────────────

@cli.command()
@click.argument("message", nargs=-1, required=True)
@click.option("--parallel", "-p", is_flag=True, help="Use ALL models")
def ask(message, parallel):
    """One-shot CTF question"""
    agent = get_agent()
    with console.status("[bold red]Thinking...[/bold red]", spinner="dots"):
        response = agent.chat(" ".join(message), parallel=parallel)
    console.print(Panel(Markdown(response), title="[bold red]R3D HUNT3R[/bold red]", border_style="red", padding=(0, 1)))


# ── RECON ─────────────────────────────────────────────────

@cli.command()
@click.argument("target")
@click.option("--lab", "-l", default=None, help="Lab name for context")
def recon(target, lab):
    """Generate full recon plan for a target (all models)"""
    console.print(f"\n[bold red]>[/bold red] Recon plan for [bold white]{target}[/bold white]"
                  + (f" [dim](lab: {lab})[/dim]" if lab else "") + "\n")
    agent = get_agent()
    with console.status("[bold red]Firing all models...[/bold red]", spinner="dots"):
        response = agent.generate_recon(target, lab)
    console.print(Panel(Markdown(response), title=f"[bold]Recon — {target}[/bold]", border_style="yellow", padding=(0, 1)))


# ── ANALYZE ───────────────────────────────────────────────

@cli.command()
@click.argument("tool", type=click.Choice([
    "nmap", "gobuster", "nikto", "enum4linux",
    "crackmapexec", "bloodhound", "linpeas", "winpeas", "other"
]))
@click.option("--file", "-f", "input_file", type=click.Path(exists=True), default=None)
@click.option("--output", "-o", default=None)
def analyze(tool, input_file, output):
    """Analyze tool output — extract attack vectors (all models)"""
    if input_file:
        with open(input_file) as f:
            tool_output = f.read()
    elif output:
        tool_output = output
    else:
        console.print("[dim]Paste output, then Ctrl+D:[/dim]")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        tool_output = "\n".join(lines)

    if not tool_output.strip():
        console.print("[red]No output provided.[/red]")
        return

    agent = get_agent()
    with console.status(f"[bold red]Analyzing {tool}...[/bold red]", spinner="dots"):
        response = agent.analyze(tool, tool_output)
    console.print(Panel(Markdown(response), title=f"[bold]Analysis — {tool}[/bold]", border_style="magenta", padding=(0, 1)))


# ── EXPLOIT ───────────────────────────────────────────────

@cli.command()
@click.argument("target")
@click.option("--parallel", "-p", is_flag=True, help="Use ALL models")
def exploit(target, parallel):
    """Look up CVEs and exploits for a service/version"""
    console.print(f"\n[bold red]>[/bold red] Searching exploits for: [bold white]{target}[/bold white]\n")
    agent = get_agent()
    with console.status("[bold red]Hunting CVEs...[/bold red]", spinner="dots"):
        response = agent.exploit_search(target)
    console.print(Panel(Markdown(response), title=f"[bold]Exploits — {target}[/bold]", border_style="red", padding=(0, 1)))


# ── PAYLOAD ───────────────────────────────────────────────

@cli.command()
@click.argument("payload_type")
@click.option("--host", "-H", default=None, metavar="LHOST", help="Your IP for reverse shells")
@click.option("--port", "-P", default=None, metavar="LPORT", help="Listener port")
@click.option("--os", "target_os", default=None, help="Target OS (linux/windows)")
@click.option("--extra", "-e", default=None, help="Extra context")
def payload(payload_type, host, port, target_os, extra):
    """Generate payloads — reverse shells, webshells, privesc one-liners"""
    extra_combined = " ".join(filter(None, [f"OS: {target_os}" if target_os else None, extra]))
    console.print(f"\n[bold red]>[/bold red] Generating payload: [bold white]{payload_type}[/bold white]\n")
    agent = get_agent()
    with console.status("[bold red]Generating payloads...[/bold red]", spinner="dots"):
        response = agent.generate_payload(payload_type, host, port, extra_combined or None)
    console.print(Panel(Markdown(response), title=f"[bold]Payload — {payload_type}[/bold]", border_style="magenta", padding=(0, 1)))


# ── WORDLIST ──────────────────────────────────────────────

@cli.command()
@click.argument("target_type")
@click.option("--parallel", "-p", is_flag=True)
def wordlist(target_type, parallel):
    """Get best wordlist strategy for a target type"""
    console.print(f"\n[bold red]>[/bold red] Wordlist strategy for: [bold white]{target_type}[/bold white]\n")
    agent = get_agent()
    with console.status("[bold red]Building strategy...[/bold red]", spinner="dots"):
        response = agent.suggest_wordlists(target_type)
    console.print(Panel(Markdown(response), title=f"[bold]Wordlists — {target_type}[/bold]", border_style="cyan", padding=(0, 1)))


# ── SEARCH ────────────────────────────────────────────────

@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--parallel", "-p", is_flag=True)
def search(query, parallel):
    """Search HackTricks / GTFOBins knowledge base"""
    q = " ".join(query)
    console.print(f"\n[bold red]>[/bold red] Searching: [bold white]{q}[/bold white]\n")
    agent = get_agent()
    with console.status("[bold red]Searching knowledge base...[/bold red]", spinner="dots"):
        response = agent.ctf_search(q)
    console.print(Panel(Markdown(response), title=f"[bold]Search — {q}[/bold]", border_style="cyan", padding=(0, 1)))


# ── HINT ──────────────────────────────────────────────────

@cli.command()
@click.argument("lab_name")
def hint(lab_name):
    """Get AI hints for a specific SecDojo lab"""
    data = load_labs()
    if lab_name not in data["labs"]:
        console.print(f"[red]Lab '{lab_name}' not found.[/red]")
        return
    info = data["labs"][lab_name]
    prompt = f"""Give strategic hints for SecDojo lab '{lab_name}'.
Level: {info['level']} | Category: {info['category']} | Status: {info['status']}
Notes: {info['notes'] or 'None'}

Provide:
1. Likely attack vectors for this lab type
2. Key tools and commands
3. Common pitfalls to avoid
4. Step-by-step methodology (no direct flag solutions)"""
    agent = get_agent()
    with console.status(f"[bold red]Getting hints...[/bold red]", spinner="dots"):
        response = agent.chat(prompt, parallel=True)
    console.print(Panel(Markdown(response), title=f"[bold]Hints — {lab_name} [{info['level']}][/bold]",
                        border_style="yellow", padding=(0, 1)))


# ── LABS ──────────────────────────────────────────────────

@cli.command()
def labs():
    """Show SecDojo lab tracker"""
    show_labs_table()


@cli.command()
@click.argument("lab_name")
@click.option("--status", "-s", type=click.Choice(["solved", "in_progress", "not_started"]), default=None)
@click.option("--local-flag", default=None)
@click.option("--proof-flag", default=None)
@click.option("--notes", "-n", default=None)
@click.option("--add", is_flag=True)
@click.option("--level", type=click.Choice(["basic", "intermediate", "advanced"]), default="intermediate")
@click.option("--category", default="misc")
def lab(lab_name, status, local_flag, proof_flag, notes, add, level, category):
    """Add or update a lab entry"""
    data = load_labs()
    labs_data = data["labs"]

    if add and lab_name not in labs_data:
        labs_data[lab_name] = {"level": level, "category": category, "status": "not_started",
                                "flags": {"local": None, "proof": None}, "notes": ""}
        console.print(f"[green]✓ Lab '{lab_name}' added.[/green]")

    if lab_name not in labs_data:
        console.print(f"[red]Lab '{lab_name}' not found. Use --add to create it.[/red]")
        return

    if status:     labs_data[lab_name]["status"]        = status;     console.print(f"[green]✓ Status: {status}[/green]")
    if local_flag: labs_data[lab_name]["flags"]["local"] = local_flag; console.print("[green]✓ Local flag saved.[/green]")
    if proof_flag: labs_data[lab_name]["flags"]["proof"] = proof_flag; console.print("[green]✓ Proof flag saved.[/green]")
    if notes:      labs_data[lab_name]["notes"]          = notes;      console.print("[green]✓ Notes updated.[/green]")

    save_labs(data)
    show_labs_table()


# ── SESSION ───────────────────────────────────────────────

@cli.group()
def session():
    """Manage saved chat sessions"""
    pass


@session.command(name="list")
def session_list():
    """List all saved sessions"""
    sessions = list_sessions()
    if not sessions:
        console.print("[dim]No saved sessions found.[/dim]")
        return
    table = Table(title="Saved Sessions", box=box.ROUNDED, border_style="red", header_style="bold red")
    table.add_column("Name",     style="bold white")
    table.add_column("Lab",      style="cyan")
    table.add_column("Messages", style="yellow")
    table.add_column("Saved At", style="dim")
    for s in sessions:
        table.add_row(s["name"], s["lab"], str(s["messages"]), s["saved_at"])
    console.print(table)


@session.command(name="delete")
@click.argument("name")
def session_delete(name):
    """Delete a saved session"""
    if delete_session(name):
        console.print(f"[green]✓ Session '{name}' deleted.[/green]")
    else:
        console.print(f"[red]Session '{name}' not found.[/red]")


# ── MODELS ────────────────────────────────────────────────

@cli.command()
def models():
    """List active OpenRouter free models"""
    table = Table(title="Active Models — R3D HUNT3R", box=box.ROUNDED, border_style="red", header_style="bold red")
    table.add_column("Name",     style="bold white")
    table.add_column("Model ID", style="dim")
    table.add_column("Strength", style="cyan")
    table.add_column("Mode",     style="yellow")
    for key, info in FREE_MODELS.items():
        used = "[bold]default + parallel[/bold]" if key in CHAT_MODELS else "parallel only"
        table.add_row(f"{info['icon']} {key}", info["id"], info["strength"], used)
    console.print(table)
    console.print(f"\n[dim]Default: 1 model (fast) | -p / --parallel: all {len(ALL_MODELS)} models[/dim]\n")


if __name__ == "__main__":
    cli()
