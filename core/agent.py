import os
import json
import threading
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
LABS_FILE = DATA_DIR / "labs.json"
SESSIONS_DIR = DATA_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"

# Best free models on OpenRouter (verified March 2026)
FREE_MODELS = {
    "openrouter-free": {
        "id": "openrouter/free",
        "strength": "auto-selects best free model",
        "icon": "🎯"
    },
    "step-3.5-flash": {
        "id": "stepfun/step-3.5-flash:free",
        "strength": "reasoning & long context (256K)",
        "icon": "🧠"
    },
    "arcee-trinity": {
        "id": "arcee-ai/trinity-large-preview:free",
        "strength": "agentic & complex tasks (131K)",
        "icon": "🦾"
    },
    "glm-4.5-air": {
        "id": "z-ai/glm-4.5-air:free",
        "strength": "thinking mode + tool use",
        "icon": "⚡"
    },
    "nemotron-nano-9b": {
        "id": "nvidia/nemotron-nano-9b-v2:free",
        "strength": "fast reasoning traces",
        "icon": "🔍"
    },
    "arcee-trinity-mini": {
        "id": "arcee-ai/trinity-mini:free",
        "strength": "fast MoE + function calling",
        "icon": "💨"
    },
}

CHAT_MODELS = ["openrouter-free", "step-3.5-flash", "glm-4.5-air"]
ALL_MODELS  = list(FREE_MODELS.keys())

CTF_SYSTEM_PROMPT = """You are R3D HUNT3R, an elite CTF AI agent specialized for the SecDojo platform.

You assist a red team with:
- CTF techniques, exploitation, and methodology
- Recon, enumeration, privilege escalation, lateral movement
- Active Directory attacks (Kerberoasting, AS-REP Roasting, Pass-the-Hash, BloodHound, DCSync, etc.)
- Web exploitation (SQLi, XSS, SSRF, LFI/RFI, IDOR, XXE, deserialization, etc.)
- Linux/Windows privilege escalation
- AI/ML and sandbox escape challenges
- N8N, MCP, Docker escape, workflow automation exploitation
- CVE research and exploit development
- Payload generation: reverse shells, web shells, privesc one-liners
- Wordlist and dictionary attack strategy
- Analyzing tool outputs (nmap, gobuster, nikto, enum4linux, crackmapexec, etc.)

Platform rules (SecDojo):
- Team mode: only ONE member needs to submit the flag
- Wrong flag submissions do NOT affect the score
- Flags are UNIQUE per lab instance
- Linux flags: /home/local.txt (user) and /root/proof.txt (root)
- Windows flags: C:\\Users\\Public\\local.txt and C:\\Users\\Administrator\\Desktop\\proof.txt

Always give practical, actionable commands. Be concise but thorough."""


# ──────────────────── Labs helpers ────────────────────

def load_labs():
    with open(LABS_FILE, "r") as f:
        return json.load(f)

