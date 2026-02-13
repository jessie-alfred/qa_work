# QA 測試案例完整工作流程手冊

## 📋 概述

本手冊說明如何從 JIRA Ticket、PRD、PR 等參考文件，使用 Cursor AI 產生完整的測試案例，並自動上傳到 Google Sheets 的完整流程。

---

## 🎯 工作流程總覽

```
參考文件 (JIRA/PRD/PR)
    ↓
使用 Cursor AI 產生測試案例 (Markdown)
    ↓
轉換為 CSV 格式
    ↓
上傳到 Google Sheets
    ↓
儲存到指定 Google Drive 資料夾
```

---

## 📚 第一階段：準備參考文件

### 1.1 收集必要文件

在開始產生測試案例前，需要準備以下文件：

#### 必要文件
- **JIRA Ticket** (CAMERA-XXXX)
  - 功能描述
  - 技術規格
  - 相關連結

- **PRD/Spec 文件**
  - 產品需求文件
  - 技術規格文件
  - 設計文件

- **GitHub PR**
  - PR 連結
  - 程式碼變更內容
  - 風險評估報告（如有）

#### 文件存放位置
```
target_project/
├── documents/          # 存放 PRD、Spec、Design 等文件
│   ├── PRD_XXX.md
│   ├── Spec_XXX.md
│   └── ...
└── test_case/          # 測試案例產出目錄
```

### 1.2 文件準備檢查清單

- [ ] JIRA Ticket 已確認並取得連結
- [ ] PRD/Spec 文件已放置在 `documents/` 目錄
- [ ] GitHub PR 連結已取得
- [ ] 相關技術文件已收集

---

## 🤖 第二階段：使用 Cursor AI 產生測試案例

### 2.1 開啟 Cursor 並準備提示詞

1. **開啟 Cursor IDE**
2. **開啟專案目錄**：`target_project/`
3. **確認 CURSOR.md 文件存在**：此文件包含產生測試案例的指令提示詞

### 2.2 使用 Cursor AI 產生測試案例

#### 標準提示詞格式

在 Cursor 中輸入以下提示詞：

```
請根據以下來源文件及 PR 建立 CAMERA-XXXX 測試案例：

@target_project/CURSOR.md
@documents/[PRD/Spec文件名稱]
[JIRA Ticket 連結]
[GitHub PR 連結]

請根據來源文件及 PR 建立 CAMERA-XXXX 測試案例
```

#### 範例提示詞

```
請根據以下來源文件及 PR 建立 CAMERA-6103 測試案例：

@target_project/CURSOR.md
@documents/User_Property_Sync_Mechanism_for_Third-Party_Services.md
https://alfredlabs.atlassian.net/browse/CAMERA-6103
https://github.com/alfred-systems/iVuu/pull/5256

請根據來源文件及 PR 建立 CAMERA-6103 測試案例
```

### 2.3 Cursor AI 會自動執行

Cursor AI 會：
1. 讀取 `CURSOR.md` 了解測試案例格式規範
2. 分析 `documents/` 中的相關文件
3. 參考 JIRA Ticket 和 GitHub PR
4. 產生符合規範的測試案例 Markdown 文件

### 2.4 檢查產出的測試案例

產出的文件會位於：
```
test_case/CAMERA-XXXX_Feature_Name_TestCase.md
```

**檢查要點**：
- [ ] 測試案例編號正確
- [ ] 測試分類完整（功能、穩定性、UX、效能、迴歸）
- [ ] 測試步驟詳細清楚
- [ ] 預期結果明確
- [ ] 涵蓋邊緣案例

---

## 📊 第三階段：轉換為 CSV 格式

### 3.1 確認 Markdown 文件

確認測試案例 Markdown 文件已產生並符合規範。

### 3.2 使用 Cursor AI 轉換為 CSV

在 Cursor 中輸入：

```
@target_project/test_case/CAMERA-XXXX_Feature_Name_TestCase.md

請將此測試案例轉換為 CSV 格式，並儲存為：
test_case/CAMERA-XXXX_Feature_Name_TestCase.csv

CSV 格式要求：
- 欄位：測試案例編號,測試分類,測試標題,測試目標,前置條件,測試步驟,預期結果,優先級,狀態,備註
- 測試步驟和預期結果中的分號（;）要轉換為換行符，以便在 Google Sheets 中正確顯示
```

