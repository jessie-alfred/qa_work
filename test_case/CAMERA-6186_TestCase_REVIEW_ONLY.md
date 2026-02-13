# CAMERA-6186 Connection Report Mechanism Refactoring 測試案例 (Review Only)

## 📋 測試概述

**Ticket**: CAMERA-6186  
**功能**: Connection Report Mechanism Refactoring - 優化現有的 Connection Report 離線資訊頁面，讓離線資訊能真正幫助用戶獲得排除問題的資訊  
**Fix Versions**: 2026.3.0  
**建立日期**: 2026-01-20  
**負責人**: QA Team - Jessie  
**狀態**: Review Only

> **注意**：本文件為 Review Only 版本，僅包含關鍵測試項目。完整測試案例請參考：`CAMERA-6186_TestCase.md`

---

## 🎯 測試重點與風險評估

### 影響模組/功能
1. **Connection Report 離線資訊頁面** - 高影響
2. **Camera 端離線統計上報機制** - 高影響
3. **Viewer 端版本判斷與顯示** - 中影響
4. **API 整合** - 高影響
5. **即時影像與連線 (Live Feed & Connection)** - 中影響

### 迴歸風險區
1. **現有 Connection Report 功能**：舊版 Camera（cameraHealth = 1）仍使用原本的 WebView 實作
2. **XMPP 連線機制**：XMPP 連線/斷線事件觸發正常
3. **即時影像功能**：即時串流功能正常

---

## 📝 關鍵測試案例 (Review Only)

## 1. 核心功能測試 (Critical Functional Tests)

### 1.1 Camera 端 Logger 機制啟動測試 ⭐ P0
**測試目標**：驗證 Camera 端 Logger 機制在第一次 XMPP 連線成功後正確啟動

**預期結果**：
- Logger 機制在第一次 XMPP 連線成功後正確啟動
- 每 1 小時記錄一次
- 記錄內容包含離線時長統計（offline array，0-23 小時）

---

### 1.2 Camera 端離線時長累計測試 ⭐ P0
**測試目標**：驗證 Camera 端正確累計 `xmpp_disconnect` → `xmpp_connected` 之間的斷線時長

**預期結果**：
- 離線時長正確累計
- 多次斷線的時長正確累計
- 斷線時長記錄在對應的時段（小時）中

---

### 1.3 Camera 端上報機制測試 - Debug 環境 ⭐ P0
**測試目標**：驗證 Debug 環境中上報機制正常運作（每 10 分鐘檢查一次）

**預期結果**：
- Debug 環境每 10 分鐘檢查一次
- 上報條件：必須滿足整點才會上傳
- 上報的 Payload 格式正確，時間切齊整點

---

### 1.4 Camera 端 Cache 管理測試 - 上報成功/失敗 ⭐ P0
**測試目標**：驗證上報成功後 Cache 正確清空，失敗後保留

**預期結果**：
- 上報成功後 Cache 正確清空
- 上報失敗後 Cache 正確保留
- 下次上報時包含之前保留的資料

---

### 1.5 iOS App 退到背景處理測試 ⭐ P1
**測試目標**：驗證 iOS App 退到背景時正確丟棄資料

**預期結果**：
- iOS App 退到背景時 Cache 正確丟棄（尚未上報的資料）
- App 回到前景時重新開始記錄（startTime 重新設定）

---

### 1.6 使用者登出處理測試 ⭐ P1
**測試目標**：驗證使用者登出時 Cache 正確清空

**預期結果**：
- 使用者登出時 Cache 正確清空
- 重新登入後重新開始記錄（startTime 重新設定）

---

## 2. Viewer 端顯示測試 (Viewer Display Tests)

### 2.1 Viewer 端版本判斷測試 - 舊版 Camera (cameraHealth = 1) ⭐ P0
**測試目標**：驗證 Viewer 端正確判斷舊版 Camera 並顯示舊版 WebView

**預期結果**：
- Viewer 端正確判斷舊版 Camera（cameraHealth = 1）
- 開啟舊版 WebView（`stats/offline.html`）
- 舊版 WebView 內容正常顯示

---

### 2.2 Viewer 端版本判斷測試 - 新版 Camera (cameraHealth = 2) ⭐ P0
**測試目標**：驗證 Viewer 端正確判斷新版 Camera 並顯示新版 Native UI

**預期結果**：
- Viewer 端正確判斷新版 Camera（cameraHealth = 2）
- 開啟新版 Native UI（而非 WebView）
- 新版 UI 內容正常顯示

---

### 2.3 Viewer 端時間軸顏色標示測試 ⭐ P0
**測試目標**：驗證 Viewer 端正確顯示時間軸顏色標示

**預期結果**：
- 離線 0-5 秒的時段顯示為綠色
- 離線 6-1440 秒的時段顯示為黃色
- 離線 >1441 秒的時段顯示為紅色
- 無資料的時段（null）顯示為灰色
- 時段標示正確

---

### 2.4 Viewer 端時區轉換測試 ⭐ P1
**測試目標**：驗證 Viewer 端正確處理時區轉換（UTC 儲存，顯示時轉換為使用者時區）

