# QA 測試案例工作流程 - 快速參考

## 🚀 三步驟快速流程

### 步驟 1：產生測試案例（使用 Cursor AI）

```
請根據以下來源文件及 PR 建立 CAMERA-XXXX 測試案例：

@target_project/CURSOR.md
@documents/[PRD/Spec文件名稱]
[JIRA Ticket 連結]
[GitHub PR 連結]

請根據來源文件及 PR 建立 CAMERA-XXXX 測試案例
```

**產出**：`test_case/CAMERA-XXXX_Feature_Name_TestCase.md`

---

### 步驟 2：轉換為 CSV（使用 Cursor AI）

```
@target_project/test_case/CAMERA-XXXX_Feature_Name_TestCase.md

請將此測試案例轉換為 CSV 格式，並儲存為：
test_case/CAMERA-XXXX_Feature_Name_TestCase.csv

CSV 格式要求：
- 欄位：測試案例編號,測試分類,測試標題,測試目標,前置條件,測試步驟,預期結果,優先級,狀態,備註
- 測試步驟和預期結果中的分號（;）要轉換為換行符
```

**產出**：`test_case/CAMERA-XXXX_Feature_Name_TestCase.csv`

---

### 步驟 3：上傳到 Google Sheets

```bash
# 設定環境變數
export GOOGLE_CLOUD_CREDENTIALS=$(cat qa-automation-credentials.json)

# 執行上傳
python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-XXXX_Feature_Name_TestCase.csv" \
    --title "CAMERA-XXXX 測試案例" \
    --folder-id "your-folder-id"
```

**產出**：Google Sheets 試算表（位於指定 Google Drive 資料夾）

---

## 📋 前置準備檢查清單

### 文件準備
- [ ] JIRA Ticket 連結
- [ ] PRD/Spec 文件已放在 `documents/`
- [ ] GitHub PR 連結

### Google Sheets 設定
- [ ] 已安裝 Python 套件：`pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`
- [ ] 已建立 Google Service Account
- [ ] 已下載 Credentials JSON 文件
- [ ] 已啟用 Google Sheets API 和 Google Drive API
- [ ] 已分享目標資料夾給 Service Account
- [ ] 已取得資料夾 ID

---

## 🔗 相關文件

- **完整手冊**：`QA_TEST_CASE_WORKFLOW_GUIDE.md`
- **Cursor 提示詞**：`CURSOR.md`
- **上傳腳本**：`upload_to_google_sheets.py`
- **上傳指南**：`GOOGLE_SHEETS_UPLOAD_GUIDE.md`

---

## ⚡ 常見問題快速解決

| 問題 | 解決方式 |
|------|----------|
| Cursor 無法讀取文件 | 確認使用 `@` 符號，路徑正確 |
| CSV 格式錯誤 | 確認分號已轉換為換行符 |
| Google 認證失敗 | 檢查 Credentials JSON 和環境變數 |
| 權限錯誤 | 確認資料夾已分享給 Service Account |