### 3.3 驗證 CSV 文件

檢查產出的 CSV 文件：
- [ ] 欄位正確
- [ ] 資料完整
- [ ] 換行符正確處理（測試步驟和預期結果）

---

## ☁️ 第四階段：上傳到 Google Sheets

### 4.1 前置準備

#### 4.1.1 安裝 Python 套件

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### 4.1.2 設定 Google Cloud Credentials

**步驟 1：建立 Google Service Account**

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立或選擇專案
3. 啟用 API：
   - Google Sheets API
   - Google Drive API
4. 建立 Service Account：（若無權限，請找 server team 協助）
   - 前往「IAM & Admin」→「Service Accounts」
   - 點擊「Create Service Account」
   - 填寫名稱和描述
   - 選擇角色：`Editor` 或 `Owner`
5. 建立 Key：（只需製作一次）
   - 點擊建立的 Service Account
   - 前往「Keys」標籤
   - 點擊「Add Key」→「Create new key」
   - 選擇「JSON」格式
   - 下載 JSON 文件

**步驟 2：分享 Google Drive 資料夾**

1. 在 Google Drive 中開啟目標資料夾
2. 右鍵點擊 →「共用」
3. 輸入 Service Account 的 Email（格式：`xxx@xxx.iam.gserviceaccount.com`）
4. 給予「編輯者」權限

**步驟 3：取得資料夾 ID**

從 Google Drive URL 取得：
```
https://drive.google.com/drive/folders/{FOLDER_ID}
```

#### 4.1.3 設定環境變數

```bash
# 方式 1：從 JSON 文件讀取
export GOOGLE_CLOUD_CREDENTIALS=$(cat path/to/credentials.json)

# 方式 2：直接設定 JSON 字串（不推薦，安全性較低）
export GOOGLE_CLOUD_CREDENTIALS='{"type":"service_account",...}'
```

### 4.2 執行上傳腳本

#### 基本使用

```bash
python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-XXXX_Feature_Name_TestCase.csv" \
    --title "CAMERA-XXXX 測試案例" \
    --folder-id "your-folder-id"
```

#### 完整範例

```bash
# 1. 設定環境變數
export GOOGLE_CLOUD_CREDENTIALS=$(cat qa-automation-credentials.json)

# 2. 執行上傳
python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv" \
    --title "CAMERA-6103 Android 用戶屬性同步第三方服務測試案例" \
    --folder-id "1ABC123xyz456DEF789"
```

### 4.3 驗證上傳結果

成功上傳後會顯示：
- ✅ 試算表 ID
- ✅ 試算表 URL
- ✅ 資料夾 ID

前往 Google Drive 確認文件已正確建立並位於指定資料夾。

---

## 🔄 完整工作流程範例

### 範例：CAMERA-6103 測試案例

#### 步驟 1：準備文件
```
documents/
└── User_Property_Sync_Mechanism_for_Third-Party_Services.md  # 技術規格文件
```

#### 步驟 2：使用 Cursor AI 產生測試案例

在 Cursor 中輸入：
```
請根據以下來源文件及 PR 建立 CAMERA-6103 測試案例：

@target_project/CURSOR.md
@documents/User_Property_Sync_Mechanism_for_Third-Party_Services.md
https://alfredlabs.atlassian.net/browse/CAMERA-6103
https://github.com/alfred-systems/iVuu/pull/5256

請根據來源文件及 PR 建立 CAMERA-6103 測試案例
```

#### 步驟 3：轉換為 CSV

在 Cursor 中輸入：
```
@target_project/test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.md

請將此測試案例轉換為 CSV 格式，並儲存為：
test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv

CSV 格式要求：
- 欄位：測試案例編號,測試分類,測試標題,測試目標,前置條件,測試步驟,預期結果,優先級,狀態,備註
- 測試步驟和預期結果中的分號（;）要轉換為換行符
```

#### 步驟 4：上傳到 Google Sheets

