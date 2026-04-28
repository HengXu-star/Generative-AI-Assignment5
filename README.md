# HW5 Skill Project

## Project

This project packages one reusable AI skill called `meeting-slot-normalizer`. The skill converts pasted meeting slots from mixed source time zones into one target timezone, validates the row structure, and flags overlapping windows or invalid entries.

## Why I Chose This Skill

I chose this idea because timezone conversion looks simple, but it breaks easily without deterministic code. Interview scheduling, office hours, and cross-timezone meeting planning are realistic workflows where an agent can help explain the result, but a script should do the actual parsing, normalization, and conflict detection.

## Why The Script Is Load-Bearing

The Python script is central to the workflow. It:

- parses structured slot rows
- validates the required fields
- converts times with `zoneinfo`
- catches invalid rows
- detects overlaps in the normalized timeline
- returns consistent JSON for the agent to summarize

This is not something a plain prompt can do reliably on its own.

## Folder Structure

```text
hw5-mac/
├─ .agents/
│  └─ skills/
│     └─ meeting-slot-normalizer/
│        ├─ SKILL.md
│        ├─ references/
│        │  └─ input-format.md
│        └─ scripts/
│           └─ normalize_slots.py
└─ README.md
```

## How To Use The Skill

Ask the agent to normalize meeting slots into a target timezone. The expected input format is:

```text
label | start | end | source_timezone
```

Example:

```text
Recruiter screen | 2026-05-02 15:00 | 2026-05-02 15:30 | America/Los_Angeles
Panel interview | 2026-05-02 18:00 | 2026-05-02 19:00 | America/Chicago
```

Then run:

```bash
python3 .agents/skills/meeting-slot-normalizer/scripts/normalize_slots.py \
  --target-tz America/New_York \
  --input sample_slots.txt
```

If some rows omit the timezone column, add:

```bash
--default-source-tz America/Chicago
```

## Example Prompts For The Agent

### Normal case

Normalize these interview slots to `America/New_York` and flag any overlaps.

### Edge case

Convert these meeting options to `America/New_York`. Some rows are missing a timezone, so use `America/Chicago` as the default source timezone.

### Cautious or partial-decline case

Normalize `next Friday afternoon`, `lunchish PST`, and `around 4 in London`.

The agent should respond that the input is too ambiguous for deterministic conversion and ask for precise timestamps in the documented format.

## What Worked Well

- The skill is narrow and easy to trigger from the description.
- The script does a clearly necessary deterministic job.
- The JSON output makes it easy for an agent to produce a concise human summary.
- The edge case and caution case are both easy to demonstrate in a short video.

## Limitations

- The script expects structured rows, not freeform natural language.
- It does not integrate with calendar APIs.
- It handles one-time meeting slots, not recurring schedules.
- It uses accepted timestamp formats rather than trying to infer every possible format.

## Video Link

Add your recording link here before submission:

`VIDEO_LINK_HERE`
