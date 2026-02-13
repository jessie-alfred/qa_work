#!/usr/bin/env python3
"""Parse [TEST Result] Firebase Events and Event Properties.xlsx and output one .md per sheet (event name)."""
import zipfile
import xml.etree.ElementTree as ET
import re
from pathlib import Path

NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

def col_ref_to_index(ref):
    """Convert cell ref like A1, B5, E12 to (col_index, row_index) 0-based."""
    m = re.match(r"^([A-Z]+)(\d+)$", ref)
    if not m:
        return None, None
    letters, row = m.group(1), int(m.group(2))
    col = 0
    for c in letters:
        col = col * 26 + (ord(c) - ord("A") + 1)
    return col - 1, row - 1

def parse_shared_strings(zipf):
    strings = []
    with zipf.open("xl/sharedStrings.xml") as f:
        tree = ET.parse(f)
    root = tree.getroot()
    for si in root.findall(".//main:si", NS):
        parts = []
        for t in si.findall(".//main:t", NS):
            if t.text:
                parts.append(t.text)
            if t.tail:
                parts.append(t.tail)
        s = "".join(parts).strip() if parts else ""
        strings.append(s)
    return strings

def parse_workbook_sheet_names(zipf):
    with zipf.open("xl/workbook.xml") as f:
        tree = ET.parse(f)
    root = tree.getroot()
    names = []
    for sheet in root.findall(".//main:sheet", NS):
        names.append(sheet.get("name", ""))
    return names

def parse_sheet(zipf, sheet_index, shared_strings):
    sheet_path = f"xl/worksheets/sheet{sheet_index + 1}.xml"
    with zipf.open(sheet_path) as f:
        tree = ET.parse(f)
    root = tree.getroot()
    grid = {}
    for row in root.findall(".//main:sheetData/main:row", NS):
        r = int(row.get("r", 0))
        for c in row.findall("main:c", NS):
            ref = c.get("r")
            col_idx, row_idx = col_ref_to_index(ref)
            if col_idx is None:
                continue
            val_elem = c.find("main:v", NS)
            if val_elem is not None and val_elem.text is not None:
                raw = val_elem.text.strip()
                if c.get("t") == "s":
                    try:
                        idx = int(raw)
                        val = shared_strings[idx] if idx < len(shared_strings) else raw
                    except ValueError:
                        val = raw
                else:
                    val = raw
            else:
                val = ""
            grid[(row_idx, col_idx)] = val
    return grid

def grid_to_rows(grid):
    if not grid:
        return []
    max_row = max(r for r, c in grid)
    max_col = max(c for r, c in grid)
    rows = []
    for r in range(max_row + 1):
        row = []
        for c in range(max_col + 1):
            row.append(grid.get((r, c), ""))
        rows.append(row)
    return rows

def rows_to_md(event_name, rows):
    """Convert parsed rows to markdown. Auto-detect Purpose row and table header row."""
    lines = [
        f"# 事件追蹤規範：{event_name}",
        "",
        "## 事件名稱 (Event Name)",
        "",
        f"`{event_name}`",
        "",
        "## 目的 (Purpose)",
        "",
    ]
    purpose = ""
    for row in rows[:10]:
        row_strs = [str(c).strip() for c in row]
        if "Purpose" in row_strs:
            idx = row_strs.index("Purpose")
            for v in row_strs[idx + 1 : idx + 4]:
                if v and v != "Purpose":
                    purpose = v
                    break
            break
    if not purpose and len(rows) > 1 and len(rows[1]) > 1:
        purpose = (rows[1][1] or "").strip() or ((rows[1][2] or "").strip() if len(rows[1]) > 2 else "")
    lines.append(purpose or "(未填)")
    lines.append("")
    lines.append("## 事件屬性 (Event Properties)")
    lines.append("")

    header_row_idx = None
    for i, row in enumerate(rows):
        row_strs = [str(c).strip().lower() for c in row]
        if "event property" in row_strs or "requirement" in row_strs or "data type" in row_strs:
            header_row_idx = i
            break
    if header_row_idx is None:
        header_row_idx = 3 if len(rows) > 4 else 0
    data_start = header_row_idx + 1
    if data_start >= len(rows):
        lines.append("(無屬性表格)")
        return "\n".join(lines)

    header_row = rows[header_row_idx]
    data_rows = rows[data_start:]
    headers = [str(h).strip() or f"Column{i}" for i, h in enumerate(header_row)]
    col_count = max(len(header_row), max((len(r) for r in data_rows), default=0))

    table_lines = ["| " + " | ".join(h for h in headers[:col_count]) + " |", "| " + " | ".join("---" for _ in headers[:col_count]) + " |"]
    for r in data_rows:
        cells = [str(r[i]) if i < len(r) else "" for i in range(col_count)]
        if any(cells):
            table_lines.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cells) + " |")
    lines.extend(table_lines)
    return "\n".join(lines)

def safe_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()

def main():
    import sys
    base = Path(__file__).parent
    if len(sys.argv) > 1:
        xlsx_path = Path(sys.argv[1])
        if not xlsx_path.is_absolute():
            xlsx_path = base / xlsx_path
    else:
        xlsx_path = base / "[TEST Result] Firebase Events and Event Properties.xlsx"
    out_dir = base / "firebase_event_specs"
    out_dir.mkdir(exist_ok=True)
    skip_existing = "--skip-existing" in sys.argv or "-s" in sys.argv

    if not xlsx_path.exists():
        print(f"錯誤：找不到檔案 {xlsx_path}", file=sys.stderr)
        sys.exit(1)

    with zipfile.ZipFile(xlsx_path, "r") as z:
        shared = parse_shared_strings(z)
        sheet_names = parse_workbook_sheet_names(z)
        for i, event_name in enumerate(sheet_names):
            filename = safe_filename(event_name) + "_event_spec.md"
            out_path = out_dir / filename
            if skip_existing and out_path.exists():
                print(f"(略過，已存在) {out_path}")
                continue
            grid = parse_sheet(z, i, shared)
            rows = grid_to_rows(grid)
            md_content = rows_to_md(event_name, rows)
            out_path.write_text(md_content, encoding="utf-8")
            print(out_path)

if __name__ == "__main__":
    main()
