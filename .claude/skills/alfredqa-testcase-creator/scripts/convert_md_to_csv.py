#!/usr/bin/env python3
"""
將測試案例 Markdown 文件轉換為 CSV

使用方式：
    python convert_md_to_csv.py \
        --md-file "test_case/CAMERA-6225_Firebase_Core_Events_TestCase.md"
"""

import argparse
import csv
import os
import re
import sys
from typing import Dict, List


def parse_markdown_test_cases(md_file_path: str) -> List[Dict[str, str]]:
    """
    解析 Markdown 文件中的測試案例

    Args:
        md_file_path: Markdown 文件路徑

    Returns:
        測試案例列表，每個案例是一個字典
    """
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    test_cases = []
    current_section = ""

    # 使用正則表達式匹配測試案例
    # 匹配格式：### 1.1 測試標題 或 #### 1.15.1 測試標題
    test_case_pattern = r'^#{3,4}\s+(\d+\.\d+(?:\.\d+)?)\s+(.+?)$'
    # 匹配測試目標
    test_objective_pattern = r'\*\*測試目標\*\*[：:]\s*(.+?)(?=\n\n|\*\*|$)'
    # 匹配前置條件
    preconditions_pattern = r'\*\*前置條件\*\*[：:]\s*(.+?)(?=\n\n\*\*測試步驟\*\*|\n\n\*\*預期結果\*\*|$)'
    # 匹配測試步驟
    test_steps_pattern = r'\*\*測試步驟\*\*[：:]\s*(.+?)(?=\n\n\*\*預期結果\*\*|$)'
    # 匹配預期結果
    expected_results_pattern = r'\*\*預期結果\*\*[：:]\s*(.+?)(?=\n\n---|\n\n##|$)'

    # 找到所有測試案例標題
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 檢查是否是章節標題（## 開頭）
        if line.startswith('## '):
            section_match = re.match(r'^##\s+\d+\.\s+(.+?)$', line)
            if section_match:
                current_section = section_match.group(1)

        # 檢查是否是測試案例標題（### 開頭）
        test_case_match = re.match(test_case_pattern, line)
        if test_case_match:
            test_id = test_case_match.group(1)
            test_title = test_case_match.group(2)

            # 從當前位置開始查找測試目標、前置條件、測試步驟、預期結果
            remaining_content = '\n'.join(lines[i:])

            # 提取測試目標
            objective_match = re.search(test_objective_pattern, remaining_content, re.DOTALL)
            test_objective = objective_match.group(1).strip() if objective_match else ""

            # 提取前置條件
            preconditions_match = re.search(preconditions_pattern, remaining_content, re.DOTALL)
            preconditions = preconditions_match.group(1).strip() if preconditions_match else ""

            # 提取測試步驟
            test_steps_match = re.search(test_steps_pattern, remaining_content, re.DOTALL)
            test_steps = test_steps_match.group(1).strip() if test_steps_match else ""

            # 提取預期結果
            results_match = re.search(expected_results_pattern, remaining_content, re.DOTALL)
            expected_results = results_match.group(1).strip() if results_match else ""

            # 清理格式（移除 Markdown 格式）
            test_objective = clean_markdown(test_objective)
            preconditions = clean_markdown(preconditions)
            test_steps = clean_markdown(test_steps)
            expected_results = clean_markdown(expected_results)

            # 確定測試分類
            test_category = determine_category(test_id, test_title, current_section)

            # 確定優先級
            priority = determine_priority(test_id, test_title)

            test_cases.append({
                'test_id': test_id,
                'category': test_category,
                'title': test_title,
                'objective': test_objective,
                'preconditions': preconditions,
                'test_steps': test_steps,
                'expected_results': expected_results,
                'priority': priority,
                'status': '待測試',
                'notes': ''
            })

        i += 1

    return test_cases


