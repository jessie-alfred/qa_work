#!/usr/bin/env python3
"""
將測試案例 CSV 上傳到 Google Sheets 並儲存到 Google Drive

使用方式：
    python upload_to_google_sheets.py \
        --csv-file "test_case/CAMERA-6225_Firebase_Core_Events_TestCase.csv"
        # --title "CAMERA-6225_test_case"  # 可選，預設為 CAMERA-xxxx_test_case
        # --folder-id "your-folder-id"  # 可選，預設使用固定資料夾

前置需求：
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def read_csv_file(csv_file_path: str) -> list[list[str]]:
    """
    讀取 CSV 文件並返回二維陣列

    Args:
        csv_file_path: CSV 文件路徑

    Returns:
        二維陣列，每行是一個列表
    """
    rows = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows


def build_google_services(credentials_json: Optional[str] = None):
    """
    建立 Google Sheets 和 Drive 服務

    Args:
        credentials_json: Service Account JSON 憑證（如果未提供，會從環境變數讀取）

    Returns:
        (sheets_service, drive_service) 元組
    """
    # 讀取憑證
    if credentials_json:
        credentials_info = json.loads(credentials_json)
    else:
        # 嘗試從環境變數讀取
        creds_env = os.getenv('GOOGLE_CLOUD_CREDENTIALS')
        if not creds_env:
            raise ValueError("需要提供 Google Cloud Credentials")
        credentials_info = json.loads(creds_env)

    # 建立憑證物件
    credentials = service_account.Credentials.from_service_account_info(
        info=credentials_info,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )

    # 建立服務
    sheets_service = build('sheets', 'v4', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)

    return sheets_service, drive_service


def create_google_sheet(
    sheets_service,
    drive_service,
    title: str,
    values: list[list[str]],
    folder_id: Optional[str] = None
) -> dict:
    """
    建立 Google Sheets 並寫入資料

    Args:
        sheets_service: Google Sheets API 服務
        drive_service: Google Drive API 服務
        title: 試算表標題
        values: 要寫入的資料（二維陣列）
        folder_id: Google Drive 資料夾 ID（可選）

    Returns:
        建立的試算表資訊
    """
    # 建立試算表
    spreadsheet_body = {
        'properties': {
            'title': title
        }
    }

    try:
        spreadsheet = sheets_service.spreadsheets().create(
            body=spreadsheet_body,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()

        spreadsheet_id = spreadsheet.get('spreadsheetId')
        print(f"✅ 試算表建立成功！ID: {spreadsheet_id}")

        # 寫入資料
        if values:
            range_name = f'Sheet1!A1'
            body = {
                'values': values
            }

            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            print(f"✅ 資料寫入成功！更新了 {result.get('updatedCells')} 個儲存格")

        # 如果指定了資料夾，移動文件
        if folder_id:
            move_to_folder(drive_service, spreadsheet_id, folder_id)

        return spreadsheet

    except HttpError as error:
        raise Exception(f"建立試算表失敗: {error}")


def move_to_folder(drive_service, file_id: str, folder_id: str):
    """
    將文件移動到指定的 Google Drive 資料夾

    Args:
        drive_service: Google Drive API 服務
        file_id: 文件 ID
        folder_id: 目標資料夾 ID
    """
    try:
        # 取得文件的父資料夾
        file = drive_service.files().get(
            fileId=file_id,
            fields='parents'
        ).execute()

        previous_parents = ",".join(file.get('parents', []))

        # 移動文件到新資料夾
        drive_service.files().update(
            fileId=file_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()

        print(f"✅ 文件已移動到資料夾 ID: {folder_id}")

    except HttpError as error:
        print(f"⚠️  移動文件失敗（但試算表已建立）: {error}")


def main():
    parser = argparse.ArgumentParser(
        description="將測試案例 CSV 上傳到 Google Sheets"
    )
    parser.add_argument(
        "--csv-file",
        required=True,
        help="CSV 文件路徑"
    )
    parser.add_argument(
        "--title",
        help="Google Sheets 標題（如果未提供，使用 CSV 檔名）"
    )
    parser.add_argument(
        "--folder-id",
        help="Google Drive 資料夾 ID（可選，預設使用固定資料夾）"
    )
    parser.add_argument(
        "--credentials",
        help="Google Cloud Credentials JSON 字串（如果未提供，會從環境變數讀取）"
    )
    parser.add_argument(
        "--credentials-file",
        help="Google Cloud Credentials JSON 文件路徑"
    )

    args = parser.parse_args()

    # 讀取 CSV 文件
    if not os.path.exists(args.csv_file):
        print(f"❌ 錯誤：CSV 文件不存在：{args.csv_file}")
        sys.exit(1)

    print(f"📖 讀取 CSV 文件：{args.csv_file}")
    values = read_csv_file(args.csv_file)
    print(f"✅ 讀取完成，共 {len(values)} 行資料")

    # 決定標題
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    if args.title:
        title = f"{args.title}_{timestamp}"
    else:
        # 從檔名取得標題
        base_name = os.path.splitext(os.path.basename(args.csv_file))[0]
        # 提取 CAMERA-xxxx 部分（假設檔名格式為 CAMERA-xxxx_...）
        match = re.match(r'^(CAMERA-\d+)', base_name)
        if match:
            title = f"{match.group(1)}_test_case_{timestamp}"
        else:
            # 如果無法匹配，使用原檔名加上 _test_case 與 timestamp
            title = f"{base_name}_test_case_{timestamp}"

    # 讀取憑證並建立 Google 服務
    credentials_json = None
    if args.credentials:
        # 使用 --credentials 參數提供的 JSON 字串
        credentials_json = args.credentials
    else:
        # 決定憑證文件路徑
        if args.credentials_file:
            credentials_file_path = args.credentials_file
        else:
            # 使用預設的憑證文件（專案根目錄的 qa-automation-credentials.json）
            # 腳本在 .claude/skills/alfredqa-testcase-creator/scripts/ 目錄下
            # 需要往上 4 層才能到達專案根目錄
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
            credentials_file_path = os.path.join(project_root, 'qa-automation-credentials.json')
        
        # 讀取憑證文件
        if not os.path.exists(credentials_file_path):
            print(f"❌ 錯誤：憑證文件不存在：{credentials_file_path}")
            sys.exit(1)
        with open(credentials_file_path, 'r', encoding='utf-8') as f:
            credentials_json = f.read()

    # 建立 Google 服務（使用已建立的服務）
    try:
        sheets_service, drive_service = build_google_services(credentials_json)
    except Exception as e:
        print(f"❌ 建立 Google 服務失敗：{e}")
        sys.exit(1)

    # 使用固定的 folder_id（如果未提供）
    DEFAULT_FOLDER_ID = "1I3CdyFlo0Y5Zx3ZLPkPhbQSIFXu19tDj"
    folder_id = args.folder_id if args.folder_id else DEFAULT_FOLDER_ID

    # 建立試算表
    print(f"📊 建立 Google Sheets：{title}")
    try:
        spreadsheet = create_google_sheet(
            sheets_service=sheets_service,
            drive_service=drive_service,
            title=title,
            values=values,
            folder_id=folder_id
        )

        spreadsheet_id = spreadsheet.get('spreadsheetId')
        spreadsheet_url = spreadsheet.get('spreadsheetUrl')

        print("\n" + "="*60)
        print("✅ 上傳成功！")
        print(f"📋 試算表 ID: {spreadsheet_id}")
        print(f"🔗 試算表 URL: {spreadsheet_url}")
        print(f"📁 資料夾 ID: {folder_id}")
        print("="*60)

    except Exception as e:
        print(f"❌ 上傳失敗：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
