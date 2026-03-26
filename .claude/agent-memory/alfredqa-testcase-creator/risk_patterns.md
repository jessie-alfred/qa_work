---
name: 高風險變更模式
description: 跨 PR 累積的常見高風險程式碼變更模式，快速識別需要加強測試的迴歸風險
type: project
---

## 風險模式清單

### 1. Entitlement 判斷邏輯改動
**觸發條件**：`shouldShowPaywall()`、`isPremiumAndFetch`、`isCrPlaybackEnabled`、`isDetectionStandardSupported` 等判斷函式有變動。

**風險**：其他 tier（Standard / Plus）可能被誤判，導致付費用戶看到 Paywall 或功能遭鎖定。

**必加測項**：驗證所有受影響 tier（Free / Premium Lite / Standard / Plus）的行為邊界，尤其是比變更 tier 更高階的方案。

---

### 2. Appcues 流程替換直接付款流程
**觸發條件**：CTA 從 `launchPremium()` 改為 `logAppcuesUpsell()`，或 Appcues placement ID 變動。

**風險**：升級後 unlock 動畫不觸發（因 `onActivityResult` 已移除），`billingState` stream 未正確串接導致功能未解鎖。

**必加測項**：
- Appcues 流程完整走完後 unlock 動畫是否顯示
- 切至背景再回前景（`onResume`）是否正確觸發 `pendingPremiumUnlock`
- 升級後功能即時解鎖（不重啟 App）

---

### 3. 單位或型別轉換（Unit / Type Change）
**觸發條件**：欄位從毫秒改為天、從 `Long` 改為 `Int`、從秒改為分鐘等。

**範例**：`eventExpiredTime`（Long, ms）→ `localEventExpirationDays`（Int, 天）

**風險**：邊界計算錯誤（如 2天 = 172800000ms 但若單位混用會計算成 2ms）。

**必加測項**：驗證過期時間邊界（T+N天-1分 vs T+N天+1分），確認 `rotateEvents()` 計算結果正確。

---

### 4. Entitlement Key 格式動態化
**觸發條件**：hardcoded 物件（如 `Cloud14D`、`Cloud30D`）改為動態解析（如 `Cloud(days)`）。

**風險**：正規表達式解析失敗時 fallback 到 Local，導致 Cloud storage 用戶看到無資料。

**必加測項**：
- 各合法 key（`event:storage:2d`、`event:storage:14d`、`event:storage:30d`）解析正確
- 非法 key（空值、格式錯誤）正確 fallback 到 Local
- 多個 entitlement 並存時，取最高 priority（天數最大）

---

### 5. Activity Result 回呼移除（RC_PAYMENT 等）
**觸發條件**：刪除 `onActivityResult` 中的 payment result 處理。

**風險**：若同時還有其他功能依賴同一 RC_PAYMENT 回呼，可能造成升級後狀態不更新。

**必加測項**：確認所有付款入口的升級後狀態同步正確，並驗證新的 `billingState` stream 覆蓋所有原有入口。

---

### 6. 訂閱方案新增（新 Tier）
**觸發條件**：新增 Premium Lite 等中間方案。

**風險**：
- 現有 Free → Standard 升級流程被新 tier 打斷
- Paywall 顯示不正確的 tier 功能列表
- RevenueCat 未配置新 tier 的 entitlement

**必加測項**：新舊 tier 所有升降級路徑（N 個 tier 有 N*(N-1) 條路徑），重點驗證跨 tier 的功能邊界。
