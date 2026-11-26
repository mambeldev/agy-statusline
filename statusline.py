#!/usr/bin/env python3
"""
Custom Statusline for Antigravity CLI (agy)
Displays token consumption (% Day, % Week, % Month) in English without emojis,
positioned at the bottom right immediately to the left of the active model.

Compatible with Python 3.7+ (works out of the box with macOS system Python 3.9).
Includes built-in installer:
  python3 statusline.py --install       # Copy to ~/.gemini/antigravity-cli/ & configure settings.json
  python3 statusline.py --install-here  # Run directly from current path & configure settings.json
  python3 statusline.py --uninstall     # Remove from settings.json & delete installed script
  python3 statusline.py --test          # Preview statusline in terminal
"""
from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import stat
import sys

AGY_DIR = os.path.expanduser("~/.gemini/antigravity-cli")
INSTALLED_SCRIPT_PATH = os.path.join(AGY_DIR, "statusline.py")
SETTINGS_PATH = os.path.join(AGY_DIR, "settings.json")
CACHE_PATH = os.path.join(AGY_DIR, "cache", "token_tracker.json")


def strip_ansi(text: str) -> str:
    """Removes ANSI escape codes to measure true printable length."""
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)


def format_percentage(pct: float | None) -> str:
    """Formats percentage with color coding based on usage thresholds."""
    if pct is None:
        return "\033[90m--%\033[0m"

    if pct < 50.0:
        color = "\033[32m"       # Green (< 50%)
    elif pct < 80.0:
        color = "\033[33m"       # Yellow (50% - 80%)
    elif pct < 95.0:
        color = "\033[31m"       # Red (80% - 95%)
    else:
        color = "\033[1;31m"     # Bold Red (>= 95%)

    return f"{color}{pct:.1f}%\033[0m"


def get_monthly_consumption(
    quota_key: str,
    week_used: float | None,
    reset_time_str: str | None,
    persist_cache: bool = True,
) -> float | None:
    """Calculates or tracks month-to-date token consumption."""
    if week_used is None:
        return None

    now = datetime.datetime.now(datetime.timezone.utc)
    month_key = now.strftime("%Y-%m")

    data = {}
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    month_data = data.setdefault(month_key, {}).setdefault(quota_key, {})

    if reset_time_str and persist_cache and reset_time_str != "2099-01-01T00:00:00Z":
        prev_peak = month_data.get(reset_time_str, 0.0)
        if week_used > prev_peak:
            month_data[reset_time_str] = round(week_used, 2)
            try:
                os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
                with open(CACHE_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f)
            except Exception:
                pass

    weeks_recorded = list(month_data.values())
    if not weeks_recorded:
        return round(week_used / 4.33, 1)

    total_consumed = sum(weeks_recorded)
    return round(total_consumed / 4.33, 1)