def save_labs(data):
    with open(LABS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_labs_context():
    data = load_labs()
    lines = ["Current SecDojo lab status:"]
    for name, info in data["labs"].items():
        icon = "✓" if info["status"] == "solved" else ("⚡" if info["status"] == "in_progress" else "○")
        lines.append(f"  {icon} {name} [{info['level']}] ({info['category']}) - {info['status']}")
    return "\n".join(lines)


# ──────────────────── Session helpers ────────────────────

def list_sessions() -> list:
    files = sorted(SESSIONS_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    sessions = []
    for f in files:
        try:
            data = json.loads(f.read_text())
            sessions.append({
                "name": f.stem,
                "lab": data.get("lab", "-"),
                "messages": len(data.get("history", [])),
                "saved_at": data.get("saved_at", "unknown"),
            })
        except Exception:
            pass
    return sessions

def save_session(name: str, history: list, lab: str = None):
    path = SESSIONS_DIR / f"{name}.json"
    path.write_text(json.dumps({
        "name": name,
        "lab": lab or "-",
        "history": history,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }, indent=2))
    return path

def load_session(name: str) -> dict:
    path = SESSIONS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Session '{name}' not found.")
    return json.loads(path.read_text())

def delete_session(name: str):
    path = SESSIONS_DIR / f"{name}.json"
    if path.exists():
        path.unlink()
        return True
    return False


# ──────────────────── Model call helpers ────────────────────

def _call_model_sync(model_key: str, messages: list, api_key: str) -> dict:
    model_info = FREE_MODELS[model_key]
    payload = json.dumps({
        "model": model_info["id"],
        "max_tokens": 1024,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(
        OPENROUTER_BASE,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://r3dhunt3r.local",
            "X-Title": "R3D HUNT3R CTF Agent",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return {"model": model_key, "content": content, "success": True}
    except Exception as e:
        return {"model": model_key, "content": str(e), "success": False}


def call_models_parallel(model_keys: list, messages: list, api_key: str) -> list:
    results = [None] * len(model_keys)
    def worker(idx, key):
        results[idx] = _call_model_sync(key, messages, api_key)
    threads = [threading.Thread(target=worker, args=(i, k)) for i, k in enumerate(model_keys)]
    for t in threads: t.start()
    for t in threads: t.join()
    return [r for r in results if r is not None]


def merge_responses(responses: list) -> str:
    successful = [r for r in responses if r["success"]]
    failed     = [r for r in responses if not r["success"]]

    if not successful:
        return "❌ All models failed:\n" + "\n".join(f"  - {r['model']}: {r['content']}" for r in failed)

    if len(successful) == 1:
        m    = successful[0]
        info = FREE_MODELS[m["model"]]
        return f"{info['icon']} **{m['model']}** — *{info['strength']}*\n\n{m['content']}"

    parts = [f"## Multi-Model Analysis ({len(successful)}/{len(responses)} models responded)\n"]
    if failed:
        parts.append(f"*Failed: {', '.join(r['model'] for r in failed)}*\n")
    for r in successful:
        info = FREE_MODELS[r["model"]]
        parts.append(f"---\n### {info['icon']} {r['model']} — *{info['strength']}*\n\n{r['content']}\n")
    return "\n".join(parts)


# ──────────────────── Main agent class ────────────────────

class CTFAgent:
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not set.\n"
                "Get your free key at: https://openrouter.ai\n"
                "Then: export OPENROUTER_API_KEY=your_key_here"
            )
        self.conversation_history = []
        self.current_session_name = None
        self.current_lab = None

    def _build_messages(self, user_message: str, include_labs: bool = True) -> list:
        context = get_labs_context() + "\n\n" if include_labs else ""
        messages = [{"role": "system", "content": CTF_SYSTEM_PROMPT}]
        messages += self.conversation_history
        messages.append({"role": "user", "content": f"{context}{user_message}"})
        return messages

    def _single_model(self, messages: list) -> str:
        """Use only the first CHAT_MODEL for fast single responses."""
        result = _call_model_sync(CHAT_MODELS[0], messages, self.api_key)
        if result["success"]:
            return result["content"]
        # fallback to second
        result = _call_model_sync(CHAT_MODELS[1], messages, self.api_key)
        return result["content"] if result["success"] else f"❌ {result['content']}"

    def chat(self, user_message: str, include_labs_context: bool = True, parallel: bool = False) -> str:
        messages = self._build_messages(user_message, include_labs_context)
        if parallel:
            responses = call_models_parallel(ALL_MODELS, messages, self.api_key)
            reply = merge_responses(responses)
            first_ok = next((r["content"] for r in responses if r["success"]), reply)
        else:
            first_ok = self._single_model(messages)
            reply = first_ok

        self.conversation_history.append({"role": "user",      "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": first_ok})
        return reply

    def analyze(self, tool_name: str, output: str) -> str:
        prompt = f"""Analyze this {tool_name} output for a CTF challenge.
1. Key findings and interesting entries
2. Potential attack vectors
3. Recommended next steps with specific commands
4. Any credentials, flags, or sensitive data visible

{tool_name.upper()} OUTPUT:
{output}"""
        messages = self._build_messages(prompt, include_labs=False)
        return merge_responses(call_models_parallel(ALL_MODELS, messages, self.api_key))

    def generate_recon(self, target: str, lab_name: str = None) -> str:
        lab_hint = f" (Lab: {lab_name})" if lab_name else ""
        prompt = f"""Generate a full recon plan for CTF target: {target}{lab_hint}
1. Nmap: fast scan → full TCP → UDP → scripts
2. Per-service enumeration commands
3. Web: gobuster, nikto, ffuf, whatweb
4. SMB/AD: enum4linux-ng, crackmapexec, bloodhound-python
5. Quick wins to check first
6. Most likely attack vectors"""
        messages = self._build_messages(prompt, include_labs=bool(lab_name))
        return merge_responses(call_models_parallel(ALL_MODELS, messages, self.api_key))

    def exploit_search(self, target: str) -> str:
        """Search for CVEs and exploits for a given service/version."""
        prompt = f"""For the following service/version in a CTF context: {target}

Provide:
1. Known CVEs with CVSS score and brief description
2. Whether a public exploit exists (Metasploit module, ExploitDB, GitHub PoC)
3. Exact exploit commands or steps to reproduce
4. Recommended exploitation order (easiest to most complex)
5. Any CTF-specific tricks for this service"""
        messages = self._build_messages(prompt, include_labs=False)
        return merge_responses(call_models_parallel(ALL_MODELS, messages, self.api_key))

    def generate_payload(self, payload_type: str, lhost: str = None, lport: str = None, extra: str = None) -> str:
        """Generate payloads: reverse shells, web shells, privesc one-liners."""
        context = ""
        if lhost: context += f"\nLHOST: {lhost}"
        if lport: context += f"\nLPORT: {lport}"
        if extra: context += f"\nExtra context: {extra}"
        prompt = f"""Generate CTF payloads for: {payload_type}{context}

Provide:
1. Multiple payload variants (bash, python, php, powershell where applicable)
2. URL-encoded version if web-facing
3. Base64-encoded version for obfuscation
4. Listener setup command (if reverse shell)
5. Notes on when to use each variant"""
        messages = self._build_messages(prompt, include_labs=False)
        return merge_responses(call_models_parallel(ALL_MODELS, messages, self.api_key))

    def suggest_wordlists(self, target_type: str) -> str:
        """Suggest best wordlists for a given attack scenario."""
        prompt = f"""Suggest the best wordlists and dictionary attack strategy for: {target_type}

Provide:
1. Top recommended wordlists (with exact paths on Kali/ParrotOS and download links)
2. Tool + wordlist combos with exact commands
3. Custom mutation rules if applicable (hashcat rules, etc.)
4. Order of attack: start with smallest/fastest, escalate
5. Any CTF-specific tricks (common CTF passwords, patterns)"""
        messages = self._build_messages(prompt, include_labs=False)
        return merge_responses(call_models_parallel(ALL_MODELS, messages, self.api_key))

    def ctf_search(self, query: str) -> str:
        """Search HackTricks / GTFOBins knowledge for a technique."""
        prompt = f"""Acting as a HackTricks + GTFOBins expert, explain: {query}

Provide:
1. Technique explanation
2. Exact commands to use
3. HackTricks page reference (hacktricks.xyz/...)
4. GTFOBins entry if relevant (gtfobins.github.io/...)
5. Real CTF examples where this was used
6. Common mistakes to avoid"""
        messages = self._build_messages(prompt, include_labs=False)
        return merge_responses(call_models_parallel(ALL_MODELS, messages, self.api_key))

    # ── Session management ──

    def save_session(self, name: str = None) -> str:
        if not name:
            name = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        path = save_session(name, self.conversation_history, self.current_lab)
        self.current_session_name = name
        return name

    def load_session(self, name: str):
        data = load_session(name)
        self.conversation_history = data.get("history", [])
        self.current_lab = data.get("lab")
        self.current_session_name = name
        return len(self.conversation_history)

    def reset_conversation(self):
        self.conversation_history = []
        self.current_session_name = None

    @staticmethod
    def list_models():
        return FREE_MODELS
