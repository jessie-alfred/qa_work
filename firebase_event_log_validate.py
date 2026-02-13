#!/usr/bin/env python3
"""
Android / iOS Firebase 事件 log 擷取與驗證工具。

用途：
1. 用 adb logcat（Android）或 idevicesyslog（iOS）過濾並擷取 [Alfred][Event] 的 Firebase 事件 log
2. 依驗證規則或 firebase_event_specs/*.md 檢查擷取到的事件是否符合預期

使用方式：
  Android（預設）：
    python android_firebase_logcat.py verify-specs --timeout 30 --output verify_result.txt
  iOS（需先安裝 libimobiledevice，裝置接 USB）：
    python android_firebase_logcat.py verify-specs --platform ios --timeout 30 --output verify_result.txt
  擷取到檔案：capture --output events.jsonl [--platform android|ios]
  即時顯示：stream [--platform android|ios]
  依 firebase_event_specs 驗證：verify-specs [--platform android|ios] [--timeout 0]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator

# log 中 Firebase 事件的前綴，後面接 JSON
EVENT_PREFIX = "[Alfred][Event] "
EVENT_PREFIX_PATTERN = re.compile(re.escape(EVENT_PREFIX))

# verify-specs 時不檢查、直接視為略過驗證的事件名稱
IGNORED_EVENT_NAMES = frozenset({
    "screen_view", "error_log", "permission_status", "convert: click subscription plan","initial_login_succeeded","continuous_recording_playback_memo_1"
})


def run_logcat(filter_tag: str | None = None) -> Iterator[str]:
    """執行 adb logcat 並 yield 每一行。可選 filter_tag 只抓特定 tag。"""
    cmd = ["adb", "logcat", "-v", "time"]
    if filter_tag:
        cmd.extend(["-s", f"{filter_tag}:V"])
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
    )
    try:
        for line in proc.stdout:
            yield line.rstrip("\n")
    finally:
        proc.terminate()
        proc.wait(timeout=2)


def run_ios_log() -> Iterator[str]:
    """執行 idevicesyslog（iOS 裝置需接 USB，需安裝 libimobiledevice）並 yield 每一行。"""
    proc = subprocess.Popen(
        ["idevicesyslog"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
    )
    try:
        for line in proc.stdout:
            yield line.rstrip("\n")
    finally:
        proc.terminate()
        proc.wait(timeout=2)


def run_log_stream(platform: str, filter_tag: str | None = None) -> Iterator[str]:
    """依 platform 執行 Android adb logcat 或 iOS idevicesyslog，yield 每一行。"""
    if platform == "ios":
        return run_ios_log()
    return run_logcat(filter_tag=filter_tag)


MONTH_ABBR_TO_NUM = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}


def extract_log_timestamp(line: str, platform: str = "android") -> str:
    """從 log 行開頭擷取時間戳。Android: MM-DD HH:MM:SS.mmm；iOS idevicesyslog: Mon DD HH:MM:SS。"""
    parts = line.split()
    if len(parts) >= 2 and re.match(r"\d{2}-\d{2}", parts[0]) and re.match(r"\d{2}:\d{2}:\d{2}", parts[1]):
        return f"{parts[0]} {parts[1]}"
    if platform == "ios" and len(parts) >= 3:
        mon, day, time_part = parts[0], parts[1], parts[2]
        if mon in MONTH_ABBR_TO_NUM and re.match(r"\d{1,2}", day) and re.match(r"\d{2}:\d{2}:\d{2}", time_part):
            mm = MONTH_ABBR_TO_NUM[mon]
            dd = day.zfill(2) if len(day) == 1 else day
            return f"{mm}-{dd} {time_part}"
    return ""


def parse_log_line(line: str) -> dict[str, Any] | None:
    """
    若該行包含 [Alfred][Event] 且後面為合法 JSON，回傳解析後的 dict，否則回傳 None。
    範例輸入：
      [Alfred][Event] {"type":"firebase","event_name":"event_play","attributes":{...}}
    """
    if EVENT_PREFIX not in line:
        return None
    idx = line.find(EVENT_PREFIX)
    payload = line[idx + len(EVENT_PREFIX) :].strip()
    if not payload:
        return None
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


def events_from_log_stream(
    platform: str = "android",
    filter_tag: str | None = None,
    filter_firebase_only: bool = False,
) -> Iterator[dict[str, Any]]:
    """從 Android logcat 或 iOS idevicesyslog 串流中只 yield 解析成功的 Firebase 事件，帶 _log_timestamp、_platform。"""
    for line in run_log_stream(platform=platform, filter_tag=filter_tag):
        if filter_firebase_only and "firebase" not in line:
            continue
        ev = parse_log_line(line)
        if ev is not None and ev.get("type") in ("firebase", "firebase_v2"):
            ev["_log_timestamp"] = extract_log_timestamp(line, platform=platform)
            ev["_platform"] = platform
            yield ev


# ---------- firebase_event_specs 解析與驗證 ----------


def _parse_spec_md(content: str) -> tuple[str, Any]:
    """
    解析單一 *_event_spec.md 內容。
    回傳 (event_name, spec)。
    spec 為 list[(property_name, requirement)] 或 dict[function_name, list[(prop, requirement)]]（function_behavior 依 function 分組）。
    """
    event_name = ""
    lines = content.split("\n")
    for line in lines:
        if line.startswith("# 事件追蹤規範："):
            event_name = line.replace("# 事件追蹤規範：", "").strip()
            break
    if not event_name:
        return "", []

    in_table = False
    header_cells: list[str] = []
    prop_idx = -1
    req_idx = -1
    data_type_idx = -1
    firebase_idx = -1  # function name 欄（function_behavior 用）
    current_prop = ""
    props: list[tuple[str, str, str]] = []
    by_function: dict[str, list[tuple[str, str, str]]] = {}
    current_function = ""
    seen_per_function: dict[str, set[str]] = {}

    for line in lines:
        line = line.strip()
        if "## 事件屬性" in line or "## 事件屬性 (Event Properties)" in line:
            in_table = False
            header_cells = []
            continue
        if not in_table and "|" in line and "Event Property" in line and ("Requirement" in line or "Data Type" in line):
            in_table = True
            header_cells = [c.strip() for c in line.split("|") if c.strip()]
            try:
                prop_idx = header_cells.index("Event Property")
            except ValueError:
                prop_idx = 0
            try:
                req_idx = header_cells.index("Requirement")
            except ValueError:
                req_idx = 1
            try:
                data_type_idx = header_cells.index("Data Type")
            except ValueError:
                data_type_idx = -1
            try:
                firebase_idx = header_cells.index("Firebase")
            except ValueError:
                firebase_idx = -1
            continue
        if not in_table or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if not cells or all(c == "---" or not c for c in cells):
            continue
        if firebase_idx >= 0 and firebase_idx < len(cells) and cells[firebase_idx]:
            current_function = cells[firebase_idx]
            if current_function and current_function not in by_function:
                by_function[current_function] = []
                seen_per_function[current_function] = set()
        if prop_idx < len(cells) and cells[prop_idx]:
            current_prop = cells[prop_idx]
        if not current_prop:
            continue
        req = (cells[req_idx] if req_idx < len(cells) else "").strip()
        data_type = (cells[data_type_idx] if data_type_idx >= 0 and data_type_idx < len(cells) else "").strip()
        if "Mandatory" in req:
            req_val = "Mandatory"
        else:
            req_val = "Optional"
        if firebase_idx >= 0 and current_function:
            if current_prop not in seen_per_function.get(current_function, set()):
                seen_per_function.setdefault(current_function, set()).add(current_prop)
                by_function.setdefault(current_function, []).append((current_prop, req_val, data_type))
        else:
            if current_prop not in {p[0] for p in props}:
                props.append((current_prop, req_val, data_type))

    if event_name == "function_behavior" and by_function:
        return event_name, by_function
    return event_name, props


def load_specs_from_dir(specs_dir: str | Path) -> dict[str, Any]:
    """
    從 firebase_event_specs 目錄載入所有 *_event_spec.md。
    回傳 { event_name: [(property_name, requirement), ...] } 或 function_behavior 為 { function_name: [(prop, requirement), ...] }。
    """
    specs_dir = Path(specs_dir)
    if not specs_dir.is_dir():
        return {}
    out: dict[str, Any] = {}
    for path in sorted(specs_dir.glob("*_event_spec.md")):
        text = path.read_text(encoding="utf-8")
        name, spec = _parse_spec_md(text)
        if name:
            out[name] = spec
    return out


def validate_event_against_spec(
    event: dict[str, Any],
    spec: Any,
) -> tuple[list[str], list[str]]:
    """
    檢查單一事件是否符合 spec（Mandatory 屬性必須存在且非空）。
    spec 可為 list[(prop, requirement, data_type)] 或 function_behavior 的 dict；依 event 的 function 只驗證該 function 的必填。
    回傳 (errors, warnings)。errors 為 FAIL；warnings 為 [WARNING]（屬性值 "none" 或 Number 型且值為 0）。
    """
    errors: list[str] = []
    warnings: list[str] = []
    attrs = event.get("attributes") or {}
    event_name = event.get("event_name", "?")

    if isinstance(spec, dict):
        func_name = attrs.get("function") or attrs.get("action") or ""
        prop_list = spec.get(func_name) if func_name else []
        if not func_name:
            errors.append(f"事件 {event_name} 缺少屬性 function（無法對應 spec）")
            return errors, warnings
        if not prop_list and func_name not in spec:
            prop_list = []
    else:
        prop_list = spec or []

    def _ensure_3tuple(t: tuple) -> tuple[str, str, str]:
        if len(t) >= 3:
            return (t[0], t[1], t[2])
        return (t[0], t[1], "")

    for item in prop_list:
        prop_name, requirement, data_type = _ensure_3tuple(item)
        if requirement != "Mandatory":
            continue
        val = attrs.get(prop_name)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            errors.append(f"事件 {event_name} 缺少必填屬性: {prop_name}")
    for key, val in attrs.items():
        if val is not None and isinstance(val, str) and val.strip() == "":
            errors.append(f"事件 {event_name} 屬性 {key} 為空字串")
    # WARNING: 屬性值為 "none" 或 (spec 為 Number 型且值為 0)
    prop_data_types: dict[str, str] = {_ensure_3tuple(t)[0]: _ensure_3tuple(t)[2] for t in prop_list}
    for key, val in attrs.items():
        if isinstance(val, str) and val.strip().lower() == "none":
            warnings.append(f"事件 {event_name} 屬性 {key} 為 \"none\"")
        elif isinstance(val, (int, float)) and val == 0:
            dt = prop_data_types.get(key, "")
            if dt and "number" in dt.lower():
                warnings.append(f"事件 {event_name} 屬性 {key} (Number) 為 0")
    return errors, warnings


def load_rules(path: str) -> list[dict[str, Any]]:
    """從 JSON 檔案載入驗證規則。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "rules" in data:
        return data["rules"]
    return [data]


