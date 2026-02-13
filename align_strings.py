#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
對齊 iOS.strings 和 Android.xml 的 string name
以 Android.xml 為基準，將 iOS.strings 中 value 相同的 entry 的 name 改成與 Android 一致
"""

import re
import xml.etree.ElementTree as ET
from collections import defaultdict


def parse_android_xml(file_path):
    """解析 Android.xml，建立 value -> [name1, name2, ...] 的映射"""
    value_to_names = defaultdict(list)

    tree = ET.parse(file_path)
    root = tree.getroot()

    for string_elem in root.findall('.//string'):
        name = string_elem.get('name')
        value = string_elem.text if string_elem.text else ''
        # 移除前後空白
        value = value.strip()
        if name and value:
            value_to_names[value].append(name)

    return value_to_names


def parse_ios_strings(file_path):
    """解析 iOS.strings，返回 (line_number, original_name, value, full_line) 的列表"""
    entries = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 匹配 iOS.strings 格式: "name" = "value";
    pattern = r'"([^"]+)"\s*=\s*"([^"]+)";'

    for line_num, line in enumerate(lines, 1):
        match = re.match(pattern, line.strip())
        if match:
            name = match.group(1)
            value = match.group(2)
            entries.append((line_num, name, value, line))

    return entries, lines


def align_strings(android_file, ios_file):
    """對齊兩個文件的 string name"""
    # 1. 解析 Android.xml
    print("解析 Android.xml...")
    value_to_android_names = parse_android_xml(android_file)
    print(f"找到 {len(value_to_android_names)} 個唯一的 value")

    # 2. 解析 iOS.strings
    print("解析 iOS.strings...")
    ios_entries, ios_lines = parse_ios_strings(ios_file)
    print(f"找到 {len(ios_entries)} 個 iOS string entries")

    # 3. 建立 iOS value -> Android name 的映射
    # 如果有多個 Android name 對應同一個 value，選擇第一個
    value_to_android_name = {}
    for value, names in value_to_android_names.items():
        # 選擇第一個 name（如果有多個）
        value_to_android_name[value] = names[0]
        if len(names) > 1:
            print(f"警告: value '{value[:50]}...' 在 Android 中有 {len(names)} 個 name，使用 '{names[0]}'")

    # 4. 建立新的 iOS.strings 內容
    new_lines = ios_lines.copy()
    updated_count = 0
    name_conflicts = defaultdict(list)  # 追蹤新的 name 是否會造成衝突

    # 先收集所有要更新的映射
    updates = []
    for line_num, ios_name, ios_value, original_line in ios_entries:
        if ios_value in value_to_android_name:
            android_name = value_to_android_name[ios_value]
            if android_name != ios_name:
                updates.append((line_num, ios_name, android_name, ios_value, original_line))
                name_conflicts[android_name].append((line_num, ios_value))

    # 檢查是否有 name 衝突（同一個 Android name 對應多個不同的 iOS value）
    conflicts = {name: values for name, values in name_conflicts.items() if len(values) > 1}
    if conflicts:
        print(f"\n發現 {len(conflicts)} 個 name 衝突（同一個 Android name 對應多個不同的 value）:")
        for name, values in conflicts.items():
            print(f"  '{name}': {len(values)} 個不同的 value")
            # 對於衝突的情況，只更新第一個，其他保持原樣
            for line_num, value in values[1:]:
                updates = [u for u in updates if not (u[0] == line_num and u[2] == name)]
                print(f"    跳過 line {line_num}: value='{value[:50]}...'")

    # 5. 執行更新
    for line_num, old_name, new_name, value, original_line in updates:
        # 替換 name，保持格式
        new_line = original_line.replace(f'"{old_name}"', f'"{new_name}"', 1)
        new_lines[line_num - 1] = new_line
        updated_count += 1

    # 6. 寫回文件
    if updated_count > 0:
        with open(ios_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"\n完成！更新了 {updated_count} 個 string name")
    else:
        print("\n沒有需要更新的項目")

    return updated_count


if __name__ == '__main__':
    android_file = 'jessie_test_project/Android.xml'
    ios_file = 'jessie_test_project/iOS.strings'

    align_strings(android_file, ios_file)
