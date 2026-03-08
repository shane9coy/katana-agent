from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
SOURCE_SKILL_DIR = SCRIPT_ROOT / "astro-companion"
HOME = Path.home()
HERMES_DIR = HOME / ".hermes"
STATE_DIR = HERMES_DIR / "oracle"
TARGET_SKILL_DIR = HERMES_DIR / "skills" / "oracle" / "astro-companion"
CONFIG_PATH = HERMES_DIR / "config.yaml"


def copy_file(src: Path, dst: Path, *, force: bool = False) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        return False
    shutil.copy2(src, dst)
    return True


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.name}.bak.{timestamp}")
    shutil.copy2(path, backup)
    return backup


def merge_natal_mcp_config(force: bool = False) -> str:
    snippet = [
        "  # >>> oracle-astro-companion",
        "  natal:",
        '    command: "uvx"',
        '    args: ["natal-mcp"]',
        "    env:",
        f'      NATAL_MCP_HOME: "{HOME / "natal_mcp"}"',
        "    timeout: 120",
        "    connect_timeout: 60",
        "  # <<< oracle-astro-companion",
    ]

    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text("mcp_servers:\n" + "\n".join(snippet) + "\n", encoding="utf-8")
        return "created"

    text = CONFIG_PATH.read_text(encoding="utf-8")
    if "# >>> oracle-astro-companion" in text and not force:
        return "present"

    backup_file(CONFIG_PATH)

    if "mcp_servers:" not in text:
        new_text = text.rstrip() + "\n\nmcp_servers:\n" + "\n".join(snippet) + "\n"
    elif "\n  natal:" in text or text.startswith("natal:"):
        new_text = text
    else:
        new_text = text.replace("mcp_servers:\n", "mcp_servers:\n" + "\n".join(snippet) + "\n", 1)

    CONFIG_PATH.write_text(new_text, encoding="utf-8")
    return "merged"


def install(project_root: Path, force: bool = False) -> dict[str, str]:
    actions: dict[str, str] = {}
    project_root.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "cache").mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "reports").mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "journal").mkdir(parents=True, exist_ok=True)
    TARGET_SKILL_DIR.parent.mkdir(parents=True, exist_ok=True)

    soul_dst = project_root / "SOUL.md"
    copy_file(SCRIPT_ROOT / "SOUL.md", soul_dst, force=force)
    actions["project_soul"] = str(soul_dst)

    for filename in ["user_profile.json", "consent.yaml", "scoring_weights.yaml", ".env.example"]:
        src = SCRIPT_ROOT / filename
        dst = STATE_DIR / filename
        changed = copy_file(src, dst, force=force)
        actions[f"state_{filename}"] = f"{dst} ({'copied' if changed else 'kept'})"

    env_dst = STATE_DIR / ".env"
    if not env_dst.exists():
        env_dst.write_text((SCRIPT_ROOT / ".env.example").read_text(encoding="utf-8"), encoding="utf-8")
        actions["state_env"] = f"{env_dst} (created placeholder)"
    else:
        actions["state_env"] = f"{env_dst} (kept)"

    if TARGET_SKILL_DIR.exists() and force:
        shutil.rmtree(TARGET_SKILL_DIR)
    TARGET_SKILL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE_SKILL_DIR, TARGET_SKILL_DIR, dirs_exist_ok=True)
    actions["skill_dir"] = str(TARGET_SKILL_DIR)

    config_snippet_dst = STATE_DIR / "config.snippet.yaml"
    copy_file(SCRIPT_ROOT / "config.yaml", config_snippet_dst, force=True)
    actions["config_snippet"] = str(config_snippet_dst)
    actions["config_merge"] = merge_natal_mcp_config(force=force)
    return actions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install the Oracle source pack into live Hermes paths")
    parser.add_argument("--project-root", default=str(SCRIPT_ROOT.parent), help="Target project root for SOUL.md")
    parser.add_argument("--force", action="store_true", help="Overwrite existing seed files and refresh the skill directory")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    result = install(Path(args.project_root).expanduser().resolve(), force=args.force)
    for key, value in result.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