def event_matches_rule(event: dict[str, Any], rule: dict[str, Any]) -> bool:
    """
    檢查單一事件是否符合一條規則。
    規則格式：
      - event_name: "event_play"          # 必須完全符合
      - event_name_regex: "event_.*"      # 或用 regex（與 event_name 二擇一）
      - type: "firebase"                  # 可選
      - attributes:                       # 可選，子鍵為 key，值為預期（或 regex 字串）
          entry: "event list"
          event_source: "cloud"
      - attributes_contains:              # 可選，只檢查 key 存在且值為真
          event_id: true
    """
    if "event_name" in rule:
        if event.get("event_name") != rule["event_name"]:
            return False
    if "event_name_regex" in rule:
        name = event.get("event_name") or ""
        if not re.search(rule["event_name_regex"], name):
            return False
    if "type" in rule and event.get("type") != rule["type"]:
        return False

    attrs = event.get("attributes") or {}
    if "attributes" in rule:
        for key, expected in rule["attributes"].items():
            actual = attrs.get(key)
            if isinstance(expected, str) and expected.startswith("regex:"):
                if not re.search(expected[6:], str(actual) if actual is not None else ""):
                    return False
            elif actual != expected:
                return False
    if "attributes_contains" in rule:
        for key, required in rule["attributes_contains"].items():
            if not required:
                continue
            if key not in attrs or attrs[key] is None or attrs[key] == "":
                return False
    return True


