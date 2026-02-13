---
name: alfredqa-testcase-creator
description: 依照讀取的文件產生阿褔管家產品 APP 的測試重點摘要包括風險評估，以及測試案例。
---

**阿褔管家** APP 產品專有名詞，請參考 Terminology Table
https://alfredlabs.atlassian.net/wiki/spaces/~590960658/pages/3834085744/Terminology+Table+v2

## 輸入
* JIRA ID 格式：`CAMERA-XXXX`
* 此 JIRA ID 必須要有 GitHub PR 以及相關的需求文件
* 取得方式：使用 MCP tool（如 GitHub MCP 或 Atlassian MCP）來讀取 PR 和需求文件
* 核心功能參考：讀取 `.claude/skills/alfredqa-testcase-creator/references/core-functionality.md` 以了解核心功能清單

## 輸出
1. **測試重點（包括風險評估）**

### 📋 測試重點結構規範
綜合評估產出測試重點摘要與風險評估 (Focus Areas & Risk Assessment)

* **影響模組/功能**：根據 PRD 和 PR 變動，列出受本次變更影響的核心模組/功能清單。核心模組/功能清單請參考 `.claude/skills/alfredqa-testcase-creator/references/core-functionality.md`

* **迴歸風險區**：列出與變動功能有高度耦合，需要進行迴歸測試的舊有功能區域（例如：若變更了登入機制，則需回歸驗證用戶權限和訂閱狀態）。

* **具體測試場景建議（含邊緣案例）**：提供本次變更最需要關注的**高風險情境**測試建議。

**產出位置**：測試重點摘要產出在測試案例文件的開頭部分，作為測試規劃的參考。

2. **測試案例**
格式及規範參考 `.claude/skills/alfredqa-testcase-creator/references/output-patterns.md`


## 測試案例 .md 轉換成 csv 格式
1. 當測試案例已生成並且提到轉換為 csv 格式時，運行 `convert_md_to_csv.py`
   * 腳本位置：`.claude/skills/alfredqa-testcase-creator/scripts/convert_md_to_csv.py`
   * 工作目錄：在專案根目錄執行
   * 使用方式：`python .claude/skills/alfredqa-testcase-creator/scripts/convert_md_to_csv.py --md-file "test_case/{{CAMERA-XXXX}}_TestCase.md"`
   * 輸出：將產生的 .csv 文件存放在與測試案例 .md 同目錄

## 上傳 .csv 至雲端
將 .csv 的測項文件 import 到 Google Sheet 並上傳至指定的 Google Drive，運行以下腳本：

* 腳本位置：`.claude/skills/alfredqa-testcase-creator/scripts/upload_to_google_sheets.py`
* 工作目錄：在專案根目錄執行
* 使用方式：`python .claude/skills/alfredqa-testcase-creator/scripts/upload_to_google_sheets.py --csv-file "test_case/{{CAMERA-XXXX}}_TestCase.csv"`
* 前置需求：需安裝 Google API 相關套件（詳見腳本註解）
* 注意事項：需要設定 Google Cloud Credentials（可透過環境變數 `GOOGLE_CLOUD_CREDENTIALS` 或 `--credentials-file` 參數提供）

## 完整工作流程
1. **輸入 JIRA ID**：提供格式為 `CAMERA-XXXX` 的 JIRA ID
2. **讀取相關文件**：使用 MCP tool 讀取 GitHub PR 和需求文件
3. **產出測試重點**：分析 PRD 和 PR 變動，產出測試重點摘要與風險評估
4. **產出測試案例**：根據測試重點，產出完整的測試案例文件（`.md` 格式）
5. **轉換格式（可選）**：如需轉換為 CSV 格式，運行轉換腳本
6. **上傳雲端（可選）**：如需上傳至 Google Drive，運行上傳腳本
