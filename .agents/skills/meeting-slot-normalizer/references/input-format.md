# Input Format

The skill expects one slot per line using pipes:

```text
label | start | end | source_timezone
```

Accepted datetime formats:

- `YYYY-MM-DD HH:MM`
- `YYYY-MM-DD HH:MM:SS`
- `YYYY-MM-DD HH:MM AM/PM`

Examples:

```text
Recruiter screen | 2026-05-02 15:00 | 2026-05-02 15:30 | America/Los_Angeles
System design | 2026-05-02 18:00 | 2026-05-02 19:00 | America/Chicago
Final debrief | 2026-05-03 09:30 AM | 2026-05-03 10:15 AM | Europe/London
```

If the timezone column is missing, the caller must provide `--default-source-tz`.

Rows that do not fit the structure are returned under `invalid_rows`.