def verify_events(
    events: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> tuple[list[dict], list[dict]]:
    """
    依規則驗證事件列表。
    回傳 (matched_rules, failed_rules)。
    matched_rules: 每條含 rule, matched_event, index
    failed_rules: 每條含 rule, reason
    """
    matched: list[dict] = []
    failed: list[dict] = []
    used_indices: set[int] = set()

    for rule in rules:
        rule_name = rule.get("name") or rule.get("event_name") or str(rule)
        found = False
        for i, ev in enumerate(events):
            if i in used_indices:
                continue
            if event_matches_rule(ev, rule):
                matched.append({"rule": rule, "rule_name": rule_name, "event": ev, "index": i})
                if rule.get("match_once", True):
                    used_indices.add(i)
                found = True
                if rule.get("match_once", True):
                    break
        if not found:
            failed.append({
                "rule": rule,
                "rule_name": rule_name,
                "reason": "no_matching_event",
            })
    return matched, failed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="擷取並驗證 Android [Alfred][Event] Firebase 事件 log",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # capture: 擷取到檔案
    cap = sub.add_parser("capture", help="擷取事件到 JSONL 檔案")
    cap.add_argument("--output", "-o", default="firebase_events.jsonl", help="輸出 JSONL 路徑")
    cap.add_argument("--platform", "-p", choices=("android", "ios"), default="android", help="裝置平台（iOS 需安裝 libimobiledevice 且裝置接 USB）")
    cap.add_argument("--tag", "-t", default=None, help="logcat tag 過濾（僅 Android）")
    cap.add_argument("--limit", "-n", type=int, default=0, help="最多擷取幾筆後結束（0=不限制）")

    # stream: 即時印出
    stream = sub.add_parser("stream", help="即時印出事件到 stdout")
    stream.add_argument("--platform", "-p", choices=("android", "ios"), default="android", help="裝置平台")
    stream.add_argument("--tag", "-t", default=None, help="logcat tag 過濾（僅 Android）")

    # verify: 驗證
    verify = sub.add_parser("verify", help="依規則驗證事件")
    verify.add_argument("--rules", "-r", required=True, help="驗證規則 JSON 路徑")
    verify.add_argument("--input", "-i", default=None, help="事件來源：JSONL 檔案；若省略則即時從 log 讀取（需手動停止）")
    verify.add_argument("--platform", "-p", choices=("android", "ios"), default="android", help="裝置平台（僅 --input 省略時有效）")
    verify.add_argument("--tag", "-t", default=None, help="logcat tag 過濾（僅 Android）")
    verify.add_argument("--timeout", type=float, default=0, help="從 log 讀取時的最多等待秒數（0=不限制）")

    # verify-specs: 依 firebase_event_specs/*.md 驗證
    verify_specs = sub.add_parser(
        "verify-specs",
        help="執行 Android logcat 或 iOS idevicesyslog，過濾 [Alfred][Event] 且含 firebase，並依 firebase_event_specs 驗證",
    )
    verify_specs.add_argument(
        "--platform",
        "-p",
        choices=("android", "ios"),
        default="android",
        help="裝置平台（iOS 需安裝 libimobiledevice、裝置接 USB）",
    )
    verify_specs.add_argument(
        "--specs-dir",
        "-s",
        default="firebase_event_specs",
        help="firebase_event_specs 目錄路徑（預設: firebase_event_specs）",
    )
    verify_specs.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=0,
        help="擷取秒數後結束（0=不限制，手動 Ctrl+C）",
    )
    verify_specs.add_argument(
        "--input",
        "-i",
        default=None,
        help="改從 JSONL 檔案驗證（不跑 log）",
    )
    verify_specs.add_argument(
        "--output",
        "-o",
        default=None,
        help="將驗證結果寫入此檔案（與終端機輸出相同內容）",
    )
    verify_specs.add_argument(
        "--record-screen",
        action="store_true",
        help="錄製期間同時錄製裝置畫面（僅 Android，檔名同結果 .mp4）",
    )

    args = parser.parse_args()

    if args.command == "capture":
        platform = getattr(args, "platform", "android")
        count = 0
        with open(args.output, "w", encoding="utf-8") as out:
            for ev in events_from_log_stream(platform=platform, filter_tag=args.tag):
                out.write(json.dumps(ev, ensure_ascii=False) + "\n")
                out.flush()
                count += 1
                if args.limit and count >= args.limit:
                    break
        print(f"已寫入 {count} 筆事件到 {args.output}", file=sys.stderr)

    elif args.command == "stream":
        platform = getattr(args, "platform", "android")
        for ev in events_from_log_stream(platform=platform, filter_tag=args.tag):
            print(json.dumps(ev, ensure_ascii=False))

    elif args.command == "verify":
        rules = load_rules(args.rules)
        if args.input:
            events = []
            with open(args.input, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        else:
            import time
            platform = getattr(args, "platform", "android")
            events = []
            start = time.monotonic()
            for ev in events_from_log_stream(platform=platform, filter_tag=args.tag):
                events.append(ev)
                if args.timeout and (time.monotonic() - start) >= args.timeout:
                    break
        matched, failed = verify_events(events, rules)
        for m in matched:
            print(f"[PASS] {m['rule_name']}", file=sys.stderr)
        for f in failed:
            print(f"[FAIL] {f['rule_name']}: {f['reason']}", file=sys.stderr)
        if failed:
            sys.exit(1)
        print("All rules passed.", file=sys.stderr)

    elif args.command == "verify-specs":
        specs_dir = Path(args.specs_dir)
        if not specs_dir.is_absolute():
            specs_dir = Path(__file__).parent / specs_dir
        all_specs = load_specs_from_dir(specs_dir)
        if not all_specs:
            print(f"錯誤：在 {specs_dir} 找不到 *_event_spec.md", file=sys.stderr)
            sys.exit(2)

        from datetime import datetime
        ts = datetime.now()
        ts_iso = ts.isoformat(timespec="seconds")
        ts_file = ts.strftime("%Y%m%d_%H%M%S")
        plat = getattr(args, "platform", "android")

        if args.input:
            events = []
            with open(args.input, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                        if ev.get("type") in ("firebase", "firebase_v2"):
                            ev_platform = ev.get("_platform")
                            if ev_platform is None or ev_platform == plat:
                                events.append(ev)
                    except json.JSONDecodeError:
                        pass
        else:
            platform = plat
            events = []
            import time
            rec_proc = None
            rec_duration = int(args.timeout) if args.timeout > 0 else 180
            rec_name = f"verify_result_{plat}_{ts_file}"
            if getattr(args, "record_screen", False) and platform == "android":
                rec_path = f"/sdcard/{rec_name}.mp4"
                rec_proc = subprocess.Popen(
                    ["adb", "shell", "screenrecord", "--time-limit", str(rec_duration), rec_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print(f"開始錄製畫面 ({rec_duration}s)：{rec_name}.mp4", file=sys.stderr)
            start = time.monotonic()
            try:
                for ev in events_from_log_stream(platform=platform, filter_firebase_only=True):
                    events.append(ev)
                    if args.timeout and (time.monotonic() - start) >= args.timeout:
                        break
            finally:
                if rec_proc is not None:
                    try:
                        rec_proc.wait(timeout=rec_duration + 10)
                    except subprocess.TimeoutExpired:
                        rec_proc.terminate()
                        rec_proc.wait(timeout=2)
                    verify_result_dir = Path(__file__).parent / "firebase_event_verify_result"
                    verify_result_dir.mkdir(exist_ok=True)
                    out_mp4 = verify_result_dir / f"{rec_name}.mp4"
                    subprocess.run(["adb", "pull", rec_path, str(out_mp4)], capture_output=True)
                    subprocess.run(["adb", "shell", "rm", "-f", rec_path], capture_output=True)
                    if out_mp4.exists():
                        print(f"畫面錄製已寫入 {out_mp4}", file=sys.stderr)

        total = len(events)
        passed_list: list[dict[str, Any]] = []
        failed_list: list[tuple[dict[str, Any], list[str]]] = []
        ignored_list: list[dict[str, Any]] = []
        warning_list: list[tuple[dict[str, Any], list[str]]] = []
        fb_spec = all_specs.get("function_behavior")
        for ev in events:
            name = ev.get("event_name", "")
            if name in IGNORED_EVENT_NAMES:
                ignored_list.append(ev)
                continue
            spec = all_specs.get(name)
            ev_for_validate = ev
            if spec is None and isinstance(fb_spec, dict) and name in fb_spec:
                spec = fb_spec
                ev_for_validate = {**ev, "attributes": {**ev.get("attributes", {}), "function": name}}
            if spec is None:
                failed_list.append((ev, [f"事件 {name} 未在 firebase_event_specs 中定義"]))
                continue
            errs, warns = validate_event_against_spec(ev_for_validate, spec)
            if errs:
                failed_list.append((ev, errs))
            elif warns:
                warning_list.append((ev, warns))
            else:
                passed_list.append(ev)

        report_lines: list[str] = []
        report_lines.append(f"Firebase 事件驗證結果 ({plat.upper()} / {ts_iso})")
        report_lines.append("")
        report_lines.append(f"共擷取 {total} 筆 Firebase 事件，符合規範: {len(passed_list)}，不符合: {len(failed_list)}，注意: {len(warning_list)}，忽略: {len(ignored_list)}")
        if total == 0 and not args.input:
            if plat == "ios":
                report_lines.append("未擷取到任何事件。請確認：iOS 裝置已接 USB、已安裝 libimobiledevice (brew install libimobiledevice)、app 有觸發 Firebase 事件、或可加長 --timeout。")
            else:
                report_lines.append("未擷取到任何事件。請確認：裝置已連接 (adb devices)、app 有觸發 Firebase 事件、或可加長 --timeout。")
        def _ts(ev: dict) -> str:
            return ev.get("_log_timestamp", "")

        report_lines.append("")
        report_lines.append("--- 符合規範 [PASS] ---")
        for ev in sorted(passed_list, key=_ts):
            ts = _ts(ev)
            report_lines.append(f"  [PASS] {ev.get('event_name', '?')}" + (f" | {ts}" if ts else ""))
            report_lines.append(f"    {json.dumps(ev.get('attributes', {}), ensure_ascii=False)}")
        report_lines.append("")
        report_lines.append("--- 注意 [WARNING] ---")
        report_lines.append("  （屬性值為 \"none\" 或 Number 型且值為 0）")
        for ev, warns in sorted(warning_list, key=lambda x: _ts(x[0])):
            ts = _ts(ev)
            report_lines.append(f"  [WARNING] {ev.get('event_name', '?')}: {'; '.join(warns)}" + (f" | {ts}" if ts else ""))
            report_lines.append(f"    {json.dumps(ev.get('attributes', {}), ensure_ascii=False)}")
        if not warning_list:
            report_lines.append("  (無)")
        report_lines.append("")
        report_lines.append("--- 不符合 [FAIL] ---")
        for ev, errs in sorted(failed_list, key=lambda x: _ts(x[0])):
            ts = _ts(ev)
            report_lines.append(f"  [FAIL] {ev.get('event_name', '?')}: {'; '.join(errs)}" + (f" | {ts}" if ts else ""))
            report_lines.append(f"    {json.dumps(ev.get('attributes', {}), ensure_ascii=False)}")
        if not failed_list:
            report_lines.append("  (無)")
        report_lines.append("")
        report_lines.append("--- 忽略不檢查 [IGNORE] ---")
        for ev in sorted(ignored_list, key=_ts):
            ts = _ts(ev)
            report_lines.append(f"  [IGNORE] {ev.get('event_name', '?')}" + (f" | {ts}" if ts else ""))
            report_lines.append(f"    {json.dumps(ev.get('attributes', {}), ensure_ascii=False)}")
        if not ignored_list:
            report_lines.append("  (無)")
        if not failed_list:
            report_lines.append("")
            report_lines.append("所有事件均符合 firebase_event_specs 規範。")

        report_text = "\n".join(report_lines) + "\n"
        for line in report_lines:
            print(line, file=sys.stderr)
        if args.output:
            out_path = Path(args.output)
            out_path.write_text(report_text, encoding="utf-8")
            print(f"驗證結果已寫入 {out_path}", file=sys.stderr)
        # 每次跑完另存一份帶 platform 與時間戳的檔案到 firebase_event_verify_result/
        verify_result_dir = Path(__file__).parent / "firebase_event_verify_result"
        verify_result_dir.mkdir(exist_ok=True)
        ts_name = f"verify_result_{plat}_{ts_file}.txt"
        ts_path = verify_result_dir / ts_name
        ts_path.write_text(report_text, encoding="utf-8")
        print(f"驗證結果已寫入（含時間戳） {ts_path}", file=sys.stderr)
        if failed_list:
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已中斷 (Ctrl+C)", file=sys.stderr)
        sys.exit(130)
