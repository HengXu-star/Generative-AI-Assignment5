---
name: meeting-slot-normalizer
description: Normalizes pasted meeting slots into a target timezone, validates row structure, and flags overlaps or invalid entries. Use when the user provides interview schedules, office hours, or meeting options that need deterministic timezone conversion and conflict checks.
---

# Meeting Slot Normalizer

## When to use

Use this skill when the user wants to:

- convert a pasted schedule into one target timezone
- validate that meeting-slot rows are structurally correct
- detect overlapping availability windows
- turn structured slot data into a concise summary

## When not to use

Do not use this skill when:

- the user wants calendar booking or outbound email drafting
- the input is vague natural language such as "late afternoon next Friday"
- the user needs recurring calendar logic rather than one-time slots

## Expected inputs

Ask for meeting slots in this pipe-delimited format:

```text
label | start | end | source_timezone
```

Examples:

```text
Recruiter screen | 2026-05-02 15:00 | 2026-05-02 15:30 | America/Los_Angeles
Panel interview | 2026-05-02 18:00 | 2026-05-02 19:00 | America/Chicago
```

The timezone column is optional only if the user also supplies a default source timezone.

## Workflow

1. Confirm the target timezone, such as `America/New_York`.
2. If any row omits a timezone, confirm a `default_source_timezone`.
3. Save the slot text to a temporary file or pass it via stdin.
4. Run `scripts/normalize_slots.py` with:
   - `--target-tz`
   - optionally `--default-source-tz`
   - optionally `--input`
5. Read the JSON output.
6. Present:
   - normalized slots
   - invalid rows
   - overlap warnings
   - a short schedule summary

## Output format

Return a compact response with these sections:

- `Normalized slots`
- `Overlaps`
- `Invalid rows`
- `Summary`

If the script returns no normalized rows, explain why and suggest the required input format.

## Important checks

- Never guess a missing timezone unless the user explicitly provides a default source timezone.
- Treat vague date phrases as insufficiently deterministic and ask for a precise rewrite.
- Preserve the original row text when reporting invalid rows so the user can fix them quickly.
- If the script finds overlaps, call them out clearly instead of burying them in the table.

## Script

Use `scripts/normalize_slots.py` for the deterministic work. The script handles:

- parsing rows
- validating required fields
- converting timezones with `zoneinfo`
- detecting overlaps
- returning machine-readable JSON

See `references/input-format.md` if the user needs formatting examples.