```bash
export GOOGLE_CLOUD_CREDENTIALS=$(cat qa-automation-credentials.json)

python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv" \
    --title "CAMERA-6103 Android 用戶屬性同步第三方服務測試案例" \
    --folder-id "1ABC123xyz456DEF789"
```

---

## 📋 快速參考指令

### 產生測試案例

```
請根據以下來源文件及 PR 建立 CAMERA-XXXX 測試案例：

@target_project/CURSOR.md
@documents/[文件名稱]
[JIRA Ticket 連結]
[GitHub PR 連結]

請根據來源文件及 PR 建立 CAMERA-XXXX 測試案例
```

### 轉換為 CSV

```
@target_project/test_case/CAMERA-XXXX_Feature_Name_TestCase.md

請將此測試案例轉換為 CSV 格式，並儲存為：
test_case/CAMERA-XXXX_Feature_Name_TestCase.csv

CSV 格式要求：
- 欄位：測試案例編號,測試分類,測試標題,測試目標,前置條件,測試步驟,預期結果,優先級,狀態,備註
- 測試步驟和預期結果中的分號（;）要轉換為換行符
```

### 上傳到 Google Sheets

```bash
export GOOGLE_CLOUD_CREDENTIALS=$(cat qa-automation-credentials.json)

python upload_to_google_sheets.py \
    --csv-file "test_case/CAMERA-XXXX_Feature_Name_TestCase.csv" \
    --title "CAMERA-XXXX 測試案例" \
    --folder-id "your-folder-id"
```

---

## 🔍 疑難排解

### 問題 1：Cursor AI 無法讀取文件

**解決方式**：
- 確認文件路徑正確
- 確認文件在專案目錄內
- 使用 `@` 符號引用文件

### 問題 2：測試案例格式不符合規範

**解決方式**：
- 確認 `CURSOR.md` 文件存在且格式正確
- 在提示詞中明確引用 `@target_project/CURSOR.md`
- 檢查產出的測試案例是否符合範例格式

### 問題 3：CSV 轉換失敗

**解決方式**：
- 確認 Markdown 文件格式正確
- 檢查測試案例編號是否連續
- 確認所有必要欄位都有內容

### 問題 4：Google Sheets 上傳失敗

**解決方式**：
- 確認 Google Cloud Credentials 正確設定
- 確認已啟用 Google Sheets API 和 Google Drive API
- 確認資料夾已分享給 Service Account
- 檢查資料夾 ID 是否正確

### 問題 5：權限錯誤

**錯誤訊息**：`403 Forbidden` 或 `Permission denied`

**解決方式**：
- 確認 Service Account 有編輯 Google Drive 的權限
- 確認目標資料夾已分享給 Service Account Email
- 確認 Service Account 有建立 Google Sheets 的權限

---

## 📚 相關文件

