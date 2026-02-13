#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比對兩個 iOS.strings 檔案的差異
忽略 string value 中的格式化參數（%s, %d, %@ 等），其他字元要完全符合
"""

import re
from collections import defaultdict


def normalize_value(value):
    """標準化 value，移除所有格式化參數"""
    # 先處理 %% (轉義的百分號)，將其替換為一個特殊標記，稍後再恢復
    normalized = value.replace('%%', '__PERCENT__')

    # 移除所有格式化參數：
    # %s, %d, %@ 等基本格式
    # %02d, %02dh, %02dm, %02ds, %02d min, %02d sec 等帶數字的格式
    # %d days, %d day(s), %d hour(s), %d minute(s) 等
    # 匹配 % 後面跟著可選的數字、可選的點號、可選的數字、然後是類型字符
    # 類型字符包括: s, d, @, f, h, m, 等
    normalized = re.sub(r'%[0-9]*\.?[0-9]*[sd@fhm]', '', normalized)

    # 恢復轉義的百分號
    normalized = normalized.replace('__PERCENT__', '%%')

    return normalized.strip()


def parse_ios_strings(file_path):
    """解析 iOS.strings，返回 {name: (value, normalized_value, line_num)} 的字典"""
    entries = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 匹配 iOS.strings 格式: "name" = "value";
    pattern = r'"([^"]+)"\s*=\s*"([^"]+)";'

    for line_num, line in enumerate(lines, 1):
        match = re.match(pattern, line.strip())
        if match:
            name = match.group(1)
            value = match.group(2)
            normalized = normalize_value(value)
            entries[name] = (value, normalized, line_num)

    return entries


def compare_files(original_file, updated_file):
    """比對兩個檔案並顯示差異"""
    print("解析原始檔案...")
    original = parse_ios_strings(original_file)
    print(f"原始檔案: {len(original)} 個 entries")

    print("解析更新後檔案...")
    updated = parse_ios_strings(updated_file)
    print(f"更新後檔案: {len(updated)} 個 entries\n")

    # 建立 normalized value 到 name 的映射
    original_normalized_map = defaultdict(list)  # normalized_value -> [(name, value, line_num)]
    updated_normalized_map = defaultdict(list)

    for name, (value, normalized, line_num) in original.items():
        original_normalized_map[normalized].append((name, value, line_num))

    for name, (value, normalized, line_num) in updated.items():
        updated_normalized_map[normalized].append((name, value, line_num))

    # 找出 name 被更改的項目（normalized value 相同但 name 不同）
    name_changes = []
    matched_normalized = set()

    for normalized, original_entries in original_normalized_map.items():
        if normalized in updated_normalized_map:
            updated_entries = updated_normalized_map[normalized]
            # 比對每個原始 entry 和更新後的 entry
            for orig_name, orig_value, orig_line in original_entries:
                # 找出對應的更新後 entry（normalized 相同）
                for upd_name, upd_value, upd_line in updated_entries:
                    if orig_name != upd_name:
                        # 檢查原始 name 是否還在 updated 中
                        if orig_name not in updated:
                            name_changes.append((orig_name, upd_name, orig_value, upd_value, normalized))
                            matched_normalized.add(normalized)
                            break

    # 找出 value 被更改的項目（name 相同但 normalized value 不同）
    changed_values = []
    for name in set(original.keys()) & set(updated.keys()):
        orig_value, orig_normalized, orig_line = original[name]
        upd_value, upd_normalized, upd_line = updated[name]
        if orig_normalized != upd_normalized:
            changed_values.append((name, orig_value, upd_value, orig_normalized, upd_normalized, orig_line, upd_line))

    # 找出新增的項目
    new_names = []
    for name in set(updated.keys()) - set(original.keys()):
        value, normalized, line_num = updated[name]
        new_names.append((name, value, normalized, line_num))

    # 找出移除的項目
    removed_names = []
    for name in set(original.keys()) - set(updated.keys()):
        value, normalized, line_num = original[name]
        removed_names.append((name, value, normalized, line_num))

    # 找出未變更的項目（name 和 normalized value 都相同）
    unchanged = []
    for name in set(original.keys()) & set(updated.keys()):
        orig_value, orig_normalized, orig_line = original[name]
        upd_value, upd_normalized, upd_line = updated[name]
        if orig_normalized == upd_normalized and name == name:  # name 相同且 normalized 相同
            unchanged.append(name)

    # 輸出結果
    print("=" * 80)
    print("比對結果摘要（忽略格式化參數 %s, %d, %@ 等）")
    print("=" * 80)
    print(f"Name 被更改的項目: {len(name_changes)}")
    print(f"Value 被更改的項目（normalized 不同）: {len(changed_values)}")
    print(f"新增的項目: {len(new_names)}")
    print(f"移除的項目: {len(removed_names)}")
    print(f"未變更的項目: {len(unchanged)}")
    print()

    if name_changes:
        print("=" * 80)
        print("Name 被更改的項目 (normalized value 相同，但 name 從原始改為 Android 的 name):")
        print("=" * 80)
        for i, (old_name, new_name, old_value, new_value, normalized) in enumerate(name_changes[:50], 1):
            old_preview = old_value[:60] + "..." if len(old_value) > 60 else old_value
            new_preview = new_value[:60] + "..." if len(new_value) > 60 else new_value
            normalized_preview = normalized[:60] + "..." if len(normalized) > 60 else normalized
            print(f"{i}. '{old_name}' → '{new_name}'")
            print(f"   原始 Value: {old_preview}")
            print(f"   更新 Value: {new_preview}")
            print(f"   Normalized: {normalized_preview}")
        if len(name_changes) > 50:
            print(f"\n... 還有 {len(name_changes) - 50} 個項目未顯示")
        print()

    if changed_values:
        print("=" * 80)
        print("Value 被更改的項目（normalized 不同）:")
        print("=" * 80)
        for i, (name, old_value, new_value, old_norm, new_norm, old_line, new_line) in enumerate(changed_values[:20], 1):
            old_preview = old_value[:50] + "..." if len(old_value) > 50 else old_value
            new_preview = new_value[:50] + "..." if len(new_value) > 50 else new_value
            print(f"{i}. '{name}' (line {old_line} → {new_line})")
            print(f"   原始: {old_preview}")
            print(f"   更新: {new_preview}")
            print(f"   原始 Normalized: {old_norm[:50]}")
            print(f"   更新 Normalized: {new_norm[:50]}")
        if len(changed_values) > 20:
            print(f"\n... 還有 {len(changed_values) - 20} 個項目未顯示")
        print()

    if new_names:
        print("=" * 80)
        print("新增的項目:")
        print("=" * 80)
        for i, (name, value, normalized, line_num) in enumerate(new_names[:20], 1):
            value_preview = value[:60] + "..." if len(value) > 60 else value
            print(f"{i}. '{name}' (line {line_num})")
            print(f"   Value: {value_preview}")
        if len(new_names) > 20:
            print(f"\n... 還有 {len(new_names) - 20} 個項目未顯示")
        print()

    if removed_names:
        print("=" * 80)
        print("移除的項目:")
        print("=" * 80)
        for i, (name, value, normalized, line_num) in enumerate(removed_names[:20], 1):
            value_preview = value[:60] + "..." if len(value) > 60 else value
            print(f"{i}. '{name}' (line {line_num})")
            print(f"   Value: {value_preview}")
        if len(removed_names) > 20:
            print(f"\n... 還有 {len(removed_names) - 20} 個項目未顯示")
        print()

    # 生成詳細報告
    report_file = 'jessie_test_project/ios_strings_diff_report_normalized.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("iOS.strings 比對報告（忽略格式化參數）\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Name 被更改的項目總數: {len(name_changes)}\n")
        f.write(f"Value 被更改的項目總數（normalized 不同）: {len(changed_values)}\n")
        f.write(f"新增的項目總數: {len(new_names)}\n")
        f.write(f"移除的項目總數: {len(removed_names)}\n\n")

        if name_changes:
            f.write("\n" + "=" * 80 + "\n")
            f.write("Name 被更改的項目 (完整列表):\n")
            f.write("=" * 80 + "\n")
            for old_name, new_name, old_value, new_value, normalized in name_changes:
                f.write(f"'{old_name}' → '{new_name}'\n")
                f.write(f"  原始 Value: {old_value}\n")
                f.write(f"  更新 Value: {new_value}\n")
                f.write(f"  Normalized: {normalized}\n\n")

        if changed_values:
            f.write("\n" + "=" * 80 + "\n")
            f.write("Value 被更改的項目（完整列表）:\n")
            f.write("=" * 80 + "\n")
            for name, old_value, new_value, old_norm, new_norm, old_line, new_line in changed_values:
                f.write(f"'{name}' (line {old_line} → {new_line})\n")
                f.write(f"  原始: {old_value}\n")
                f.write(f"  更新: {new_value}\n")
                f.write(f"  原始 Normalized: {old_norm}\n")
                f.write(f"  更新 Normalized: {new_norm}\n\n")

    print(f"\n詳細報告已儲存至: {report_file}")

    return {
        'name_changes': len(name_changes),
        'value_changes': len(changed_values),
        'new': len(new_names),
        'removed': len(removed_names)
    }


if __name__ == '__main__':
    original_file = 'jessie_test_project/iOS-original.strings'
    updated_file = 'jessie_test_project/iOS.strings'

    compare_files(original_file, updated_file)
