# R3D HUNT3R — CTF AI Agent

**AI-powered CTF assistant for SecDojo**, built for red teams. Combines multiple free LLMs from OpenRouter running in parallel to give you recon plans, exploit lookups, payload generation, tool analysis, and a persistent lab tracker — all from the terminal.

---

## Setup

```bash
# 1. Clone / copy the project
cd R3D-HUNT3ER

# 2. Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install rich click

# 4. Get your free OpenRouter API key
#    → https://openrouter.ai  (no credit card required)

# 5. Set the API key
export OPENROUTER_API_KEY=your_key_here
# Add to ~/.bashrc to persist:
echo 'export OPENROUTER_API_KEY=your_key_here' >> ~/.bashrc

# 6. Create core/__init__.py if missing
touch core/__init__.py

# 7. (Optional) add alias
echo "alias r3d='python3 /path/to/R3D-HUNT3ER/cyberowl.py'" >> ~/.bashrc
source ~/.bashrc
```

---

## Commands

### Launch menu
```bash
python3 cyberowl.py
```
Shows the full feature dashboard with all commands and examples.

---

### `chat` — Interactive session
```bash
python3 cyberowl.py chat                  # Fast mode (single model)
python3 cyberowl.py chat -p               # All models in parallel
python3 cyberowl.py chat --resume AD105-session   # Resume saved session
```
**In-session commands:**
| Command | Action |
|---------|--------|
| `/save [name]` | Save current session to disk |
| `/load <name>` | Load a previously saved session |
| `/parallel` | Switch to all-models mode |
| `/fast` | Switch back to single-model mode |
| `/labs` | Show lab progress table |
| `/reset` | Clear conversation history |
| `/exit` | Quit |

---

### `ask` — One-shot question
```bash
python3 cyberowl.py ask "how to enumerate SMB on Windows"
python3 cyberowl.py ask -p "explain Kerberoasting step by step"
```

---

### `recon` — Recon plan generator
Generates a full recon plan: nmap phases → service enumeration → web/AD enumeration → attack vectors.
```bash
python3 cyberowl.py recon 10.10.10.50
python3 cyberowl.py recon 10.10.10.50 -l AD105    # with lab context
```

---

### `analyze` — Tool output analyzer
Paste or pipe tool output — the agent identifies findings, attack vectors, and next steps.
```bash
# From a file
python3 cyberowl.py analyze nmap -f scan.txt
python3 cyberowl.py analyze linpeas -f linpeas_out.txt

# Pipe directly
nmap -sV 10.10.10.50 > scan.txt && python3 cyberowl.py analyze nmap -f scan.txt

# Interactive paste (Ctrl+D when done)
python3 cyberowl.py analyze gobuster
python3 cyberowl.py analyze enum4linux
```
**Supported tools:** `nmap` `gobuster` `nikto` `enum4linux` `crackmapexec` `bloodhound` `linpeas` `winpeas` `other`

---

### `exploit` — CVE & exploit lookup
Given a service name or version, returns known CVEs, ExploitDB entries, Metasploit modules, and exact exploit commands.
```bash
python3 cyberowl.py exploit "Apache 2.4.49"
python3 cyberowl.py exploit "SMB EternalBlue"
python3 cyberowl.py exploit "OpenSSH 7.2p2"
python3 cyberowl.py exploit "Samba 3.0.20"
```

---

### `payload` — Payload generator
Generates reverse shells, web shells, and privesc one-liners in multiple variants with base64 encoding.
```bash
# Reverse shells
python3 cyberowl.py payload reverse-shell -H 10.10.14.5 -P 4444
python3 cyberowl.py payload reverse-shell -H 10.10.14.5 -P 443 --os windows

# Web shells
python3 cyberowl.py payload php-webshell
python3 cyberowl.py payload aspx-webshell

# Privilege escalation
python3 cyberowl.py payload privesc --os linux
python3 cyberowl.py payload privesc --os windows

# Custom context
python3 cyberowl.py payload "SQL injection RCE" -e "MySQL, Windows Server 2019"
```