def render_statusline(data: dict, persist_cache: bool = True) -> str:
    """Builds the formatted ANSI statusline string from an agy JSON payload."""
    # 1. Terminal width
    width = data.get("terminal_width") or 80

    # 2. Model information
    model_info = data.get("model", {})
    model_name = model_info.get("display_name") or model_info.get("id") or "Antigravity"
    model_lower = model_name.lower()

    # Determine whether active model is 3rd-party (Claude/GPT) or native (Gemini)
    is_3p = any(k in model_lower for k in ["claude", "opus", "sonnet", "3p", "haiku", "gpt"])

    # 3. Quota parsing
    quota = data.get("quota") or {}

    day_key = "3p-5h" if is_3p else "gemini-5h"
    week_key = "3p-weekly" if is_3p else "gemini-weekly"

    # Daily quota
    day_rem = None
    if day_key in quota and "remaining_fraction" in quota[day_key]:
        day_rem = quota[day_key]["remaining_fraction"]
    else:
        for k, v in quota.items():
            if ("5h" in k or "day" in k or "daily" in k) and isinstance(v, dict) and "remaining_fraction" in v:
                day_rem = v["remaining_fraction"]
                break

    # Weekly quota
    week_rem = None
    week_reset_time = None
    if week_key in quota and "remaining_fraction" in quota[week_key]:
        week_rem = quota[week_key]["remaining_fraction"]
        week_reset_time = quota[week_key].get("reset_time")
    else:
        for k, v in quota.items():
            if ("week" in k or "weekly" in k) and isinstance(v, dict) and "remaining_fraction" in v:
                week_rem = v["remaining_fraction"]
                week_reset_time = v.get("reset_time")
                break

    day_used = ((1.0 - day_rem) * 100.0) if day_rem is not None else None
    week_used = ((1.0 - week_rem) * 100.0) if week_rem is not None else None

    # Monthly quota: direct from payload if provided, otherwise compute from tracker
    month_used = None
    for k, v in quota.items():
        if ("month" in k or "monthly" in k) and isinstance(v, dict) and "remaining_fraction" in v:
            month_used = (1.0 - v["remaining_fraction"]) * 100.0
            break

    if month_used is None:
        month_used = get_monthly_consumption(week_key, week_used, week_reset_time, persist_cache=persist_cache)

    # 4. Construct Left Side (Status & Directory/Branch in English)
    state = data.get("agent_state", "idle")
    state_badge = "\033[90m○ idle\033[0m" if state == "idle" else "\033[32m● active\033[0m"

    vcs = data.get("vcs") or {}
    branch = vcs.get("branch")

    cwd = data.get("cwd") or data.get("workspace", {}).get("current_dir", "")
    folder_name = cwd.rstrip("/").split("/")[-1] if cwd else "workspace"

    if branch:
        left_text = f" {state_badge} \033[2m{folder_name}\033[0m \033[36m({branch})\033[0m"
    else:
        left_text = f" {state_badge} \033[2m{folder_name}\033[0m"

    # 5. Construct Right Side (Tokens indicator in English without emojis + Model badge)
    day_str = format_percentage(day_used)
    week_str = format_percentage(week_used)
    month_str = format_percentage(month_used)

    model_badge = f"\033[1;34m[{model_name}]\033[0m "

    # Choose full vs compact text based on terminal width
    if width >= 95:
        tokens_indicator = f"\033[90m[Day:\033[0m {day_str} \033[90m| Week:\033[0m {week_str} \033[90m| Month:\033[0m {month_str}\033[90m]\033[0m"
    else:
        tokens_indicator = f"\033[90m[D:\033[0m {day_str} \033[90m| W:\033[0m {week_str} \033[90m| M:\033[0m {month_str}\033[90m]\033[0m"

    right_text = f"{tokens_indicator}  {model_badge}"

    # 6. Alignment & Width calculation
    plain_left = strip_ansi(left_text)
    plain_right = strip_ansi(right_text)

    spacing = width - len(plain_left) - len(plain_right)

    # Fallbacks for narrower terminals
    if spacing < 1:
        left_text = f" {state_badge}"
        plain_left = strip_ansi(left_text)
        spacing = width - len(plain_left) - len(plain_right)

    if spacing < 1:
        tokens_indicator = f"\033[90m[\033[0m{day_str}\033[90m|\033[0m{week_str}\033[90m|\033[0m{month_str}\033[90m]\033[0m"
        right_text = f"{tokens_indicator} {model_badge}"
        plain_right = strip_ansi(right_text)
        spacing = width - len(plain_left) - len(plain_right)

    if spacing < 1:
        spacing = 1

    return left_text + (" " * spacing) + right_text