### 專案文件
- **CURSOR.md** - 測試案例產生指令提示詞和規範
- **documents/** - PRD、Spec、Design 等參考文件
- **test_case/** - 測試案例產出目錄

### 工具腳本
- **upload_to_google_sheets.py** - Google Sheets 上傳腳本

### 參考資源
- [Terminology Table v2](https://alfredlabs.atlassian.net/wiki/spaces/~590960658/pages/3834085744/Terminology+Table+v2) - 阿褔管家 APP 產品專有名詞
- [Google Sheets API 文件](https://developers.google.com/sheets/api)
- [Google Drive API 文件](https://developers.google.com/drive/api)

---

## ✅ 工作流程檢查清單

### 準備階段
- [ ] JIRA Ticket 已確認
- [ ] PRD/Spec 文件已收集並放置在 `documents/`
- [ ] GitHub PR 連結已取得
- [ ] 相關技術文件已準備

### 產生測試案例階段
- [ ] 在 Cursor 中輸入正確的提示詞
- [ ] 確認 Cursor AI 已讀取所有參考文件
- [ ] 檢查產出的 Markdown 文件格式
- [ ] 驗證測試案例完整性

### 轉換 CSV 階段
- [ ] 使用 Cursor AI 轉換為 CSV
- [ ] 驗證 CSV 文件格式正確
- [ ] 確認換行符正確處理

### 上傳 Google Sheets 階段
- [ ] Google Cloud Credentials 已設定
- [ ] Google Drive 資料夾已分享給 Service Account
- [ ] 資料夾 ID 已取得
- [ ] 執行上傳腳本
- [ ] 驗證 Google Sheets 已正確建立
- [ ] 確認文件位於正確的資料夾

---

## 🎯 最佳實踐

### 1. 文件管理
- 將所有參考文件統一放在 `documents/` 目錄
- 使用清晰的檔名，便於識別
- 定期清理不需要的文件

### 2. 測試案例命名
- 遵循命名規範：`CAMERA-XXXX_Feature_Name_TestCase.md`
- 確保檔名清楚描述功能

### 3. 版本控制
- 將測試案例 Markdown 和 CSV 文件提交到版本控制
- **不要**提交 Google Cloud Credentials JSON 文件
- 使用 `.gitignore` 排除敏感文件

### 4. 品質檢查
- 產出測試案例後，人工檢查一次
- 確認測試案例涵蓋所有重要場景
- 驗證邊緣案例和錯誤處理

### 5. 協作
- 在 Google Sheets 中與團隊成員協作
- 使用 Google Sheets 的評論功能進行討論
- 定期更新測試狀態

---

## 📝 範例工作流程記錄

### 範例：CAMERA-6103

**日期**：2025-12-10  
**負責人**：Jessie

**步驟記錄**：
1. ✅ 收集文件：
   - JIRA: CAMERA-6103
   - Spec: User Property Sync Mechanism for Third-Party Services
   - PR: #5256

2. ✅ 產生測試案例：
   - 使用 Cursor AI 產生 Markdown 文件
   - 產出：`CAMERA-6103_User_Property_Sync_Third_Party_TestCase.md`
   - 共 25 個測試案例

3. ✅ 轉換 CSV：
   - 使用 Cursor AI 轉換
   - 產出：`CAMERA-6103_User_Property_Sync_Third_Party_TestCase.csv`

4. ✅ 上傳 Google Sheets：
   - 試算表 ID: `1ABC123xyz456DEF789`
   - URL: `https://docs.google.com/spreadsheets/d/1ABC123xyz456DEF789`
   - 資料夾 ID: `1ABC123xyz456DEF789`

---

## ⚠️ 注意事項

1. **憑證安全**
   - 不要將 Google Cloud Credentials JSON 提交到版本控制
   - 使用環境變數或安全的憑證管理系統

2. **權限管理**
   - 只給予 Service Account 必要的權限
   - 定期檢查和更新權限設定

3. **API 配額**
   - 注意 Google API 的使用配額限制
   - 避免頻繁建立和刪除試算表

4. **文件備份**
   - 定期備份測試案例 Markdown 和 CSV 文件
   - 保留歷史版本以便追蹤

5. **協作規範**
   - 在 Google Sheets 中進行協作時，注意不要覆蓋重要資料
   - 使用版本歷史功能追蹤變更

---

## 🚀 進階技巧

### 1. 批次處理多個測試案例

如果需要處理多個測試案例，可以建立批次腳本：

```bash
#!/bin/bash

# 批次上傳多個測試案例
for csv_file in test_case/*.csv; do
    base_name=$(basename "$csv_file" .csv)
    title="${base_name//_/ }"
    
    python upload_to_google_sheets.py \
        --csv-file "$csv_file" \
        --title "$title" \
        --folder-id "your-folder-id"
done
```

### 2. 自動化工作流程

可以將整個流程整合到 CI/CD 或自動化腳本中，實現：
- 自動監控 JIRA Ticket 狀態
- 自動產生測試案例
- 自動上傳到 Google Sheets

### 3. 測試案例模板

建立測試案例模板，加速產生過程：
- 功能測試模板
- 迴歸測試模板
- 效能測試模板

---

## 📞 支援與協助

如有問題或需要協助，請：
1. 檢查本手冊的疑難排解章節
2. 參考相關文件連結
3. 聯繫 QA 團隊

---

**最後更新**：2025-12-10  
**版本**：1.0