def clean_markdown(text: str) -> str:
    """
    清理 Markdown 格式，轉換為純文字

    Args:
        text: Markdown 文字

    Returns:
        清理後的純文字
    """
    if not text:
        return ""

    # 移除列表標記
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)
    # 移除數字列表標記
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    # 移除粗體標記
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # 移除代碼標記
    text = re.sub(r'`(.+?)`', r'\1', text)
    # 移除連結標記，保留文字
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # 移除多餘的空白行
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 移除行首尾空白
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def determine_category(test_id: str, test_title: str, current_section: str) -> str:
    """
    根據測試 ID、標題和章節確定測試分類

    Args:
        test_id: 測試案例編號
        test_title: 測試標題
        current_section: 當前章節名稱

    Returns:
        測試分類
    """
    # 根據測試標題中的關鍵字判斷特殊分類
    title_lower = test_title.lower()
    
    # Data Type 驗證相關測試
    if any(keyword in title_lower for keyword in ['data type', '資料型別', '資料類型', '型別驗證', '類型驗證']):
        if test_id.startswith('1.'):
            return '功能與業務邏輯測試 (Data Type 驗證)'
    
    # 根據測試 ID 開頭數字判斷基本分類
    if test_id.startswith('1.'):
        return '功能與業務邏輯測試'
    elif test_id.startswith('2.'):
        return '穩定性與可靠性測試'
    elif test_id.startswith('3.'):
        return '使用者體驗測試'
    elif test_id.startswith('4.'):
        return '效能測試'
    elif test_id.startswith('5.'):
        return '迴歸測試'
    elif test_id.startswith('6.'):
        return 'API 整合測試'
    elif test_id.startswith('7.'):
        return '邊緣案例測試'
    elif test_id.startswith('8.'):
        return '裝置相容性測試'
    elif test_id.startswith('9.'):
        return '整合測試'
    else:
        return current_section or '其他'


def determine_priority(test_id: str, test_title: str) -> str:
    """
    根據測試標題從 Markdown 文件中提取優先級

    Args:
        test_id: 測試案例編號
        test_title: 測試標題（應包含優先級標記，如：⭐ P0 或 ⭐ P1）

    Returns:
        優先級 (P0, P1, P2)，如果未找到則返回 P1（預設值）
    """
    # 從標題中提取優先級（標題格式：測試標題 ⭐ P0 或 ⭐ P1）
    priority_match = re.search(r'⭐\s*(P[0-2])', test_title)
    if priority_match:
        return priority_match.group(1)
    
    # 如果標題中沒有優先級標記，使用預設值 P1
    return 'P1'


def convert_to_csv(test_cases: List[Dict[str, str]], csv_file_path: str):
    """
    將測試案例轉換為 CSV 文件

    Args:
        test_cases: 測試案例列表
        csv_file_path: CSV 文件輸出路徑
    """
    headers = ['測試案例編號', '測試分類', '測試標題', '測試目標', '前置條件', '測試步驟', '預期結果', '優先級', '狀態', '備註']

    with open(csv_file_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for case in test_cases:
            writer.writerow([
                case['test_id'],
                case['category'],
                case['title'],
                case['objective'],
                case['preconditions'],
                case['test_steps'],
                case['expected_results'],
                case['priority'],
                case['status'],
                case['notes']
            ])


def main():
    parser = argparse.ArgumentParser(
        description="將測試案例 Markdown 文件轉換為 CSV"
    )
    parser.add_argument(
        "--md-file",
        required=True,
        help="Markdown 文件路徑"
    )
    parser.add_argument(
        "--output",
        help="CSV 文件輸出路徑（如果未提供，使用 Markdown 檔名，副檔名改為 .csv）"
    )

    args = parser.parse_args()

    # 檢查 Markdown 文件是否存在
    if not os.path.exists(args.md_file):
        print(f"❌ 錯誤：Markdown 文件不存在：{args.md_file}")
        sys.exit(1)

    # 解析 Markdown 文件
    print(f"📖 讀取 Markdown 文件：{args.md_file}")
    try:
        test_cases = parse_markdown_test_cases(args.md_file)
        print(f"✅ 解析完成，共找到 {len(test_cases)} 個測試案例")
    except Exception as e:
        print(f"❌ 解析 Markdown 文件失敗：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 決定 CSV 文件輸出路徑
    if args.output:
        csv_file_path = args.output
    else:
        csv_file_path = args.md_file.replace('.md', '.csv')

    # 生成 CSV 文件
    print(f"📝 生成 CSV 文件：{csv_file_path}")
    try:
        convert_to_csv(test_cases, csv_file_path)
        print(f"✅ CSV 文件已成功生成：{csv_file_path}")
    except Exception as e:
        print(f"❌ 生成 CSV 文件失敗：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
