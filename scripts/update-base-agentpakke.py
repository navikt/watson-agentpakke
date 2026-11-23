#!/usr/bin/env python3
"""Update inherited lockfile items from an exact navikt/copilot revision."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SOURCE = "navikt/copilot"
EXCLUDED_ITEMS = {"deliberate-ai-use"}
TYPE_OVERRIDES = {
    "accessibility": "instruction",
    "kafka": "agent",
    "security-owasp": "instruction",
}
TYPE_GROUPS = {
    "agents": "agent",
    "hooks": "hook",
    "instructions": "instruction",
    "prompts": "prompt",
    "skills": "skill",
    "extensions": "extension",
}


def list_upstream(ref: str) -> dict[str, str]:
    result = subprocess.run(
        [
            "nav-pilot",
            "list",
            "--source",
            SOURCE,
            "--ref",
            ref,
            "--items",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(f"nav-pilot returnerte ugyldig JSON for {ref}") from error

    groups = response.get("items")
    if not isinstance(groups, dict):
        raise ValueError(f"nav-pilot mangler et items-kart for {ref}")

    choices: dict[str, set[str]] = {}
    for group, item_type in TYPE_GROUPS.items():
        names = groups.get(group, [])
        if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
            raise ValueError(f"nav-pilot returnerte en ugyldig {group}-liste for {ref}")
        for name in names:
            if name not in EXCLUDED_ITEMS:
                choices.setdefault(name, set()).add(item_type)

    items: dict[str, str] = {}
    for name, types in choices.items():
        if name in TYPE_OVERRIDES:
            items[name] = TYPE_OVERRIDES[name]
        elif len(types) == 1:
            items[name] = next(iter(types))
        else:
            raise ValueError(f"Upstream har flere typer for {name}: {sorted(types)}")
    return items


def local_items(root: Path) -> dict[str, str]:
    items: dict[str, str] = {}
    for path in (root / "agents").glob("*.agent.md"):
        items[path.name.removesuffix(".agent.md")] = "agent"
    for path in (root / "skills").glob("*/SKILL.md"):
        items[path.parent.name] = "skill"
    for path in (root / "instructions").glob("*.instructions.md"):
        items[path.name.removesuffix(".instructions.md")] = "instruction"
    for path in (root / "extensions").glob("*/extension.mjs"):
        items[path.parent.name] = "extension"
    return items


def render_diff(old: dict[str, Any], new: dict[str, str], old_sha: str, new_sha: str) -> str:
    old_items = {name: item_type for name, item_type in old.items() if name not in EXCLUDED_ITEMS}
    added = sorted((name, new[name]) for name in new.keys() - old_items.keys())
    removed = sorted((name, old_items[name]) for name in old_items.keys() - new.keys())
    changed = sorted(
        (name, old_items[name], new[name])
        for name in old_items.keys() & new.keys()
        if old_items[name] != new[name]
    )

    lines = [
        f"Oppdatert base-SHA: `{old_sha}` → `{new_sha}`",
        "",
        "Elementendringer i `.nav-pilot/agentpakke.lock.json`:",
    ]
    if not (added or removed or changed):
        lines.append("- Ingen.")
    else:
        for name, item_type in added:
            lines.append(f"- Lagt til `{name}` ({item_type})")
        for name, item_type in removed:
            lines.append(f"- Fjernet `{name}` ({item_type})")
        for name, old_type, new_type in changed:
            lines.append(f"- Endret `{name}` fra {old_type} til {new_type}")
    lines.extend(
        [
            "",
            "Gå gjennom skyggefilene `agents/nav-pilot.agent.md` og "
            "`instructions/output-style.instructions.md` mot denne SHA-en før merge.",
        ]
    )
    return "\n".join(lines) + "\n"


def update_lockfile(lockfile: Path, package_root: Path, ref: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError("--ref må være en full SHA med 40 små hex-tegn")

    data = json.loads(lockfile.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Lockfila må inneholde et JSON-objekt")
    if data.get("source") != SOURCE:
        raise ValueError(f"Lockfila må ha source={SOURCE}")
    old_sha = data.get("sha")
    old_items = data.get("items")
    if not isinstance(old_sha, str) or not isinstance(old_items, dict):
        raise ValueError("Lockfila mangler sha eller items")

    latest = list_upstream(ref)
    previous = latest if old_sha == ref else list_upstream(old_sha)

    # Existing entries absent from the previous upstream revision are package-specific.
    custom = {
        name: item_type
        for name, item_type in old_items.items()
        if name not in previous and name not in EXCLUDED_ITEMS
    }
    # Keep locally shipped items even if an older lockfile did not list them yet.
    for name, item_type in local_items(package_root).items():
        if name not in latest and name not in EXCLUDED_ITEMS:
            custom.setdefault(name, item_type)

    merged = dict(latest)
    merged.update(custom)
    data["sha"] = ref
    data["items"] = dict(sorted(merged.items()))
    lockfile.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return render_diff(old_items, data["items"], old_sha, ref)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", required=True, help="Upstream commit SHA to lock")
    parser.add_argument(
        "--lockfile",
        type=Path,
        help="Lockfile to update (defaults to this repository's lockfile)",
    )
    parser.add_argument("--summary-file", type=Path, help="Write the item diff summary here")
    arguments = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    lockfile = arguments.lockfile or root / ".nav-pilot" / "agentpakke.lock.json"
    try:
        summary = update_lockfile(lockfile, root, arguments.ref)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"Oppdatering av base-agentpakke feilet: {error}", file=sys.stderr)
        return 1

    if arguments.summary_file:
        arguments.summary_file.write_text(summary, encoding="utf-8")
    print(summary, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