---

### `wordlist` — Wordlist strategy
Returns the best wordlists and tool combos for a given attack scenario, with exact Kali/Parrot paths and download links.
```bash
python3 cyberowl.py wordlist web-directories
python3 cyberowl.py wordlist "AD passwords"
python3 cyberowl.py wordlist "SSH brute force"
python3 cyberowl.py wordlist "subdomain enumeration"
python3 cyberowl.py wordlist "WordPress login"
```

---

### `search` — HackTricks / GTFOBins lookup
Deep-dives into a technique: explanation, commands, HackTricks reference, GTFOBins entry, and real CTF examples.
```bash
python3 cyberowl.py search "kerberoasting"
python3 cyberowl.py search "SSRF to internal metadata"
python3 cyberowl.py search "docker escape privileged container"
python3 cyberowl.py search "sudo -l exploitation"
python3 cyberowl.py search "SUID binary exploitation"
```

---

### `hint` — Lab-specific AI hints
Provides methodology, key tools, and common pitfalls for a specific SecDojo lab — no direct spoilers.
```bash
python3 cyberowl.py hint AD105
python3 cyberowl.py hint N8N
python3 cyberowl.py hint Labyrinth
```

---

### `labs` — Lab progress tracker
```bash
python3 cyberowl.py labs
```

### `lab` — Update a lab
```bash
# Mark as solved
python3 cyberowl.py lab AD105 -s solved

# Save flags
python3 cyberowl.py lab AD105 --local-flag "FLAG{abc123}" --proof-flag "FLAG{xyz789}"

# Add notes
python3 cyberowl.py lab AD105 -n "Got shell via AS-REP roasting, cracked hash with hashcat"

# Add a new lab (when SecDojo releases more)
python3 cyberowl.py lab NewLab --add --level advanced --category web
```

---

### `session` — Session management
Save and resume full chat histories — useful for long lab investigations.
```bash
# List saved sessions
python3 cyberowl.py session list

# Delete a session
python3 cyberowl.py session delete AD105-session
```

**Saving from inside chat:**
```
> /save AD105-session
✓ Session saved as 'AD105-session'.

# Next time:
python3 cyberowl.py chat --resume AD105-session
```

---

### `models` — Show active models
```bash
python3 cyberowl.py models
```

---

## Model strategy

| Mode | Models used | When |
|------|-------------|------|
| Default | 1 model (fast) | `chat`, `ask` |
| `--parallel` / `-p` | All 6 models simultaneously | Deep analysis |
| Auto-parallel | All 6 models | `recon`, `analyze`, `exploit`, `payload`, `wordlist`, `search`, `hint` |

**Active free models (OpenRouter, March 2026):**
| Model | Strength |
|-------|----------|
| openrouter/free | Auto-selects best available free model |
| stepfun/step-3.5-flash | Reasoning & 256K context |
| arcee-ai/trinity-large-preview | Agentic & complex tasks |
| z-ai/glm-4.5-air | Thinking mode + tool use |
| nvidia/nemotron-nano-9b-v2 | Fast reasoning traces |
| arcee-ai/trinity-mini | Fast MoE + function calling |

---

## SecDojo rules (built-in context)
- **Team mode:** only ONE member needs to submit the flag
- **Wrong flags:** don't affect your score
- **Flags are unique** per lab instance (can't be shared between instances)
- Linux: `/home/local.txt` and `/root/proof.txt`
- Windows: `C:\Users\Public\local.txt` and `C:\Users\Administrator\Desktop\proof.txt`

---

## Project structure
```
R3D-HUNT3ER/
├── cyberowl.py          # Main CLI
├── core/
│   ├── __init__.py
│   └── agent.py         # AI agent, model calls, session logic
├── data/
│   ├── labs.json        # Lab tracker database
│   └── sessions/        # Saved chat sessions
└── README.md
```