**預期結果**：
- Viewer 端正確處理時區轉換
- 時間軸顯示的時間為使用者時區
- 時段對應正確（UTC 與本地時區的轉換）

---

## 3. API 測試 (API Tests)

### 3.1 POST /device/v1/stats API 測試 - 正常上報 ⭐ P0
**測試目標**：驗證 POST `/device/v1/stats` API 正常上報離線統計資料

**預期結果**：
- POST API 正常上報
- Request 格式正確（Header：Authorization: Bearer KV_TOKEN；Body：start_time, end_time, offline array）
- Response 格式正確，Status Code 為 201，包含 status_code: "succeeded"

---

### 3.2 GET /device/v1/stats/:jid API 測試 - 正常查詢 ⭐ P0
**測試目標**：驗證 GET `/device/v1/stats/:jid` API 正常查詢離線統計資料

**預期結果**：
- GET API 正常查詢
- Request 格式正確（Header：Authorization: Bearer KV_TOKEN；URL：jid URL encode；Query Params：start_date, end_date, timezone）
- Response 格式正確，Status Code 為 200，包含 status_code: "succeeded"、data.offline_stats array

---

### 3.3 GET /device/v1/stats/:jid API 測試 - 日期範圍查詢 ⭐ P1
**測試目標**：驗證 GET API 正確處理日期範圍查詢

**預期結果**：
- API 正確處理日期範圍查詢
- 單日查詢（start_date = end_date）返回 1 個物件
- 多日查詢返回對應數量的物件

---

## 4. 邊緣案例測試 (Edge Cases)

### 4.1 短暫斷線進位測試 ⭐ P1
**測試目標**：驗證斷線時間小於 1 秒時，無條件進位到 1 秒上報

**預期結果**：
- 斷線時間小於 1 秒時，無條件進位到 1 秒上報
- 上報的 Payload 中對應時段顯示 1 秒（而非 0 秒）

---

### 4.2 超長斷線測試（跨多個小時） ⭐ P1
**測試目標**：驗證超長斷線（跨多個小時）時，離線時長正確累計和上報

**預期結果**：
- 超長斷線時，離線時長正確累計到對應的時段
- 上報的 Payload 包含所有受影響的時段
- 每個時段的離線時長計算正確

---

### 4.3 跨日上報測試 ⭐ P1
**測試目標**：驗證跨日時上報機制正常運作

**預期結果**：
- 跨日時上報機制正常運作
- 上報的 Payload 日期正確（前一天的 23:00:00 至當天的 00:00:00）
- 跨日後的資料正確記錄和上報

---

## 5. 迴歸測試 (Regression Tests)

### 5.1 舊版 Camera 顯示測試 ⭐ P0
**測試目標**：驗證舊版 Camera（cameraHealth = 1）仍正常顯示舊版 WebView

**預期結果**：
- 舊版 Camera 仍正常顯示舊版 WebView（`stats/offline.html`）
- 舊版 WebView 功能正常
- 舊版 WebView 內容正常顯示

---

### 5.2 XMPP 連線功能測試 ⭐ P0
**測試目標**：驗證 XMPP 連線功能不受影響

**預期結果**：
- XMPP 連線功能正常
- XMPP 斷線和恢復正常
- Camera 狀態顯示正確

---

### 5.3 即時影像功能測試 ⭐ P0
**測試目標**：驗證即時影像功能不受影響

**預期結果**：
- 即時影像功能正常
- 即時影像延遲在合理範圍內
- 即時影像中斷和恢復正常

---

## 6. 整合測試 (Integration Tests)

### 6.1 端到端測試 - 完整流程 ⭐ P0
**測試目標**：驗證從 Camera 端上報到 Viewer 端顯示的完整流程

**預期結果**：
- 完整流程正常運作
- Camera 端上報成功
- Viewer 端正確顯示資料
- 時間軸顏色標示正確（如：10 分鐘 = 600 秒，介於 6-1440 秒，應顯示為黃色）
- 時區轉換正確

---

## 測試優先級說明

- **⭐ P0**：必須測試的核心功能，影響主要功能運作
- **⭐ P1**：重要功能，影響使用者體驗或邊緣案例處理

---

## 附錄

### A. 測試環境
- **Dev 環境**：https://api.my-alfred-dev.com/
- **Pre-prod 環境**：https://api.my-alfred-pre.com/
- **Prod 環境**：https://api.my-alfred.com/

### B. 相關文件
- **完整測試案例**：`CAMERA-6186_TestCase.md`
- **API 規格**：[Connection Report API v2 (WIP)](https://alfredlabs.atlassian.net/wiki/spaces/PD/pages/4583030786/Connection+Report+API+v2+WIP)
- **Tech Spec**：[Camera 離線報告優化 Tech Spec](https://alfredlabs.atlassian.net/wiki/spaces/MOB/pages/4598628353/Camera+Tech+Spec)
- **設計文件**：[Camera Health Offline Dashboard Redesign](https://www.figma.com/file/0XjlIeVcUWlnASWCcYJoYW?node-id=12006%3A3428)

---

**測試案例版本**：v1.0 (Review Only)  
**最後更新日期**：2026-01-20  
**負責人**：QA Team - Jessie
