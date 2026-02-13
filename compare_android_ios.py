#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比對 Android.xml 和 iOS.strings 檔案
忽略格式化參數 %s, %d, %@ 等的差異，其他字元要完全符合
"""

import re
import xml.etree.ElementTree as ET
from collections import defaultdict

def normalize_value(value):
    """標準化 value，移除所有格式化參數"""
    if not value:
        return ""
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

def parse_android_xml(file_path):
    """解析 Android.xml，返回 {normalized_value: [(name, value)]} 的字典"""
    value_map = defaultdict(list)
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    for string_elem in root.findall('.//string'):
        name = string_elem.get('name')
        value = string_elem.text if string_elem.text else ''
        value = value.strip()
        if name and value:
            normalized = normalize_value(value)
            value_map[normalized].append((name, value))
    
    return value_map

def parse_ios_strings(file_path):
    """解析 iOS.strings，返回 {normalized_value: [(name, value)]} 的字典"""
    value_map = defaultdict(list)
    
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
            value_map[normalized].append((name, value))
    
    return value_map

def compare_files(android_file, ios_file):
    """比對兩個檔案並顯示差異"""
    print("解析 Android.xml...")
    android_map = parse_android_xml(android_file)
    print(f"Android.xml: {len(android_map)} 個唯一的 normalized value")
    
    print("解析 iOS.strings...")
    ios_map = parse_ios_strings(ios_file)
    print(f"iOS.strings: {len(ios_map)} 個唯一的 normalized value\n")
    
    # 找出匹配的項目（normalized value 相同）
    matched = []
    android_only = []
    ios_only = []
    
    for normalized, android_entries in android_map.items():
        if normalized in ios_map:
            ios_entries = ios_map[normalized]
            # 比對每個 Android entry 和 iOS entry
            for android_name, android_value in android_entries:
                for ios_name, ios_value in ios_entries:
                    matched.append((android_name, ios_name, android_value, ios_value, normalized))
        else:
            android_only.append((normalized, android_entries))
    
    for normalized, ios_entries in ios_map.items():
        if normalized not in android_map:
            ios_only.append((normalized, ios_entries))
    
    # 找出格式化參數不同的範例
    format_diff_examples = []
    for android_name, ios_name, android_value, ios_value, normalized in matched:
        # 檢查原始 value 是否不同（但 normalized 相同）
        if android_value != ios_value:
            # 檢查是否只是格式化參數不同
            android_formats = set(re.findall(r'%[0-9]*\.?[0-9]*[sd@fhm]', android_value))
            ios_formats = set(re.findall(r'%[0-9]*\.?[0-9]*[sd@fhm]', ios_value))
            if android_formats != ios_formats:
                format_diff_examples.append((android_name, ios_name, android_value, ios_value, normalized))
    
    # 輸出結果
    print("=" * 80)
    print("比對結果摘要（忽略格式化參數 %s, %d, %@ 等）")
    print("=" * 80)
    print(f"匹配的項目（normalized value 相同）: {len(matched)}")
    print(f"僅在 Android 中的項目: {len(android_only)}")
    print(f"僅在 iOS 中的項目: {len(ios_only)}")
    print(f"格式化參數不同的範例: {len(format_diff_examples)}")
    print()
    
    if format_diff_examples:
        print("=" * 80)
        print("格式化參數不同的範例（normalized value 相同，但格式化參數不同）:")
        print("=" * 80)
        for i, (android_name, ios_name, android_value, ios_value, normalized) in enumerate(format_diff_examples[:20], 1):
            android_preview = android_value[:70] + "..." if len(android_value) > 70 else android_value
            ios_preview = ios_value[:70] + "..." if len(ios_value) > 70 else ios_value
            normalized_preview = normalized[:70] + "..." if len(normalized) > 70 else normalized
            print(f"{i}. Android: '{android_name}'")
            print(f"   iOS: '{ios_name}'")
            print(f"   Android Value: {android_preview}")
            print(f"   iOS Value: {ios_preview}")
            print(f"   Normalized: {normalized_preview}")
            print()
        if len(format_diff_examples) > 20:
            print(f"... 還有 {len(format_diff_examples) - 20} 個範例未顯示")
        print()
    
    # 檢查用戶給的範例
    print("=" * 80)
    print("檢查用戶範例:")
    print("=" * 80)
    example_android = "To activate this feature, please allow Notifications for Alfred in your system setting on %s."
    example_ios = "To activate this feature, please allow Notifications for Alfred in your system setting on %@."
    
    norm_android = normalize_value(example_android)
    norm_ios = normalize_value(example_ios)
    
    print(f"Android 範例: {example_android}")
    print(f"iOS 範例: {example_ios}")
    print(f"Android Normalized: {norm_android}")
    print(f"iOS Normalized: {norm_ios}")
    print(f"是否匹配: {norm_android == norm_ios}")
    print()
    
    # 生成詳細報告
    report_file = 'jessie_test_project/android_ios_comparison_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Android.xml 與 iOS.strings 比對報告（忽略格式化參數）\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"匹配的項目總數: {len(matched)}\n")
        f.write(f"僅在 Android 中的項目: {len(android_only)}\n")
        f.write(f"僅在 iOS 中的項目: {len(ios_only)}\n")
        f.write(f"格式化參數不同的範例: {len(format_diff_examples)}\n\n")
        
        if format_diff_examples:
            f.write("\n" + "=" * 80 + "\n")
            f.write("格式化參數不同的範例（完整列表）:\n")
            f.write("=" * 80 + "\n")
            for android_name, ios_name, android_value, ios_value, normalized in format_diff_examples:
                f.write(f"Android: '{android_name}'\n")
                f.write(f"iOS: '{ios_name}'\n")
                f.write(f"Android Value: {android_value}\n")
                f.write(f"iOS Value: {ios_value}\n")
                f.write(f"Normalized: {normalized}\n\n")
    
    print(f"詳細報告已儲存至: {report_file}")
    
    return {
        'matched': len(matched),
        'android_only': len(android_only),
        'ios_only': len(ios_only),
        'format_diffs': len(format_diff_examples)
    }

if __name__ == '__main__':
    android_file = 'jessie_test_project/Android.xml'
    ios_file = 'jessie_test_project/iOS.strings'
    
    compare_files(android_file, ios_file)

