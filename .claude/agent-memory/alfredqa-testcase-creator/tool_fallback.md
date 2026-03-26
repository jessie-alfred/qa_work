---
name: 工具使用規則與替代指令
description: GitHub MCP 失敗時的替代 CLI 指令、測案轉換與上傳腳本路徑
type: feedback
---

## GitHub PR 讀取

**Why：** GitHub MCP 在部分情況下會回傳 401 Bad credentials，需要 fallback 到 gh CLI。

**How to apply：** 優先使用 GitHub MCP；若遭遇 401 錯誤，立即切換為以下 CLI 指令：

```bash
# PR 基本資訊
gh pr view {PR號} --repo alfred-systems/iVuu --json title,body,files,additions,deletions

# 完整 diff（分析程式碼變更）
gh pr diff {PR號} --repo alfred-systems/iVuu
```

## 測案轉換與上傳腳本

所有腳本皆在**專案根目錄**執行：

```bash
# MD → CSV 轉換
python .claude/skills/alfredqa-testcase-creator/scripts/convert_md_to_csv.py \
  --md-file "test_case/{filename}.md"

# CSV → Google Sheets 上傳
python .claude/skills/alfredqa-testcase-creator/scripts/upload_to_google_sheets.py \
  --csv-file "test_case/{filename}.csv"
```

輸出 CSV 存放在與 MD 同目錄（`test_case/`）。

## 參考文件路徑

| 文件 | 路徑 |
|------|------|
| 核心功能清單 | `.claude/skills/alfredqa-testcase-creator/references/core-functionality.md` |
| 輸出格式範例 | `.claude/skills/alfredqa-testcase-creator/references/output-patterns.md` |
| 異常情境勾選 | `.claude/skills/alfredqa-testcase-creator/references/Test_Scenario.md` |
| Premium Lite 規格 | `.claude/skills/alfredqa-testcase-creator/references/Premium_lite_spec.md` |
