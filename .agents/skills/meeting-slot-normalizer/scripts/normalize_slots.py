#!/usr/bin/env python3
"""Normalize meeting slots into a target timezone and flag overlaps."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %I:%M %p",
    "%Y-%m-%d %I:%M:%S %p",
)


@dataclass
class Slot:
    label: str
    source_tz: str
    start_local: datetime
    end_local: datetime
    start_target: datetime
    end_target: datetime
    original: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize meeting slots into a target timezone.",
    )
    parser.add_argument(
        "--target-tz",
        required=True,
        help="IANA timezone name for normalized output, such as America/New_York.",
    )
    parser.add_argument(
        "--default-source-tz",
        help="Fallback source timezone for rows that omit the timezone column.",
    )
    parser.add_argument(
        "--input",
        help="Optional path to a text file containing pipe-delimited slot rows.",
    )
    return parser.parse_args()


def load_text(input_path: str | None) -> str:
    if input_path:
        return Path(input_path).read_text(encoding="utf-8")
    return sys.stdin.read()


def parse_datetime(value: str) -> datetime:
    cleaned = value.strip()
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    raise ValueError(
        "Unsupported datetime format. Use YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM AM/PM."
    )


def get_zoneinfo(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone '{name}'. Use an IANA timezone name.") from exc


def parse_slots(
    text: str,
    target_tz: str,
    default_source_tz: str | None,
) -> tuple[list[Slot], list[dict[str, str]]]:
    target_zone = get_zoneinfo(target_tz)
    slots: list[Slot] = []
    invalid_rows: list[dict[str, str]] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = [part.strip() for part in raw_line.split("|")]
        if len(parts) not in (3, 4):
            invalid_rows.append(
                invalid_row(
                    line_number,
                    raw_line,
                    "Expected 3 or 4 pipe-delimited fields: label | start | end | timezone",
                )
            )
            continue

        label, start_text, end_text = parts[:3]
        source_tz = parts[3] if len(parts) == 4 else default_source_tz

        if not label:
            invalid_rows.append(invalid_row(line_number, raw_line, "Label is required"))
            continue

        if not source_tz:
            invalid_rows.append(
                invalid_row(
                    line_number,
                    raw_line,
                    "Missing timezone. Add a timezone column or provide --default-source-tz.",
                )
            )
            continue

        try:
            source_zone = get_zoneinfo(source_tz)
            start_local = parse_datetime(start_text).replace(tzinfo=source_zone)
            end_local = parse_datetime(end_text).replace(tzinfo=source_zone)
        except ValueError as exc:
            invalid_rows.append(invalid_row(line_number, raw_line, str(exc)))
            continue

        if end_local <= start_local:
            invalid_rows.append(
                invalid_row(line_number, raw_line, "End time must be after start time.")
            )
            continue

        slots.append(
            Slot(
                label=label,
                source_tz=source_tz,
                start_local=start_local,
                end_local=end_local,
                start_target=start_local.astimezone(target_zone),
                end_target=end_local.astimezone(target_zone),
                original=raw_line,
            )
        )

    return slots, invalid_rows


def invalid_row(line_number: int, raw: str, error: str) -> dict[str, str]:
    return {
        "line": line_number,
        "raw": raw,
        "error": error,
    }


def build_overlap_report(slots: Iterable[Slot]) -> list[dict[str, object]]:
    ordered = sorted(slots, key=lambda slot: slot.start_target)
    overlaps: list[dict[str, object]] = []

    for index in range(len(ordered) - 1):
        current = ordered[index]
        nxt = ordered[index + 1]
        if current.end_target > nxt.start_target:
            overlaps.append(
                {
                    "first_label": current.label,
                    "second_label": nxt.label,
                    "first_start": current.start_target.isoformat(),
                    "first_end": current.end_target.isoformat(),
                    "second_start": nxt.start_target.isoformat(),
                    "second_end": nxt.end_target.isoformat(),
                }
            )
    return overlaps


def build_output(
    slots: list[Slot],
    invalid_rows: list[dict[str, str]],
    target_tz: str,
) -> dict[str, object]:
    normalized = [
        {
            "label": slot.label,
            "source_timezone": slot.source_tz,
            "target_timezone": target_tz,
            "original_start": slot.start_local.isoformat(),
            "original_end": slot.end_local.isoformat(),
            "normalized_start": slot.start_target.isoformat(),
            "normalized_end": slot.end_target.isoformat(),
            "original_row": slot.original,
        }
        for slot in sorted(slots, key=lambda item: item.start_target)
    ]

    overlaps = build_overlap_report(slots)

    return {
        "target_timezone": target_tz,
        "normalized_slots": normalized,
        "invalid_rows": invalid_rows,
        "overlaps": overlaps,
        "summary": {
            "normalized_count": len(normalized),
            "invalid_count": len(invalid_rows),
            "overlap_count": len(overlaps),
        },
    }


def main() -> int:
    args = parse_args()

    try:
        text = load_text(args.input)
        slots, invalid_rows = parse_slots(
            text=text,
            target_tz=args.target_tz,
            default_source_tz=args.default_source_tz,
        )
        output = build_output(slots, invalid_rows, args.target_tz)
    except Exception as exc:  # pragma: no cover - top-level CLI safety
        json.dump({"error": str(exc)}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 1

    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
