from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sys

from .core import load_activities, load_manifest
from .generator import generate_proposal_batch
from .render import write_outputs


def proposal_limit(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("limit must be an integer from 1 to 3") from exc
    if parsed < 1 or parsed > 3:
        raise argparse.ArgumentTypeError("limit must be an integer from 1 to 3")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-maker",
        description="Recommend agents based on the work someone already does.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    run = subcommands.add_parser("run", help="generate source report, proposals, and scaffold specs")
    run.add_argument("--manifest", required=True, type=Path, help="JSON source manifest")
    run.add_argument("--activities", type=Path, help="JSONL normalized activity records")
    run.add_argument("--out", type=Path, help="output directory; defaults to a private run folder under ~/scripts_output/agent-maker/runs")
    run.add_argument("--limit", type=proposal_limit, default=3, help="maximum proposals to generate, from 1 to 3")
    run.add_argument("--overwrite", action="store_true", help="allow overwriting an existing agent-maker output directory")
    run.add_argument("--allow-outside-scripts-output", action="store_true", help="allow output outside ~/scripts_output/agent-maker")

    return parser


def run(args: argparse.Namespace) -> int:
    sources = load_manifest(args.manifest)
    activities = load_activities(args.activities)
    proposal_batch = generate_proposal_batch(sources, activities, limit=args.limit)
    proposals = list(proposal_batch.selected)
    out_dir = resolve_output_dir(args.out)
    validate_output_dir(out_dir, overwrite=args.overwrite, allow_outside=args.allow_outside_scripts_output)
    if args.overwrite:
        clear_managed_outputs(out_dir, allow_unmarked=is_safe_output_dir(out_dir))
    written = write_outputs(out_dir, sources, proposals, proposal_batch.rejected)
    write_run_marker(out_dir)
    print(f"Generated {len(proposals)} proposal(s)")
    for path in written:
        print(path)
    if not proposals:
        print("No proposals generated. Approve read-only sources and provide activity records with work-pattern signals.")
    return 0


def resolve_output_dir(requested: Path | None) -> Path:
    if requested is not None:
        return requested.expanduser().resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return (Path.home() / "scripts_output" / "agent-maker" / "runs" / stamp).resolve()


def validate_output_dir(out_dir: Path, overwrite: bool, allow_outside: bool) -> None:
    safe_root = safe_output_root()
    if not allow_outside and not is_safe_output_dir(out_dir):
        raise SystemExit(f"output must be under {safe_root} unless --allow-outside-scripts-output is set")
    if overwrite and allow_outside and not is_safe_output_dir(out_dir) and out_dir.exists() and any(out_dir.iterdir()) and not is_agent_maker_output(out_dir):
        raise SystemExit(f"refusing to overwrite non-agent-maker output directory outside {safe_root}: {out_dir}")
    if out_dir.exists() and any(out_dir.iterdir()) and not overwrite:
        raise SystemExit(f"output directory already exists and is not empty: {out_dir}; pass --overwrite or choose a new path")


def safe_output_root() -> Path:
    return (Path.home() / "scripts_output" / "agent-maker").resolve()


def is_safe_output_dir(out_dir: Path) -> bool:
    safe_root = safe_output_root()
    return out_dir == safe_root or safe_root in out_dir.parents


def clear_managed_outputs(out_dir: Path, *, allow_unmarked: bool = False) -> None:
    if out_dir.exists() and any(out_dir.iterdir()) and not allow_unmarked and not is_agent_maker_output(out_dir):
        raise SystemExit(f"refusing to overwrite non-agent-maker output directory: {out_dir}")
    for name in ("source-report.md", "index.md"):
        target = out_dir / name
        if target.exists():
            target.unlink()
    for name in ("proposals", "scaffolds"):
        target = out_dir / name
        if target.exists():
            shutil.rmtree(target)


def is_agent_maker_output(out_dir: Path) -> bool:
    marker = out_dir / ".agent-maker-run"
    return marker.is_file()


def write_run_marker(out_dir: Path) -> None:
    marker = out_dir / ".agent-maker-run"
    marker.write_text("agent-maker-output\n", encoding="utf-8")
    os.chmod(marker, 0o600)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "run":
            return run(args)
        parser.error(f"unknown command: {args.command}")
    except (FileNotFoundError, ValueError) as exc:
        parser.exit(1, f"agent-maker: error: {exc}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
