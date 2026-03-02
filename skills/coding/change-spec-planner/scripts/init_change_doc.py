#!/usr/bin/env python3
"""Generate a project change spec from the bundled templates."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

TYPE_CHOICES = ("feat", "fix", "refactor", "chore", "project")
LEVEL_CHOICES = ("lite", "standard", "major")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a change spec Markdown file in docs/changes/."
    )
    parser.add_argument("--title", required=True, help="Human-readable change title")
    parser.add_argument(
        "--type",
        choices=TYPE_CHOICES,
        default="feat",
        help="Change type used in frontmatter and file name",
    )
    parser.add_argument(
        "--level",
        choices=LEVEL_CHOICES,
        default="standard",
        help="Spec template level",
    )
    parser.add_argument(
        "--issue",
        default="N/A",
        help="Related issue ID, ticket number, or URL",
    )
    parser.add_argument(
        "--date",
        dest="spec_date",
        help="Override date in YYYY-MM-DD format; defaults to today",
    )
    parser.add_argument(
        "--sequence",
        type=int,
        help="Optional manual sequence number for the day",
    )
    parser.add_argument(
        "--slug",
        help="Optional ASCII slug override for the file name",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/changes",
        help="Directory for generated specs",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug or "spec"


def detect_sequence(output_dir: Path, day_compact: str) -> int:
    pattern = re.compile(rf"^CHG-{re.escape(day_compact)}-(\d{{3}})-")
    max_sequence = 0

    if not output_dir.exists():
        return 1

    for path in output_dir.glob(f"CHG-{day_compact}-*.md"):
        match = pattern.match(path.name)
        if match:
            max_sequence = max(max_sequence, int(match.group(1)))

    return max_sequence + 1


def load_template(level: str) -> str:
    template_path = (
        Path(__file__).resolve().parent.parent / "assets" / "templates" / f"{level}.md"
    )
    if not template_path.exists():
        raise SystemExit(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def render(template: str, mapping: dict[str, str]) -> str:
    rendered = template
    for key, value in mapping.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def main() -> int:
    args = parse_args()
    spec_day = date.fromisoformat(args.spec_date) if args.spec_date else date.today()
    day_iso = spec_day.isoformat()
    day_compact = spec_day.strftime("%Y%m%d")
    output_dir = Path(args.output_dir)
    sequence = args.sequence or detect_sequence(output_dir, day_compact)
    if sequence <= 0:
        raise SystemExit("Sequence must be a positive integer.")

    slug = args.slug or slugify(args.title)
    change_id = f"CHG-{day_compact}-{sequence:03d}"
    file_name = f"{change_id}-{args.type}-{slug}.md"
    output_path = output_dir / file_name

    if output_path.exists() and not args.force:
        raise SystemExit(
            f"Refusing to overwrite existing file: {output_path}. Use --force to overwrite."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    template = load_template(args.level)
    content = render(
        template,
        {
            "ID": change_id,
            "TITLE": args.title,
            "TYPE": args.type,
            "DATE": day_iso,
            "RELATED_ISSUE": args.issue,
        },
    )
    output_path.write_text(content, encoding="utf-8")

    print(f"Created: {output_path}")
    print(f"Level: {args.level}")
    print(f"Review required: {'yes' if args.level != 'lite' else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
