#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標記 iOS.strings 中需要修改的 string name
1. 第一個字母是大寫的
2. 有空白的
在這些項目的 name 前面加上 "!" 前綴
"""

import re

def should_mark(name):
    """判斷是否需要標記（第一個字母是大寫或包含空白）"""
    if not name:
        return False
    # 檢查第一個字母是否是大寫
    first_char_upper = name[0].isupper()
    # 檢查是否包含空白
    has_space = ' ' in name
    return first_char_upper or has_space

def process_ios_strings(file_path):
    """處理 iOS.strings 檔案，標記需要修改的項目"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 匹配 iOS.strings 格式: "name" = "value";
    pattern = r'"([^"]+)"\s*=\s*"([^"]+)";'
    
    new_lines = []
    marked_count = 0
    marked_items = []
    
    for line_num, line in enumerate(lines, 1):
        match = re.match(pattern, line.strip())
        if match:
            name = match.group(1)
            value = match.group(2)
            
            if should_mark(name):
                # 在 name 前面加上 "!"
                new_line = line.replace(f'"{name}"', f'!"{name}"', 1)
                new_lines.append(new_line)
                marked_count += 1
                marked_items.append((line_num, name, value))
            else:
                new_lines.append(line)
        else:
            # 不是 string entry，保持原樣
            new_lines.append(line)
    
    # 寫回檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"完成！標記了 {marked_count} 個項目")
    print("\n標記的項目（前 30 個）:")
    for i, (line_num, name, value) in enumerate(marked_items[:30], 1):
        value_preview = value[:50] + "..." if len(value) > 50 else value
        print(f"{i}. Line {line_num}: '{name}' = '{value_preview}'")
    
    if len(marked_items) > 30:
        print(f"\n... 還有 {len(marked_items) - 30} 個項目未顯示")
    
    return marked_count

if __name__ == '__main__':
    ios_file = 'jessie_test_project/iOS.strings'
    process_ios_strings(ios_file)

