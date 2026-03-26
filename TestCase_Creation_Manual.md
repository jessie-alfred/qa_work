# 測試案例建立手冊

## 概覽

本手冊說明如何為 **Alfred Camera** APP 建立完整的測試案例，涵蓋必備輸入要件、工作流程、文件規範與注意事項。

---

## 必備輸入要件

建立測項前，**必須**備齊以下三項輸入：

### 1. JIRA Ticket
- 格式：`CAMERA-XXXX`
- 用途：取得功能摘要、Epic 脈絡、Fix Version、Sprint 目標，判斷測試範疇
- 取得方式：透過 Atlassian MCP（`getJiraIssue`）讀取
- 確認項目：
  - `summary`：功能描述
  - `parent`：所屬 Epic
  - `fixVersions`：目標版本
  - `status`：確認狀態為 Ready for Test

### 2. 需求文件（Spec / PRD）
- 格式：`.md` 或 `.xlsx`（xlsx 需先轉換）
- 用途：了解功能邊界、Entitlement 規則、UI 行為、各 Tier 差異
- 必須包含的資訊：
  - 各訂閱方案（Free / Premium Lite / Standard / Plus）功能對照
  - Entitlement Key 名稱（如 `cr:playback`、`event:storage:2d`）
  - Paywall / 遮罩觸發條件與 CTA 行為
  - 數值邊界（如：保留天數、相機數量上限、解析度限制）
- 參考位置：`.claude/skills/alfredqa-testcase-creator/references/`

### 3. GitHub PR
- 格式：`https://github.com/alfred-systems/{repo}/pull/{number}`
- 用途：了解程式碼實際異動範圍，識別迴歸風險區
- 取得方式：透過 GitHub MCP（`get_pull_request`、`get_pull_request_files`）讀取
- 確認項目：
  - 異動的檔案與模組
  - PR 描述中的實作細節
  - 是否有影響其他 Tier 的共用邏輯

> **注意**：若 GitHub PR 無法存取（如 401 權限問題），可改從 JIRA `customfield_10300`（PR 狀態欄位）確認 PR 已 merged，並以 JIRA 摘要 + Spec 作為主要依據繼續產出測項。

---

## 輔助參考文件

以下文件在每次建立測項時必須參照：

| 文件 | 路徑 | 用途 |
|------|------|------|
| 核心功能清單 | `.claude/skills/alfredqa-testcase-creator/references/core-functionality.md` | 判斷哪些模組受影響、迴歸風險區 |
| 輸出格式規範 | `.claude/skills/alfredqa-testcase-creator/references/output-patterns.md` | 測項標題格式、優先級標示規則 |
| 異常情境勾選表 | `.claude/skills/alfredqa-testcase-creator/references/Test_Scenario.md` | 決定第 6 節要展開哪些異常情境 |
| Entitlement 對照表 | `.claude/agent-memory/alfredqa-testcase-creator/product_entitlements.md` | 各 Tier 功能邊界與 Entitlement Key 快速比對 |

---

## 工作流程

```
1. 輸入 JIRA ID
       ↓
2. 讀取資料（並行執行）
   ├── Atlassian MCP → JIRA Ticket 摘要
   ├── GitHub MCP → PR 異動範圍
   └── 讀取 Spec / PRD 文件
       ↓
3. 交叉比對 Entitlement 對照表
   確認功能邊界是否完整（避免遺漏）
       ↓
4. 產出測試重點摘要
   ├── 影響模組/功能
   ├── 迴歸風險區
   └── 高風險情境建議
       ↓
5. 產出測試案例 .md
   共六節，存至 test_case/CAMERA-XXXX_TestCase.md
       ↓
6. 轉換 CSV
   python .claude/skills/alfredqa-testcase-creator/scripts/convert_md_to_csv.py \
     --md-file "test_case/CAMERA-XXXX_TestCase.md"
       ↓
7. 上傳 Google Sheets
   python .claude/skills/alfredqa-testcase-creator/scripts/upload_to_google_sheets.py \
     --csv-file "test_case/CAMERA-XXXX_TestCase.csv"
```

---

## 測試案例結構（六節）

每份測試案例文件必須包含以下六節：

| 節次 | 名稱 | 說明 |
|------|------|------|
| 第 1 節 | 功能與業務邏輯測試 | 核心功能行為、Entitlement 啟用、數值邊界 |
| 第 2 節 | Entitlement / 訂閱控制邏輯 | entitlement key 授權正確性、各 Tier 差異驗證 |
| 第 3 節 | 使用者情境測試（Paywall）| 用戶實際操作路徑、Paywall 觸發、遮罩 CTA |
| 第 4 節 | Membership 轉換測試 | 升降級路徑的功能邊界驗證（Free ↔ Lite ↔ Standard ↔ Plus）|
| 第 5 節 | 穩定性與邊緣案例 | 時間邊界、多裝置同步、降級狀態、功能即時生效 |
| 第 6 節 | 異常情境測試 | 依 `Test_Scenario.md` 勾選項目展開，使用字母前綴編號（A-1、B-1 等）|

> 若 `Test_Scenario.md` 中所有項目均未勾選，可省略第 6 節。

---

## 測項格式規範

```markdown
### {節號}.{序號} {測項標題} ⭐ P0|P1
**測試步驟**：{具體操作步驟，包含帳號 Tier、功能入口、觸發條件}

**預期結果**：{明確的預期行為，包含數值、UI 狀態、entitlement 反應}
```

**優先級定義：**
- ⭐ **P0**：核心功能，影響主要功能運作（訂閱授權、功能解鎖、Paywall 觸發）
- ⭐ **P1**：重要功能，影響使用者體驗或邊緣案例（邊界值、UI 適配、降級行為）

---

## 完整性自我檢查清單

產出測項後，對照 Entitlement 對照表逐一確認：

- [ ] 該 Tier 所有**可用功能**都有正向測項（功能可正常使用）
- [ ] 該 Tier 所有**不可用功能**都有對應的遮罩 / 提示測項
- [ ] 每個 entitlement key 都有對應的授權驗證測項
- [ ] 升降級路徑（至少 Free → 目標 Tier、目標 Tier → 上一 Tier、目標 Tier → Free）已涵蓋
- [ ] 數值邊界（天數、台數、時長）已有邊界值測項
- [ ] `Test_Scenario.md` 勾選的異常情境已全數展開

---

## 檔案輸出位置

| 類型 | 路徑 |
|------|------|
| 測試案例（Markdown）| `test_case/CAMERA-XXXX_TestCase.md` |
| 測試案例（CSV）| `test_case/CAMERA-XXXX_TestCase.csv` |
| Google Sheets | 上傳後取得 URL，存入指定 Google Drive 資料夾 |

---

## 常見問題

**Q：GitHub PR 取得 401 錯誤怎麼辦？**
可改從 JIRA 的 PR 狀態欄位確認 PR 已 merged，並以 JIRA 摘要 + Spec 文件作為主要依據繼續產出，PR 異動細節可事後補充迴歸測項。

**Q：Spec 文件是 Excel 格式怎麼辦？**
先執行 `python xlsx_to_firebase_event_md.py {excel_file}` 將 Excel 轉為 Markdown，再作為輸入。

**Q：如何確認測項是否完整？**
對照 `.claude/agent-memory/alfredqa-testcase-creator/product_entitlements.md` 的功能對照表，逐行確認每個功能都有對應測項。
