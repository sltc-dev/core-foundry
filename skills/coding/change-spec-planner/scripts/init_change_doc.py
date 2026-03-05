#!/usr/bin/env python3
"""Generate a project change spec from the bundled templates."""

from __future__ import annotations

import argparse
import re
import unicodedata
from datetime import date
from pathlib import Path

TYPE_CHOICES = ("feat", "fix", "refactor", "chore", "project")
LEVEL_CHOICES = ("lite", "risky")
LEGACY_LEVEL_ALIASES = {"standard": "risky", "major": "risky"}
NON_ACTIONABLE_ISSUES = {"", "n/a", "na", "none", "-"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a change spec Markdown file in a target repository.",
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
        choices=LEVEL_CHOICES + tuple(LEGACY_LEVEL_ALIASES.keys()),
        default="lite",
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
        help="Optional file-name slug override",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root where docs/changes lives",
    )
    parser.add_argument(
        "--output-dir",
        help="Optional custom output directory; relative paths resolve from repo root",
    )
    parser.add_argument(
        "--no-reuse",
        action="store_true",
        help="Always create a new file and skip existing-spec detection",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).strip().lower()
    if not normalized:
        return "spec"

    parts: list[str] = []
    last_was_dash = False

    for char in normalized:
        if char.isalnum():
            parts.append(char)
            last_was_dash = False
            continue

        if not last_was_dash:
            parts.append("-")
            last_was_dash = True

    slug = "".join(parts).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug or "spec"


def resolve_output_dir(repo_root: Path, output_dir: str | None) -> Path:
    if not output_dir:
        candidate = repo_root / "docs" / "changes"
    else:
        configured = Path(output_dir)
        candidate = configured if configured.is_absolute() else repo_root / configured

    resolved_repo_root = repo_root.resolve()
    resolved_candidate = candidate.resolve()
    try:
        resolved_candidate.relative_to(resolved_repo_root)
    except ValueError as exc:
        raise SystemExit(
            "Output directory must stay inside repo root: "
            f"{resolved_candidate} not under {resolved_repo_root}"
        ) from exc
    return resolved_candidate


def yaml_single_quoted(value: str) -> str:
    sanitized = value.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ").strip()
    escaped = sanitized.replace("'", "''")
    return f"'{escaped}'"


def strip_yaml_quotes(value: str) -> str:
    trimmed = value.strip()
    if len(trimmed) >= 2 and trimmed[0] == trimmed[-1] == "'":
        return trimmed[1:-1].replace("''", "'")
    if len(trimmed) >= 2 and trimmed[0] == trimmed[-1] == '"':
        return trimmed[1:-1]
    return trimmed


def parse_frontmatter(markdown: str) -> dict[str, str]:
    if not markdown.startswith("---\n"):
        return {}

    end = markdown.find("\n---\n", 4)
    if end == -1:
        return {}

    data: dict[str, str] = {}
    for line in markdown[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = strip_yaml_quotes(value)
    return data


def normalize_for_match(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def issue_is_actionable(issue: str) -> bool:
    return normalize_for_match(issue) not in NON_ACTIONABLE_ISSUES


def find_existing_spec(
    output_dir: Path,
    *,
    title: str,
    issue: str,
    change_type: str,
    slug: str,
) -> Path | None:
    if not output_dir.exists():
        return None

    normalized_issue = normalize_for_match(issue)
    normalized_title = normalize_for_match(title)
    expected_suffix = f"-{change_type}-{slug}.md"
    issue_matches: list[Path] = []
    title_matches: list[Path] = []

    for path in sorted(output_dir.glob("*.md")):
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        existing_issue = normalize_for_match(frontmatter.get("related_issue", ""))
        existing_title = normalize_for_match(frontmatter.get("title", ""))

        if issue_is_actionable(issue) and existing_issue == normalized_issue:
            issue_matches.append(path)
            continue

        if path.name.endswith(expected_suffix) or (
            normalized_title and existing_title == normalized_title
        ):
            title_matches.append(path)

    matches = issue_matches if issue_matches else title_matches
    if not matches:
        return None

    if len(matches) > 1:
        joined = "\n".join(f"- {match}" for match in matches)
        raise SystemExit(
            "Multiple existing specs matched this request. "
            "Refine --issue/--slug or pass --no-reuse.\n"
            f"{joined}"
        )
    return matches[0]


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


def load_template() -> str:
    template_path = Path(__file__).resolve().parent.parent / "assets" / "templates" / "spec.md"
    if not template_path.exists():
        raise SystemExit(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def normalize_level(level: str) -> str:
    if level in LEVEL_CHOICES:
        return level
    if level in LEGACY_LEVEL_ALIASES:
        mapped = LEGACY_LEVEL_ALIASES[level]
        print(f"Warning: level '{level}' is deprecated; using '{mapped}' instead.")
        return mapped
    raise SystemExit(f"Unsupported level: {level}")


def render(template: str, mapping: dict[str, str]) -> str:
    rendered = template
    for key, value in mapping.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def main() -> int:
    args = parse_args()
    level = normalize_level(args.level)
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        raise SystemExit(f"Repository root not found: {repo_root}")
    if not repo_root.is_dir():
        raise SystemExit(f"Repository root is not a directory: {repo_root}")

    spec_day = date.fromisoformat(args.spec_date) if args.spec_date else date.today()
    day_iso = spec_day.isoformat()
    day_compact = spec_day.strftime("%Y%m%d")

    output_dir = resolve_output_dir(repo_root, args.output_dir)
    slug = args.slug or slugify(args.title)
    if not args.no_reuse:
        existing_spec = find_existing_spec(
            output_dir,
            title=args.title,
            issue=args.issue,
            change_type=args.type,
            slug=slug,
        )
        if existing_spec:
            print(f"Reusing existing spec: {existing_spec}")
            print("Next step: update this file instead of creating a duplicate.")
            return 0

    sequence = args.sequence or detect_sequence(output_dir, day_compact)
    if sequence <= 0:
        raise SystemExit("Sequence must be a positive integer.")

    change_id = f"CHG-{day_compact}-{sequence:03d}"
    file_name = f"{change_id}-{args.type}-{slug}.md"
    output_path = output_dir / file_name

    if output_path.exists() and not args.force:
        raise SystemExit(
            f"Refusing to overwrite existing file: {output_path}. Use --force to overwrite."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    template = load_template()
    content = render(
        template,
        {
            "ID": yaml_single_quoted(change_id),
            "TITLE": yaml_single_quoted(args.title),
            "TYPE": yaml_single_quoted(args.type),
            "LEVEL": yaml_single_quoted(level),
            "REVIEW_REQUIRED": "true" if level == "risky" else "false",
            "DATE": yaml_single_quoted(day_iso),
            "RELATED_ISSUE": yaml_single_quoted(args.issue),
        },
    )
    output_path.write_text(content, encoding="utf-8")

    print(f"Created: {output_path}")
    print(f"Level: {level}")
    print(f"Review required: {'yes' if level == 'risky' else 'no'}")
    if level == "risky":
        print("Next step: stop here and wait for human review approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
