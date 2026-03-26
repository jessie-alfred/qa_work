# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a QA automation toolkit for the **Alfred Camera** app (Android/iOS surveillance application). It combines AI-powered test case generation with Firebase event validation and Google Sheets integration.

## Setup

```bash
pip install -r requirements.txt
```

External tools required:
- **Android testing**: Android SDK Platform Tools (`adb`)
- **iOS testing**: libimobiledevice (`idevicesyslog`)

## Key Scripts

### Firebase Event Validation (`firebase_event_log_validate.py`)

The primary tool. Captures device logs and validates Firebase events against specs in `firebase_event_specs/`.

```bash
# Validate Android events (30s capture window)
python firebase_event_log_validate.py verify-specs --timeout 30 --output verify_result.txt

# Validate iOS events
python firebase_event_log_validate.py verify-specs --platform ios --timeout 30

# Capture events to file without validation
python firebase_event_log_validate.py capture --output events.jsonl

# Stream events in real-time
python firebase_event_log_validate.py stream
```

Log format it parses: lines prefixed with `[Alfred][Event]` from `adb logcat` or `idevicesyslog`.

### Other Scripts

```bash
# Decode a JWT token (no signature validation)
python jwt_decode.py [optional_jwt_token]

# Convert Excel event spec to markdown
python xlsx_to_firebase_event_md.py [excel_file]
```

## Architecture

### QA Workflow

1. Receive JIRA ticket (CAMERA-XXXX) with PRD/Spec
2. Use the `alfredqa-testcase-creator` skill to generate test cases → output to `test_case/`
3. Convert markdown test cases to CSV for Google Sheets upload
4. Execute tests on device; capture Firebase logs with `firebase_event_log_validate.py`
5. Verify captured events against specs in `firebase_event_specs/`
6. Store results in `firebase_event_verify_result/`

### Firebase Event Spec System

Event specs in `firebase_event_specs/*.md` define:
- **Mandatory properties** — must exist and be non-empty
- **Optional properties** — may be present
- **Valid values/constraints** — data types and value ranges

The validation script compares captured `[Alfred][Event]` log events against these specs and reports missing mandatory properties. Output language is Traditional Chinese.

### Test Case AI Generation

`CURSOR.md` defines the QA engineer role for AI agents. When generating test cases, the agent:
- Analyzes PRD/Spec documents from `documents/`
- Reviews GitHub PR code changes for regression risk
- Produces test cases across 4 dimensions: functional correctness, user scenarios, system reliability, UX
- Outputs structured markdown to `test_case/CAMERA-XXXX_TestCase.md`

## Key File Locations

| Path | Purpose |
|------|---------|
| `firebase_event_specs/` | Event property definitions (18 specs) |
| `test_case/` | Generated test cases (markdown + CSV) |
| `firebase_event_verify_result/` | Validation run outputs |
| `documents/` | PRD, specs, core functionality docs |
| `android_firebase_event_rules_example.json` | Example validation rules format |
| `CURSOR.md` | AI role definition for test case generation |

## Validation Rules Format

Custom validation rules (`android_firebase_event_rules_example.json`) follow:
```json
{
  "name": "Rule name",
  "event_name": "event_name_string",
  "attributes": {"key": "value"},
  "match_once": true
}
```
