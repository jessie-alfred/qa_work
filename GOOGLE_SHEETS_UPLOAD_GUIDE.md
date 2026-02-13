# Google Sheets 上傳指南

## 📋 功能說明

此腳本可以將測試案例 CSV 文件轉換為 Google Sheets 格式，並上傳到 Google Drive 的指定資料夾。

## 🔧 前置需求

### 1. 安裝 Python 套件

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. 設定 Google Cloud Credentials

需要建立 Google Service Account 並取得憑證 JSON 文件。

#### 步驟：

1. **前往 Google Cloud Console**
   - https://console.cloud.google.com/

2. **建立或選擇專案**

3. **啟用 API**
   - 啟用 "Google Sheets API"
   - 啟用 "Google Drive API"

4. **建立 Service Account**
   - 前往「IAM & Admin」→「Service Accounts」
   - 點擊「Create Service Account」
   - 填寫名稱和描述
   - 點擊「Create and Continue」
   - 選擇角色：`Editor` 或 `Owner`
   - 點擊「Done」

5. **建立 Key**
   - 點擊建立的 Service Account
   - 前往「Keys」標籤
   - 點擊「Add Key」→「Create new key」
   - 選擇「JSON」格式
   - 下載 JSON 文件

6. **分享 Google Drive 資料夾給 Service Account**
   - 在 Google Drive 中，右鍵點擊目標資料夾
   - 選擇「共用」
   - 輸入 Service Account 的 Email（格式：`xxx@xxx.iam.gserviceaccount.com`）
   - 給予「編輯者」權限

### 3. 取得 Google Drive 資料夾 ID

1. 在 Google Drive 中開啟目標資料夾
2. 從 URL 中取得資料夾 ID：
   ```
   https://drive.google.com/drive/folders/{FOLDER_ID}
   ```

---

## 🚀 使用方式

### 方式 1：使用環境變數（推薦）

```bash
# 設定環境變數
export GOOGLE_CLOUD_CREDENTIALS='{"type":"service_account",...}'  # JSON 字串

# 執行腳本
python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv" \
    --title "CAMERA-6103 測試案例" \
    --folder-id "your-folder-id"
```

### 方式 2：使用憑證文件

```bash
python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv" \
    --title "CAMERA-6103 測試案例" \
    --folder-id "your-folder-id" \
    --credentials-file "path/to/credentials.json"
```

### 方式 3：直接提供 JSON 字串

```bash
python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv" \
    --title "CAMERA-6103 測試案例" \
    --folder-id "your-folder-id" \
    --credentials '{"type":"service_account",...}'
```

---

## 📝 參數說明

| 參數 | 必填 | 說明 |
|------|------|------|
| `--csv-file` | ✅ | CSV 文件路徑 |
| `--title` | ❌ | Google Sheets 標題（如果未提供，使用 CSV 檔名） |
| `--folder-id` | ❌ | Google Drive 資料夾 ID（如果未提供，會建立在使用者的根目錄） |
| `--credentials` | ❌ | Google Cloud Credentials JSON 字串 |
| `--credentials-file` | ❌ | Google Cloud Credentials JSON 文件路徑 |

---

## 📋 完整範例

```bash
# 1. 設定環境變數（從 JSON 文件讀取）
export GOOGLE_CLOUD_CREDENTIALS=$(cat path/to/credentials.json)

# 2. 執行腳本
python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv" \
    --title "CAMERA-6103 Android 用戶屬性同步第三方服務測試案例" \
    --folder-id "1ABC123xyz456DEF789"
```

---

## ✅ 執行結果

成功執行後會顯示：

```
📖 讀取 CSV 文件：test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv
✅ 讀取完成，共 26 行資料
🔐 建立 Google 服務...
✅ Google 服務建立成功
📊 建立 Google Sheets：CAMERA-6103 Android 用戶屬性同步第三方服務測試案例
✅ 試算表建立成功！ID: 1ABC123xyz456DEF789
✅ 資料寫入成功！更新了 260 個儲存格
✅ 文件已移動到資料夾 ID: 1ABC123xyz456DEF789

============================================================
✅ 上傳成功！
📋 試算表 ID: 1ABC123xyz456DEF789
🔗 試算表 URL: https://docs.google.com/spreadsheets/d/1ABC123xyz456DEF789
📁 資料夾 ID: 1ABC123xyz456DEF789
============================================================
```

---

## 🔍 疑難排解

### 問題 1：認證失敗

**錯誤訊息**：`Invalid credentials` 或 `401 Unauthorized`

**解決方式**：
- 確認 JSON 憑證文件格式正確
- 確認 Service Account 已啟用
- 確認已啟用 Google Sheets API 和 Google Drive API

### 問題 2：權限不足

**錯誤訊息**：`403 Forbidden` 或 `Permission denied`

**解決方式**：
- 確認 Service Account 有編輯 Google Drive 資料夾的權限
- 確認已分享資料夾給 Service Account Email

### 問題 3：資料夾 ID 錯誤

**錯誤訊息**：`File not found` 或 `Invalid folder ID`

**解決方式**：
- 確認資料夾 ID 正確（從 Google Drive URL 取得）
- 確認資料夾已分享給 Service Account

### 問題 4：CSV 格式問題

**錯誤訊息**：`Invalid CSV format`

**解決方式**：
- 確認 CSV 文件編碼為 UTF-8
- 確認 CSV 格式正確（使用逗號分隔）

---

## 📚 相關資源

- [Google Sheets API 文件](https://developers.google.com/sheets/api)
- [Google Drive API 文件](https://developers.google.com/drive/api)
- [Service Account 說明](https://cloud.google.com/iam/docs/service-accounts)

---

## ⚠️ 注意事項

1. **憑證安全**：不要將憑證 JSON 文件提交到版本控制系統
2. **權限管理**：只給予 Service Account 必要的權限
3. **資料夾分享**：記得分享目標資料夾給 Service Account
4. **API 配額**：注意 Google API 的使用配額限制