def make_executable(path: str) -> None:
    """Adds executable permissions (chmod +x) to the given file."""
    current_mode = os.stat(path).st_mode
    os.chmod(path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def sample_payload() -> dict:
    """Returns a sample payload for testing and previewing the statusline."""
    try:
        cols = shutil.get_terminal_size((100, 20)).columns
    except Exception:
        cols = 100
    return {
        "terminal_width": max(cols, 80),
        "agent_state": "active",
        "cwd": os.getcwd(),
        "vcs": {"branch": "main"},
        "model": {"display_name": "Gemini 2.5 Pro"},
        "quota": {
            "gemini-5h": {"remaining_fraction": 0.855},
            "gemini-weekly": {
                "remaining_fraction": 0.58,
                "reset_time": "2099-01-01T00:00:00Z",
            },
        },
    }


def install(in_place: bool = False) -> int:
    """Installs statusline.py and updates ~/.gemini/antigravity-cli/settings.json."""
    src_path = os.path.abspath(__file__)
    target_path = src_path if in_place else INSTALLED_SCRIPT_PATH
    command_str = src_path if in_place else "~/.gemini/antigravity-cli/statusline.py"

    try:
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        if not in_place and os.path.abspath(src_path) != os.path.abspath(target_path):
            shutil.copy2(src_path, target_path)
        make_executable(target_path)

        settings_data = {}
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    settings_data = json.loads(content)

        settings_data["statusLine"] = {
            "type": "command",
            "command": command_str,
            "enabled": True,
            "padding": 0,
            "stack_with_default": False,
        }

        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, indent=2)
            f.write("\n")

        print(f"✔ Script configurado en: {target_path}")
        print(f"✔ Ajustes actualizados en: {SETTINGS_PATH}")
        print("\nVista previa:")
        print(render_statusline(sample_payload(), persist_cache=False))
        return 0
    except OSError as exc:
        try:
            make_executable(src_path)
        except Exception:
            pass
        print(f"⚠ El entorno actual bloqueó el acceso directo a {AGY_DIR} ({exc}).", file=sys.stderr)
        print(f"Puedes activarlo directamente dentro de agy ejecutando:\n  /statusline {src_path}", file=sys.stderr)
        return 1


def uninstall() -> int:
    """Removes statusLine from settings.json and cleans up the installed script."""
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                settings_data = json.loads(content) if content else {}
            if "statusLine" in settings_data:
                del settings_data["statusLine"]
                with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                    json.dump(settings_data, f, indent=2)
                    f.write("\n")
                print(f"✔ Clave 'statusLine' eliminada de {SETTINGS_PATH}")

        if os.path.exists(INSTALLED_SCRIPT_PATH) and os.path.abspath(__file__) != os.path.abspath(INSTALLED_SCRIPT_PATH):
            os.remove(INSTALLED_SCRIPT_PATH)
            print(f"✔ Archivo eliminado: {INSTALLED_SCRIPT_PATH}")

        if os.path.exists(CACHE_PATH):
            os.remove(CACHE_PATH)
            print(f"✔ Caché mensual eliminado: {CACHE_PATH}")

        print("✔ Desinstalación completada.")
        return 0
    except OSError as exc:
        print(f"⚠ Permiso denegado al modificar {AGY_DIR} ({exc}).", file=sys.stderr)
        print("Ejecuta dentro de agy: /statusline reset", file=sys.stderr)
        return 1


def main() -> None:
    args = sys.argv[1:]

    if "--install" in args:
        sys.exit(install(in_place=False))
    if "--install-here" in args:
        sys.exit(install(in_place=True))
    if "--uninstall" in args:
        sys.exit(uninstall())
    if "--test" in args:
        sys.stdout.write(render_statusline(sample_payload(), persist_cache=False) + "\n")
        sys.stdout.flush()
        sys.exit(0)
    if "--help" in args or "-h" in args:
        print(__doc__.strip())
        sys.exit(0)

    # If executed directly in an interactive terminal without arguments (no piped stdin),
    # show a preview and installation hints instead of hanging on stdin.read().
    if sys.stdin.isatty():
        print("Vista previa de agy-statusline:")
        print(render_statusline(sample_payload(), persist_cache=False))
        print("\nOpciones de instalación rápida:")
        print("  python3 statusline.py --install       # Copia a ~/.gemini/antigravity-cli/ y activa en settings.json")
        print("  python3 statusline.py --install-here  # Usa el script en su ubicación actual y activa en settings.json")
        print("  python3 statusline.py --uninstall     # Desinstala y restaura la barra por defecto")
        sys.exit(0)

    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.exit(0)
        data = json.loads(raw_input)
    except Exception:
        sys.exit(0)

    sys.stdout.write(render_statusline(data, persist_cache=True))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
