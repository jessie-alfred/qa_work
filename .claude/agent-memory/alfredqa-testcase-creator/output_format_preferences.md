---
name: 測項輸出格式偏好
description: 此專案採用 6 節測項格式（非 output-patterns.md 的 5 節），各節名稱與編號規則
type: feedback
---

此專案的測項採用 **6 節格式**，與 `output-patterns.md` 範本的 5 節不同，產生測案時以此為準。

**Why：** 訂閱類功能需要專屬的 Membership 轉換章節，第 4 節固定為此用途。

**How to apply：** 每次產出測案時，依下列 6 節結構輸出，不要跟著 output-patterns.md 縮減為 5 節。

## 測項章節結構（6 節）

| 節次 | 名稱 | 編號格式 |
|------|------|------|
| 第 1 節 | 功能與業務邏輯測試（Functional & Business Logic） | 1.1、1.2… |
| 第 2 節 | Entitlement / 訂閱控制邏輯（依需求調整節名） | 2.1、2.2… |
| 第 3 節 | 使用者情境測試（User Scenarios / Paywall） | 3.1、3.2… |
| 第 4 節 | Membership 轉換測試（Membership Conversion） | 4.1、4.2… |
| 第 5 節 | 穩定性與邊緣案例測試（Stability & Edge Cases） | 5.1、5.2… |
| 第 6 節 | 異常情境測試（Abnormal Scenarios） | A-1、B-1、D-1、E-1… |

## 第 6 節異常情境字母前綴分類

- **A**：網路異常
- **B**：螢幕方向異常
- **C**：App 生命週期異常
- **D**：帳號與權限同步異常
- **E**：儲存邊界異常
- **F**：偵測功能異常

只展開 `Test_Scenario.md` 中 `[x]` 勾選的項目，未勾選（`[ ]`）略過。

## 其他格式規則

- 每個測項標題：`### x.y 測項名稱 ⭐ Px`
- 內文固定兩欄：`**測試步驟**：` 和 `**預期結果**：`
- 優先級：⭐ P0（核心必測）、⭐ P1（重要）
- 具體參數優先（天數、人數、解析度、金額）優於模糊描述
- 無 JIRA ID 時，檔名使用功能名稱：`{FeatureName}_TestCase.md`
