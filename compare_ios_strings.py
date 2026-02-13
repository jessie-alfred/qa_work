#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比對兩個 iOS.strings 檔案的差異
找出哪些 string name 被更改了
"""

import re
from collections import defaultdict

def parse_ios_strings(file_path):
    """解析 iOS.strings，返回 {name: (value, line_num)} 的字典"""
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
            entries[name] = (value, line_num)
    
    return entries

def compare_files(original_file, updated_file):
    """比對兩個檔案並顯示差異"""
    print("解析原始檔案...")
    original = parse_ios_strings(original_file)
    print(f"原始檔案: {len(original)} 個 entries")
    
    print("解析更新後檔案...")
    updated = parse_ios_strings(updated_file)
    print(f"更新後檔案: {len(updated)} 個 entries\n")
    
    # 找出所有更改的項目
    changed_names = []
    new_names = []
    removed_names = []
    unchanged = []
    
    # 檢查所有原始項目
    for name, (value, line_num) in original.items():
        if name in updated:
            updated_value, updated_line = updated[name]
            if value != updated_value:
                changed_names.append((name, value, updated_value, line_num, updated_line))
            elif name != updated.get(name, (None, None))[0]:
                # name 相同但可能位置不同
                unchanged.append(name)
        else:
            removed_names.append((name, value, line_num))
    
    # 找出新增的項目
    for name in updated:
        if name not in original:
            new_names.append((name, updated[name][0], updated[name][1]))
    
    # 找出 name 被更改的項目（value 相同但 name 不同）
    name_changes = []
    value_to_original_name = {}
    value_to_updated_name = {}
    
    for name, (value, _) in original.items():
        if value not in value_to_original_name:
            value_to_original_name[value] = name
    
    for name, (value, _) in updated.items():
        if value not in value_to_updated_name:
            value_to_updated_name[value] = name
    
    # 找出 value 相同但 name 不同的項目
    for value, original_name in value_to_original_name.items():
        if value in value_to_updated_name:
            updated_name = value_to_updated_name[value]
            if original_name != updated_name:
                # 檢查是否原始 name 還在 updated 中
                if original_name not in updated:
                    name_changes.append((original_name, updated_name, value))
    
    # 輸出結果
    print("=" * 80)
    print("比對結果摘要")
    print("=" * 80)
    print(f"Name 被更改的項目: {len(name_changes)}")
    print(f"Value 被更改的項目: {len(changed_names)}")
    print(f"新增的項目: {len(new_names)}")
    print(f"移除的項目: {len(removed_names)}")
    print(f"未變更的項目: {len(unchanged)}")
    print()
    
    if name_changes:
        print("=" * 80)
        print("Name 被更改的項目 (value 相同，但 name 從原始改為 Android 的 name):")
        print("=" * 80)
        for i, (old_name, new_name, value) in enumerate(name_changes[:50], 1):  # 只顯示前50個
            value_preview = value[:60] + "..." if len(value) > 60 else value
            print(f"{i}. '{old_name}' → '{new_name}'")
            print(f"   Value: {value_preview}")
        if len(name_changes) > 50:
            print(f"\n... 還有 {len(name_changes) - 50} 個項目未顯示")
        print()
    
    if changed_names:
        print("=" * 80)
        print("Value 被更改的項目:")
        print("=" * 80)
        for i, (name, old_value, new_value, old_line, new_line) in enumerate(changed_names[:20], 1):
            old_preview = old_value[:50] + "..." if len(old_value) > 50 else old_value
            new_preview = new_value[:50] + "..." if len(new_value) > 50 else new_value
            print(f"{i}. '{name}' (line {old_line} → {new_line})")
            print(f"   舊: {old_preview}")
            print(f"   新: {new_preview}")
        if len(changed_names) > 20:
            print(f"\n... 還有 {len(changed_names) - 20} 個項目未顯示")
        print()
    
    if new_names:
        print("=" * 80)
        print("新增的項目:")
        print("=" * 80)
        for i, (name, value, line_num) in enumerate(new_names[:20], 1):
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
        for i, (name, value, line_num) in enumerate(removed_names[:20], 1):
            value_preview = value[:60] + "..." if len(value) > 60 else value
            print(f"{i}. '{name}' (line {line_num})")
            print(f"   Value: {value_preview}")
        if len(removed_names) > 20:
            print(f"\n... 還有 {len(removed_names) - 20} 個項目未顯示")
        print()
    
    # 生成詳細報告
    report_file = 'jessie_test_project/ios_strings_diff_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("iOS.strings 比對報告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Name 被更改的項目總數: {len(name_changes)}\n")
        f.write(f"Value 被更改的項目總數: {len(changed_names)}\n")
        f.write(f"新增的項目總數: {len(new_names)}\n")
        f.write(f"移除的項目總數: {len(removed_names)}\n\n")
        
        if name_changes:
            f.write("\n" + "=" * 80 + "\n")
            f.write("Name 被更改的項目 (完整列表):\n")
            f.write("=" * 80 + "\n")
            for old_name, new_name, value in name_changes:
                f.write(f"'{old_name}' → '{new_name}'\n")
                f.write(f"  Value: {value}\n\n")
    
    print(f"\n詳細報告已儲存至: {report_file}")
    
    return {
        'name_changes': len(name_changes),
        'value_changes': len(changed_names),
        'new': len(new_names),
        'removed': len(removed_names)
    }

if __name__ == '__main__':
    original_file = 'jessie_test_project/iOS-original.strings'
    updated_file = 'jessie_test_project/iOS.strings'
    
    compare_files(original_file, updated_file)

