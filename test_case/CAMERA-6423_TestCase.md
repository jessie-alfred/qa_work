# CAMERA-6423 [Embedded/SW Camera] Upload Connection Report Data 測試案例

## 📋 測試概述

**Ticket**: CAMERA-6306, CAMERA-6307, CAMERA-6423   
**Parent Epic**: [CAMERA-6186](https://alfredlabs.atlassian.net/browse/CAMERA-6186) - Connection Report Mechanism Refactoring  
**技術規格文件**: 
- [Connection Report API v2 (WIP)](https://alfredlabs.atlassian.net/wiki/spaces/PD/pages/4583030786/Connection+Report+API+v2+WIP)
- [Camera 離線報告優化 Tech Spec](https://alfredlabs.atlassian.net/wiki/spaces/MOB/pages/4598628353/Camera+Tech+Spec)
**Fix Versions**: 
Embedded/SW Camera - AC101 1.20.0, AC201 1.20.0, AC202 1.20.0 
iOS - 2026.3.0 
Android - 2026.3.0
**建立日期**：2026-01-20  
**負責人**：QA Team - Jessie  
**狀態**：Testing

**產品專有名詞參考**：本測試案例中使用的專有名詞請參考 [Terminology Table v2](https://alfredlabs.atlassian.net/wiki/spaces/~590960658/pages/3834085744/Terminology+Table+v2)

### 變更重點
本專案為 Embedded/SW Camera 端 Connection Report 資料上傳實作，主要包含：
1. **CameraStats 模組重寫**：
   - 從複雜的多功能統計系統簡化為專注於連線狀態報告
   - 移除複雜的動態偵測和 WiFi 統計追蹤
   - 簡化統計邏輯，僅保留離線時間和 SD 卡錯誤追蹤

2. **API 端點變更**：
   - 將 `UploadOfflineStats` 替換為 `UploadDeviceStats`
   - 使用新的 `/device/v1/stats` 端點
   - 資料格式變更：從舊的離線統計格式改為新的 device stats 格式

3. **整合介面更新**：
   - 更新 `Core`、`MediaRecorder`、`EventFileHandler` 等模組的呼叫介面
   - `NotifySdCardError` 和 `ResetSdCardError` 介面變更
   - `HasNetworkIssue()` 和 `HasSdCardIssue()` 方法變更

4. **移除功能**：
   - 移除 WiFi 狀態的週期性檢查
   - 移除動態偵測統計
   - 移除 `ToIsoDateTime` 和 `IsDirectoryExist` 等工具函式
   - 移除 `camera_stats_test.cc` 及相關測試建構配置

### 核心變更
1. **統計邏輯簡化**：
   - 從多維度統計改為單純的離線時間追蹤
   - 移除 WiFi 統計和動態偵測追蹤
   - 保留 SD 卡錯誤處理

2. **API 整合**：
   - 新的 `/device/v1/stats` API 端點
   - 新的 Payload 格式（start_time, end_time, offline array）

3. **健康狀態檢查**：
   - `HasNetworkIssue()` 方法邏輯變更
   - `HasSdCardIssue()` 方法邏輯變更

---

## 🎯 測試重點與風險評估

### 影響模組/功能
1. **CameraStats 模組** - 高影響
   - 核心統計模組重寫
   - 連線狀態監控邏輯變更
   - SD 卡錯誤處理機制變更

2. **API 客戶端整合** - 高影響
   - API 端點變更（`UploadOfflineStats` → `UploadDeviceStats`）
   - 新的 `/device/v1/stats` 端點整合
   - Payload 格式變更

3. **即時影像與連線 (Live Feed & Connection)** - 中影響
   - 連線狀態監控邏輯變更（影響即時串流的穩定性判斷）
   - `HasNetworkIssue()` 方法變更

4. **錄影及回放 (Video Recording & Playback)** - 中影響
   - SD 卡錯誤處理機制變更（`NotifySdCardError`、`ResetSdCardError`）
   - `HasSdCardIssue()` 方法變更
   - 影響錄影失敗的偵測和恢復機制

5. **事件偵測與通知 (Motion Detection & Push Notification)** - 中影響
   - 健康狀態檢查邏輯變更（`HasNetworkIssue()`、`HasSdCardIssue()`）
   - 影響事件偵測的可靠性和通知的準確性

6. **整合模組** - 中影響
   - `Core`、`MediaRecorder`、`EventFileHandler` 等模組的呼叫介面更新

### 迴歸風險區
1. **即時影像功能**：
   - 即時串流功能正常
   - 連線狀態監控邏輯變更可能影響即時串流的穩定性判斷

2. **錄影功能**：
   - 錄影功能正常
   - SD 卡錯誤處理邏輯簡化可能影響錄影失敗的偵測和恢復機制

3. **事件偵測功能**：
   - 事件偵測功能正常
   - 健康狀態檢查邏輯簡化可能影響事件偵測的可靠性和通知的準確性


### 具體測試場景建議（含邊緣案例）
1. **連線狀態轉換測試**：
   - 驗證 online/offline 狀態轉換的準確性和即時性
   - 驗證 XMPP 連線狀態監聽正確

2. **SD 卡錯誤處理測試**：
   - 確保 SD 卡 fatal 錯誤和一般錯誤的正確分類和處理
   - 驗證 `NotifySdCardError` 和 `ResetSdCardError` 介面正常運作

3. **API 上傳功能測試**：
   - 驗證新的 `/device/v1/stats` 端點的資料格式和上傳成功率
   - 驗證 Payload 格式正確（start_time, end_time, offline array）

4. **健康狀態檢查測試**：
   - 確保 `HasNetworkIssue()` 和 `HasSdCardIssue()` 方法的判斷邏輯正確

5. **長時間運行測試**：
   - 驗證連線報告的週期性上傳和資料累積的穩定性


7. **向下相容性測試**：
   - 確保與舊版系統的相容性（如有）

---

## 📝 測試案例

## 1. 功能與業務邏輯測試 (Functional & Business Logic)

### 1.1 Embedded/SW Camera 端連線狀態監控測試 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端正確監控 XMPP 連線狀態（online/offline 轉換）

**前置條件**：
- Embedded/SW Camera 裝置（AC101/AC201/AC202）已安裝新版本韌體（1.20.0）
- Embedded/SW Camera 裝置已配對並登入
- 網路連線正常
- XMPP 連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 XMPP 連線狀態為 online
2. 透過 Viewer 端或 API 監控 Embedded/SW Camera 裝置的連線狀態
3. 模擬網路中斷（如：關閉路由器或切斷網路連線）
4. 觀察 Embedded/SW Camera 端是否正確偵測到 offline 狀態
5. 恢復網路連線
6. 觀察 Embedded/SW Camera 端是否正確偵測到 online 狀態
7. 檢查連線狀態轉換的即時性（應在數秒內完成狀態轉換）
8. 驗證連線狀態記錄是否正確

**預期結果**：
- Embedded/SW Camera 端正確監聽 XMPP 連線狀態轉換
- online/offline 狀態轉換準確且即時（數秒內完成）
- 連線狀態記錄正確

---

### 1.2 Embedded/SW Camera 端離線時長累計測試 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端正確累計離線時長

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- XMPP 連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 XMPP 連線狀態為 online
2. 記錄當前時間（T1，範例：`2026-01-20T13:30:00Z`）
3. 模擬網路中斷（如：關閉路由器）
4. 等待 5 分鐘（實際斷線時間：5 分鐘 = 300 秒）
5. 記錄斷線時間（T2，範例：`2026-01-20T13:30:00Z`）
6. 恢復網路連線
7. 等待 XMPP 重新連線成功
8. 記錄重新連線時間（T3，範例：`2026-01-20T13:35:00Z`）
9. 檢查離線時長是否正確累計：
    - 計算離線時長：T3 - T2 = 5 分鐘 = 300 秒
    - 確認離線時長記錄在對應的時段（13:00-14:00，對應 `offline[13]`）
    - 確認 `offline[13]` 為 300
10. 重複步驟 2-9，模擬第二次斷線（等待 3 分鐘 = 180 秒）
    - 斷線時間：14:10-14:13（對應 14:00-15:00 時段，`offline[14]`）
11. 檢查累計的離線時長是否正確：
    - 第一次斷線：`offline[13]` = 300 秒
    - 第二次斷線：`offline[14]` = 180 秒
    - 確認兩次斷線時長分別記錄在對應的時段中
12. 驗證離線時長記錄在對應的時段（小時）中：
    - 13:00-14:00 時段的斷線記錄在 `offline[13]`
    - 14:00-15:00 時段的斷線記錄在 `offline[14]`

**預期結果**：
- 離線時長正確累計
- 多次斷線的時長正確累計
- 離線時長記錄在對應的時段（小時）中

---

### 1.3 Embedded/SW Camera 端 API 上傳測試 - 正常上報 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端正確上傳 Connection Report 資料到新的 `/device/v1/stats` API

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- Embedded/SW Camera 裝置已累計離線時長資料
- 網路連線正常
- API 服務正常運作

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置已累計離線時長資料
2. 等待上報時機（開始 Logger + 1 hour，且必須滿足整點）
3. 使用網路封包監控工具（如：Wireshark、mitmproxy）監控 API 請求
4. 確認 Embedded/SW Camera 端呼叫的 API 端點為 `POST /device/v1/stats`（而非舊的 `UploadOfflineStats`）
5. 檢查 Request Body 格式：
   - 確認包含 `start_time`（UTC ISO DateTime 格式，帶 `Z` 後綴，範例：`2026-01-21T02:54:34Z`）
   - 確認 `start_time` 為 app 啟動連上線的實際時間（非整點）
   - 確認 `start_time` 為 UTC 時間（無論 Embedded/SW Camera 裝置本地時區為何，都必須轉換為 UTC）
   - 確認包含 `end_time`（UTC ISO DateTime 格式，帶 `Z` 後綴，範例：`2026-01-21T03:00:00Z`）
   - 確認 `end_time` 為切齊整點的時間
   - 確認 `end_time` 為 UTC 時間（無論 Embedded/SW Camera 裝置本地時區為何，都必須轉換為 UTC）
   - 確認包含 `offline` array（24 個元素，對應 0-23 小時，單位為秒）
   - 範例 Payload：
     ```json
     {
       "start_time": "2026-01-21T02:54:34Z",
       "end_time": "2026-01-21T03:00:00Z",
       "offline": [0]
     }
     ```
     - `start_time`: app 啟動連上線的實際時間（2026-01-21 02:54:34 UTC，非整點）
     - `end_time`: 切齊整點的時間（2026-01-21 03:00:00 UTC）
7. 檢查 Response：
   - Status Code 為 201（Created）
   - Response Body 格式正確（如：`{"status_code": "succeeded"}`）
8. 驗證上傳成功率（應為 100%）

**預期結果**：
- Embedded/SW Camera 端正確呼叫新的 `/device/v1/stats` API（而非舊的 `UploadOfflineStats`）
- Request 格式正確（start_time, end_time, offline array）
- `start_time` 和 `end_time` 都必須是 UTC 格式（帶 `Z` 後綴）
- Response 格式正確，Status Code 為 201
- 上傳成功率正常

---

### 1.4 Embedded/SW Camera 端 API 上傳測試 - Payload 格式 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端上傳的 Payload 格式符合 API 規格

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- Embedded/SW Camera 裝置已累計離線時長資料
- 網路連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置已累計離線時長資料
2. 等待上報時機
3. 使用網路封包監控工具擷取 API 請求 Payload
4. 檢查 Payload 結構：
   - 確認包含 `start_time` 欄位
   - 確認 `start_time` 為 UTC ISO DateTime 格式（範例：`2026-01-21T02:54:34Z`）
   - 確認 `start_time` 格式符合 ISO 8601 標準（`YYYY-MM-DDTHH:mm:ssZ`）
   - 確認 `start_time` 為 app 啟動連上線的實際時間（非整點，如：`2026-01-21T02:54:34Z`）
   - 確認包含 `end_time` 欄位
   - 確認 `end_time` 為 UTC ISO DateTime 格式（範例：`2026-01-21T03:00:00Z`）
   - 確認 `end_time` 格式符合 ISO 8601 標準
   - 確認 `end_time` 為切齊整點的時間（如：`2026-01-21T03:00:00Z`）
   - 確認包含 `offline` array
   - 確認 `offline` array 長度為 24（對應 0-23 小時）
   - 確認 `offline` array 每個元素為整數（離線時長，單位為秒）
5. 檢查時間格式和時區：
   - 確認 `start_time` 為 UTC 格式（帶 `Z` 後綴）
   - 確認 `start_time` 為 app 啟動連上線的實際時間（非整點）
   - 確認 `end_time` 為 UTC 格式（帶 `Z` 後綴）
   - 確認 `end_time` 為切齊整點的時間
   - 範例 Payload：
     ```json
     {
       "start_time": "2026-01-21T02:54:34Z",
       "end_time": "2026-01-21T03:00:00Z",
       "offline": [0]
     }
     ```
     - `start_time`: app 啟動連上線的實際時間（2026-01-21 02:54:34 UTC）
     - `end_time`: 切齊整點的時間（2026-01-21 03:00:00 UTC）
6. 檢查 `offline` array 內容：
   - 確認每個元素為非負整數（離線時長，單位為秒，範圍：0 到 3600）
   - 確認 `offline[0]` 對應 00:00-01:00 時段
   - 確認 `offline[13]` 對應 13:00-14:00 時段
   - 確認 `offline[23]` 對應 23:00-24:00 時段
   - 驗證對應時段的離線時長正確（如：在 13:30-13:35 斷線 5 分鐘，則 `offline[13]` 應為 300）
7. 檢查特殊規則：
   - 確認斷線時間小於 1 秒時，無條件進位到 1 秒（如：0.5 秒 → 1 秒）
   - 確認無離線時段的值為 0

**預期結果**：
- Payload 包含 `start_time`（app 啟動連上線的實際時間，UTC ISO DateTime 格式，帶 `Z` 後綴，非整點）
- Payload 包含 `end_time`（切齊整點的時間，UTC ISO DateTime 格式，帶 `Z` 後綴）
- Payload 包含 `offline` array（24 小時的離線時長，單位為秒）
- `start_time` 和 `end_time` 都必須是 UTC 時間（無論本地時區為何）
- 時間格式符合 ISO 8601 標準（`YYYY-MM-DDTHH:mm:ssZ`）

---

### 1.5 Embedded/SW Camera 端時區轉換測試 - UTC 格式驗證 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端正確將本地時間轉換為 UTC 格式（帶 Z 後綴）

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- Embedded/SW Camera 裝置已累計離線時長資料
- 網路連線正常
- 可設定或確認 Embedded/SW Camera 裝置的時區設定

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置的時區設定（如：UTC+8、UTC-5 等）
2. 記錄 Embedded/SW Camera 裝置的本地時間（如：2026-01-21 10:54:34 UTC+8）
3. 等待上報時機
4. 使用網路封包監控工具擷取 API 請求 Payload
5. 檢查 `start_time` 格式：
   - 確認 `start_time` 為 UTC ISO DateTime 格式（範例：`2026-01-21T02:54:34Z`）
   - 確認 `start_time` 格式符合 ISO 8601 標準（`YYYY-MM-DDTHH:mm:ssZ`）
   - 確認 `start_time` 以 `Z` 結尾（表示 UTC 時區）
   - 確認 `start_time` 為 app 啟動連上線的實際時間（非整點）
   - 驗證時區轉換正確：
     - 如果 Embedded/SW Camera 裝置時區為 UTC+8，本地時間 `2026-01-21 10:54:34` 應轉換為 UTC `2026-01-21T02:54:34Z`
     - 如果 Embedded/SW Camera 裝置時區為 UTC-5，本地時間 `2026-01-21 10:54:34` 應轉換為 UTC `2026-01-21T15:54:34Z`
6. 檢查 `end_time` 格式：
   - 確認 `end_time` 為 UTC ISO DateTime 格式（範例：`2026-01-21T03:00:00Z`）
   - 確認 `end_time` 格式符合 ISO 8601 標準（`YYYY-MM-DDTHH:mm:ssZ`）
   - 確認 `end_time` 以 `Z` 結尾（表示 UTC 時區）
   - 確認 `end_time` 為切齊整點的時間（如：`03:00:00`、`04:00:00`、`05:00:00` 等）
   - 驗證時區轉換正確（與 `start_time` 使用相同的時區轉換規則）
7. 驗證時間格式範例：
   - 範例 Payload：
     ```json
     {
       "start_time": "2026-01-21T02:54:34Z",
       "end_time": "2026-01-21T03:00:00Z",
       "offline": [0]
     }
     ```
   - 確認 `start_time` 為 app 啟動連上線的實際時間（非整點，如：`02:54:34`）
   - 確認 `end_time` 為切齊整點的時間（如：`03:00:00`）
   - 確認 `start_time` 和 `end_time` 都是 UTC 時間（帶 `Z` 後綴）
   - 確認時間格式正確（無時區偏移符號，如：`+08:00` 或 `-05:00`）
8. 測試不同時區設定：
   - 設定 Embedded/SW Camera 裝置時區為 UTC+8，驗證轉換正確
   - 設定 Embedded/SW Camera 裝置時區為 UTC-5，驗證轉換正確
   - 設定 Embedded/SW Camera 裝置時區為 UTC+0，驗證轉換正確（應與本地時間相同）
9. 驗證跨日轉換：
   - 如果本地時間為 `2026-01-21 23:54:34 UTC+8`，應轉換為 UTC `2026-01-21T15:54:34Z`
   - 如果本地時間為 `2026-01-22 00:54:34 UTC+8`，應轉換為 UTC `2026-01-21T16:54:34Z`（跨日）

**預期結果**：
- `start_time` 為 app 啟動連上線的實際時間（非整點），且必須是 UTC 格式（帶 `Z` 後綴）
- `end_time` 為切齊整點的時間，且必須是 UTC 格式（帶 `Z` 後綴）
- 時區轉換正確（本地時間正確轉換為 UTC 時間）
- 時間格式符合 ISO 8601 標準（`YYYY-MM-DDTHH:mm:ssZ`）
- 無時區偏移符號（如：`+08:00` 或 `-05:00`）

---

### 1.6 Embedded/SW Camera 端上報時機測試 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端在正確的時機上報 Connection Report 資料

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- Embedded/SW Camera 裝置已累計離線時長資料
- 網路連線正常

**測試步驟**：
1. 在 13:35 啟動 Embedded/SW Camera 裝置，開始 Logger（設定 startTime = 13:35）
2. 等待上報檢查時機（開始 Logger + 1 hour = 14:35）
3. 在 14:35 檢查是否嘗試上報
   - 預期：✅ 上傳 13:00~14:00 的資料（因為已滿足整點條件）
4. 檢查上報的 Payload：
   - `start_time` 為 app 啟動連上線的實際時間（如：`2026-01-20T13:35:00Z`，非整點，UTC 時間）
   - `end_time` 為 `2026-01-20T14:00:00Z`（切齊整點，UTC 時間）
   - `offline` array 包含 13:00-14:00 時段的離線時長（對應 `offline[13]`）
5. 在 14:00 啟動另一個 Embedded/SW Camera 裝置，開始 Logger（設定 startTime = 14:00）
6. 等待上報檢查時機（開始 Logger + 1 hour = 15:00）
7. 在 15:00 檢查是否嘗試上報
   - 預期：✅ 上傳 14:00~15:00 的資料（因為已滿足整點條件）
8. 檢查上報的 Payload：
   - `start_time` 為 app 啟動連上線的實際時間（如：`2026-01-20T14:00:00Z`，UTC 時間）
   - `end_time` 為 `2026-01-20T15:00:00Z`（切齊整點，UTC 時間）
   - `offline` array 包含 14:00-15:00 時段的離線時長（對應 `offline[14]`）
9. 驗證上報頻率：
   - Debug 環境：每 10 分鐘檢查一次（如：14:35, 14:45, 14:55, 15:05...）
   - Production 環境：每 60 分鐘檢查一次（如：14:35, 15:35, 16:35...）
10. 驗證上報條件：
    - 必須滿足整點才會上傳（如：14:00, 15:00, 16:00...）
    - 非整點時不上傳（如：14:35, 14:45, 14:55...）

**預期結果**：
- 上報時機符合規格（開始 Logger + 1 hour）
- 上報條件：必須滿足整點才會上傳
- 上報頻率正常（Debug 環境每 10 分鐘檢查，Production 每 60 分鐘檢查）

---

### 1.7 Embedded/SW Camera 端 Cache 管理測試 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端正確管理 Cache（上報成功清空、失敗保留）

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- Embedded/SW Camera 裝置已累計離線時長資料
- 網路連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置已累計離線時長資料（Cache 中有資料）
   - 範例 Cache 資料：`{start_time: "2026-01-20T13:35:00Z", offline: [0,0,0,0,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0,0,0,0]}`
   - 註：`start_time` 為 app 啟動連上線的實際時間（非整點）
2. 等待上報時機
3. 確認網路連線正常
4. 執行上報
5. 檢查上報是否成功：
   - Status Code 為 201（Created）
   - Response Body：`{"status_code": "succeeded"}`
6. 檢查 Cache 是否已清空（應為空或重置）
7. 重新累計離線時長資料（Cache 中有新資料）
   - 範例新 Cache 資料：`{start_time: "2026-01-20T14:15:00Z", offline: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,180,0,0,0,0,0,0,0,0,0]}`
   - 註：`start_time` 為 app 啟動連上線的實際時間（非整點）
8. 等待下次上報時機
9. 模擬網路異常（如：關閉路由器）
10. 執行上報（應失敗）
    - Status Code：網路錯誤或 500/503
11. 檢查 Cache 是否保留（應包含之前的資料）
    - 確認 Cache 中的 `offline[14]` 仍為 180
12. 恢復網路連線
13. 等待下次上報時機
14. 執行上報（應成功）
15. 檢查上報的 Payload 是否包含之前保留的資料：
    - 確認 `offline[14]` 為 180（之前保留的資料）
    - 確認 Payload 包含完整的 24 小時資料

**預期結果**：
- 上報成功後 Cache 正確清空
- 上報失敗後 Cache 正確保留
- 下次上報時包含之前保留的資料

---

## 2. SD 卡錯誤處理測試 (SD Card Error Handling)

### 2.1 SD 卡 Fatal 錯誤處理測試 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端正確處理 SD 卡 Fatal 錯誤

**前置條件**：
- Embedded/SW Camera 裝置已安裝 SD 卡
- Embedded/SW Camera 裝置正常運作

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 SD 卡正常運作
2. 模擬 SD 卡 Fatal 錯誤（如：移除 SD 卡、損壞 SD 卡檔案系統）
3. 觀察 Embedded/SW Camera 端是否正確偵測到 SD 卡 Fatal 錯誤
4. 檢查 `NotifySdCardError` 介面是否正常運作（應被呼叫）
5. 檢查 `HasSdCardIssue()` 方法是否正確返回 true
6. 檢查錯誤分類是否正確（應分類為 Fatal 錯誤）
7. 檢查錯誤處理機制是否正常運作（如：停止錄影、顯示錯誤訊息）

**預期結果**：
- `NotifySdCardError` 介面正常運作
- SD 卡 Fatal 錯誤正確分類和處理
- `HasSdCardIssue()` 方法正確判斷 Fatal 錯誤

---

### 2.2 SD 卡一般錯誤處理測試 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端正確處理 SD 卡一般錯誤

**前置條件**：
- Embedded/SW Camera 裝置已安裝 SD 卡
- Embedded/SW Camera 裝置正常運作

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 SD 卡正常運作
2. 模擬 SD 卡一般錯誤（如：SD 卡空間不足、寫入速度慢）
3. 觀察 Embedded/SW Camera 端是否正確偵測到 SD 卡一般錯誤
4. 檢查錯誤分類是否正確（應分類為一般錯誤，而非 Fatal 錯誤）
5. 檢查 `HasSdCardIssue()` 方法是否正確返回 true
6. 檢查錯誤處理機制是否正常運作（如：降級錄影品質、顯示警告訊息）
7. 檢查 `ResetSdCardError` 介面是否正常運作（當錯誤恢復時）

**預期結果**：
- SD 卡一般錯誤正確分類和處理
- `ResetSdCardError` 介面正常運作
- `HasSdCardIssue()` 方法正確判斷一般錯誤

---

### 2.3 SD 卡錯誤恢復測試 ⭐ P1
**測試目標**：驗證 Embedded/SW Camera 端正確處理 SD 卡錯誤恢復

**前置條件**：
- Embedded/SW Camera 裝置已發生 SD 卡錯誤
- `HasSdCardIssue()` 方法返回 true

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 SD 卡錯誤狀態（`HasSdCardIssue()` 返回 true）
2. 修復 SD 卡錯誤（如：重新插入 SD 卡、格式化 SD 卡、清理 SD 卡空間）
3. 觀察 Embedded/SW Camera 端是否正確偵測到 SD 卡錯誤恢復
4. 檢查 `ResetSdCardError` 介面是否正常運作（應被呼叫）
5. 檢查 `HasSdCardIssue()` 方法是否正確返回 false
6. 檢查錄影功能是否正常運作（應能正常錄影）
7. 驗證錄影品質是否恢復正常

**預期結果**：
- SD 卡錯誤恢復後，`HasSdCardIssue()` 方法正確返回 false
- 錄影功能在錯誤恢復後正常運作

---

## 3. 健康狀態檢查測試 (Health Status Check)

### 3.1 HasNetworkIssue() 方法測試 ⭐ P0
**測試目標**：驗證 `HasNetworkIssue()` 方法判斷邏輯正確

**前置條件**：
- Embedded/SW Camera 裝置正常運作
- 網路連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置網路連線正常
2. 檢查 `HasNetworkIssue()` 方法返回值（應為 false）
3. 模擬網路異常（如：關閉路由器、切斷網路連線）
4. 等待數秒，讓 Embedded/SW Camera 端偵測到網路異常
5. 檢查 `HasNetworkIssue()` 方法返回值（應為 true）
6. 恢復網路連線
7. 等待數秒，讓 Embedded/SW Camera 端偵測到網路恢復
8. 檢查 `HasNetworkIssue()` 方法返回值（應為 false）
9. 驗證判斷邏輯的即時性（應在數秒內完成狀態轉換）

**預期結果**：
- 網路正常時，`HasNetworkIssue()` 返回 false
- 網路異常時，`HasNetworkIssue()` 返回 true
- 判斷邏輯準確且即時

---

### 3.2 HasSdCardIssue() 方法測試 ⭐ P0
**測試目標**：驗證 `HasSdCardIssue()` 方法判斷邏輯正確

**前置條件**：
- Embedded/SW Camera 裝置已安裝 SD 卡
- Embedded/SW Camera 裝置正常運作

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 SD 卡正常運作
2. 檢查 `HasSdCardIssue()` 方法返回值（應為 false）
3. 模擬 SD 卡異常（如：移除 SD 卡、損壞 SD 卡檔案系統）
4. 等待數秒，讓 Embedded/SW Camera 端偵測到 SD 卡異常
5. 檢查 `HasSdCardIssue()` 方法返回值（應為 true）
6. 修復 SD 卡異常（如：重新插入 SD 卡）
7. 等待數秒，讓 Embedded/SW Camera 端偵測到 SD 卡恢復
8. 檢查 `HasSdCardIssue()` 方法返回值（應為 false）
9. 驗證判斷邏輯的即時性（應在數秒內完成狀態轉換）

**預期結果**：
- SD 卡正常時，`HasSdCardIssue()` 返回 false
- SD 卡異常時，`HasSdCardIssue()` 返回 true
- 判斷邏輯準確且即時

---

## 4. 迴歸測試 (Regression Tests)

### 4.1 即時影像功能測試 ⭐ P0
**測試目標**：驗證即時影像功能不受影響

**前置條件**：
- Embedded/SW Camera 裝置已配對
- Viewer 端設備（iOS/Android）
- 網路連線正常

**測試步驟**：
1. 在 Viewer 端開啟即時影像
2. 確認即時影像正常顯示
3. 觀察即時影像延遲（應在合理範圍內，如：小於 2 秒）
4. 模擬網路中斷
5. 觀察即時影像是否正確中斷
6. 恢復網路連線
7. 觀察即時影像是否正確恢復
8. 驗證連線狀態監控邏輯變更不影響即時串流的穩定性判斷

**預期結果**：
- 即時影像功能正常
- 即時影像延遲在合理範圍內
- 連線狀態監控邏輯變更不影響即時串流的穩定性判斷

---

### 4.2 錄影功能測試 ⭐ P0
**測試目標**：驗證錄影功能不受影響

**前置條件**：
- Embedded/SW Camera 裝置已安裝 SD 卡
- Embedded/SW Camera 裝置正常運作

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 SD 卡正常運作
2. 觸發事件錄影（如：移動偵測）
3. 確認錄影功能正常運作
4. 檢查錄影檔案是否正確儲存到 SD 卡
5. 檢查錄影品質是否正常
6. 模擬 SD 卡錯誤（如：移除 SD 卡）
7. 觸發事件錄影
8. 檢查錄影失敗的偵測機制是否正常運作
9. 修復 SD 卡錯誤
10. 觸發事件錄影
11. 檢查錄影恢復機制是否正常運作
12. 驗證 SD 卡錯誤處理邏輯簡化不影響錄影失敗的偵測和恢復機制

**預期結果**：
- 錄影功能正常
- SD 卡錯誤處理邏輯簡化不影響錄影失敗的偵測和恢復機制
- 錄影品質正常

---

### 4.3 事件偵測功能測試 ⭐ P0
**測試目標**：驗證事件偵測功能不受影響

**前置條件**：
- Embedded/SW Camera 裝置正常運作
- 移動偵測功能已啟用

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置移動偵測功能已啟用
2. 在相機前移動（觸發移動偵測）
3. 確認事件偵測功能正常運作
4. 確認事件通知正常發送
5. 模擬網路異常
6. 在相機前移動（觸發移動偵測）
7. 檢查事件偵測是否正常運作（應能正常偵測，但通知可能延遲）
8. 恢復網路連線
9. 在相機前移動（觸發移動偵測）
10. 確認事件偵測和通知功能正常運作
11. 驗證健康狀態檢查邏輯簡化不影響事件偵測的可靠性和通知的準確性

**預期結果**：
- 事件偵測功能正常
- 健康狀態檢查邏輯簡化不影響事件偵測的可靠性和通知的準確性
- 事件通知正常

---

## 5. 穩定性測試 (Stability Tests)

### 5.1 長時間運行測試 ⭐ P1
**測試目標**：驗證 Embedded/SW Camera 端長時間運行時，Connection Report 上報機制穩定

**前置條件**：
- Embedded/SW Camera 裝置正常運作
- 網路連線正常

**測試步驟**：
1. 啟動 Embedded/SW Camera 裝置，開始連線狀態監控
2. 讓 Embedded/SW Camera 裝置持續運行 24 小時
3. 定期檢查（每 1 小時）：
   - 連線報告的週期性上傳是否正常運作
   - 資料累積的穩定性是否正常
   - 系統是否穩定（無崩潰或異常）
4. 檢查系統日誌，確認無錯誤或警告訊息

**預期結果**：
- 連線報告的週期性上傳正常運作
- 資料累積的穩定性正常
- 無崩潰或異常

---

## 6. API 整合測試 (API Integration Tests)

### 6.1 API 端點變更測試 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端使用新的 API 端點（`/device/v1/stats`）

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- Embedded/SW Camera 裝置已累計離線時長資料
- 網路連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置已累計離線時長資料
2. 等待上報時機
3. 使用網路封包監控工具監控 API 請求
4. 確認 Embedded/SW Camera 端呼叫的 API 端點為 `/device/v1/stats`
5. 確認 Embedded/SW Camera 端不再使用舊的 `UploadOfflineStats` API
6. 確認 Embedded/SW Camera 端正確使用新的 `UploadDeviceStats` API
7. 驗證 API 呼叫成功（Status Code 為 201）

**預期結果**：
- Embedded/SW Camera 端不再使用舊的 `UploadOfflineStats` API
- Embedded/SW Camera 端正確使用新的 `UploadDeviceStats` API（`/device/v1/stats` 端點）
- API 呼叫成功

---

### 6.2 API 錯誤處理測試 ⭐ P1
**測試目標**：驗證 Embedded/SW Camera 端正確處理 API 錯誤情況

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- Embedded/SW Camera 裝置已累計離線時長資料

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置已累計離線時長資料（Cache 中有資料）
   - 範例 Cache 資料：`{start_time: "2026-01-20T13:35:00Z", offline: [0,0,0,0,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0,0,0,0]}`
   - 註：`start_time` 為 app 啟動連上線的實際時間（非整點）
2. 等待上報時機
3. 模擬網路異常（如：關閉路由器）
4. 執行上報（應失敗）
   - Status Code：網路錯誤（如：Connection timeout、Network unreachable）
   - 或 HTTP 錯誤（如：503 Service Unavailable）
5. 檢查 Cache 是否保留（應包含之前的資料）
   - 確認 Cache 中的 `offline[13]` 仍為 300
6. 恢復網路連線
7. 等待下次上報時機
8. 執行上報（應成功）
   - Status Code 為 201
9. 檢查上報的 Payload 是否包含之前保留的資料：
   - 確認 `offline[13]` 為 300（之前保留的資料）
   - 確認 Payload 包含完整的 24 小時資料
10. 模擬 API 返回錯誤（如：500 Internal Server Error）
    - 使用 API Mock 工具或修改 API 回應
    - Status Code：500
    - Response Body：`{"error": "Internal Server Error"}`
11. 檢查 Embedded/SW Camera 端是否正確處理錯誤：
    - 確認錯誤被正確記錄
    - 確認不會導致系統崩潰
12. 檢查 Cache 是否保留：
    - 確認 Cache 中的資料未丟失
    - 確認下次上報時會重試

**預期結果**：
- API 錯誤時（如：網路異常、API 返回錯誤），Embedded/SW Camera 端正確處理
- 上報失敗後 Cache 保留
- 下次上報時包含之前保留的資料

---

## 7. 邊緣案例測試 (Edge Cases)

### 7.1 短暫斷線進位測試 ⭐ P1
**測試目標**：驗證斷線時間小於 1 秒時，無條件進位到 1 秒上報

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- 網路連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 XMPP 連線狀態為 online
2. 模擬極短暫的網路中斷（如：快速切換 Wi-Fi、短暫的網路抖動）
3. 確保斷線時間小於 1 秒（如：0.5 秒）
   - 記錄斷線開始時間：T1（範例：`2026-01-20T13:30:00.000Z`）
   - 記錄斷線結束時間：T2（範例：`2026-01-20T13:30:00.500Z`）
   - 實際斷線時長：0.5 秒
4. 恢復網路連線
5. 等待 XMPP 重新連線成功
6. 等待上報時機（如：14:00）
7. 檢查上報的 Payload 中對應時段的離線時長：
   - 確認 `offline[13]`（13:00-14:00 時段）的值
8. 驗證離線時長是否為 1 秒（而非 0 秒或實際的 0.5 秒）：
   - 預期：`offline[13]` = 1（無條件進位規則）
   - 不應為：`offline[13]` = 0 或 0.5

**預期結果**：
- 斷線時間小於 1 秒時，無條件進位到 1 秒上報
- 上報的 Payload 中對應時段顯示 1 秒（而非 0 秒）

---

### 7.2 超長斷線測試（跨多個小時） ⭐ P1
**測試目標**：驗證超長斷線（跨多個小時）時，離線時長正確累計和上報

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- 網路連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置 XMPP 連線狀態為 online
2. 記錄當前時間（T1，範例：`2026-01-20T13:30:00Z`）
3. 模擬網路中斷（如：關閉路由器）
4. 等待 2.5 小時（跨越多個小時：13:30 → 16:00）
   - 斷線時間：13:30-16:00（共 2.5 小時 = 9000 秒）
5. 恢復網路連線
6. 等待 XMPP 重新連線成功
7. 記錄重新連線時間（T2，範例：`2026-01-20T16:00:00Z`）
8. 等待上報時機（如：17:00）
9. 檢查上報的 Payload：
   - 確認包含所有受影響的時段（13:00-14:00, 14:00-15:00, 15:00-16:00）
   - 確認每個時段的離線時長計算正確：
     - `offline[13]`（13:00-14:00）：30 分鐘 = 1800 秒
     - `offline[14]`（14:00-15:00）：60 分鐘 = 3600 秒
     - `offline[15]`（15:00-16:00）：60 分鐘 = 3600 秒
   - 驗證總離線時長：1800 + 3600 + 3600 = 9000 秒（正確）
   - 範例 Payload：
     ```json
     {
       "start_time": "2026-01-20T13:00:00Z",
       "end_time": "2026-01-20T17:00:00Z",
       "offline": [0,0,0,0,0,0,0,0,0,0,0,0,0,1800,3600,3600,0,0,0,0,0,0,0,0]
     }
     ```

**預期結果**：
- 超長斷線時，離線時長正確累計到對應的時段
- 上報的 Payload 包含所有受影響的時段
- 每個時段的離線時長計算正確

---

### 7.3 跨日上報測試 ⭐ P1
**測試目標**：驗證跨日時上報機制正常運作

**前置條件**：
- Embedded/SW Camera 裝置已啟動連線狀態監控
- Embedded/SW Camera 裝置已累計離線時長資料
- 網路連線正常

**測試步驟**：
1. 在 23:30 啟動 Embedded/SW Camera 裝置，開始 Logger（設定 startTime = `2026-01-20T23:30:00Z`）
2. 累計離線時長資料（23:30-24:00，對應 `offline[23]`）
   - 範例：在 23:35-23:40 斷線 5 分鐘，`offline[23]` = 300
3. 等待上報時機（開始 Logger + 1 hour = 00:30，且必須滿足整點）
4. 在 00:30 檢查是否嘗試上報
   - 預期：✅ 上傳前一天的 23:00~24:00 的資料
5. 檢查上報的 Payload：
   - `start_time` 為 app 啟動連上線的實際時間（如：`2026-01-20T23:30:00Z`，非整點，UTC 時間）
   - `end_time` 為當天的 `2026-01-21T00:00:00Z`（切齊整點，跨日）
   - `offline` array 包含對應時段的離線時長（`offline[23]` = 300）
   - 範例 Payload：
     ```json
     {
       "start_time": "2026-01-20T23:30:00Z",
       "end_time": "2026-01-21T00:00:00Z",
       "offline": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,300]
     }
     ```
6. 繼續累計當天的離線時長資料（00:00-01:00，對應 `offline[0]`）
   - 範例：在 00:10-00:15 斷線 5 分鐘，`offline[0]` = 300
7. 等待下次上報時機（01:30）
8. 在 01:30 檢查是否嘗試上報
   - 預期：✅ 上傳當天的 00:00~01:00 的資料
9. 檢查上報的 Payload：
   - `start_time` 為 app 啟動連上線的實際時間（如：`2026-01-20T23:30:00Z`，非整點，UTC 時間）
   - 註：如果 app 在 23:30 啟動，則 `start_time` 為 `2026-01-20T23:30:00Z`（非整點）
   - `end_time` 為當天的 `2026-01-21T01:00:00Z`
   - `offline` array 包含對應時段的離線時長（`offline[0]` = 300）
   - 範例 Payload：
     ```json
     {
       "start_time": "2026-01-21T00:00:00Z",
       "end_time": "2026-01-21T01:00:00Z",
       "offline": [300,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
     }
     ```
10. 驗證跨日後的資料正確記錄和上報：
    - 前一天的資料（23:00-24:00）正確上報
    - 當天的資料（00:00-01:00）正確上報
    - 日期轉換正確（UTC 時間）

**預期結果**：
- 跨日時上報機制正常運作
- 上報的 Payload 日期正確（前一天的 23:00:00 至當天的 00:00:00）
- 跨日後的資料正確記錄和上報

---

## 8. 裝置相容性測試 (Device Compatibility)

### 8.1 AC101 裝置測試 ⭐ P0
**測試目標**：驗證 AC101 裝置上 Connection Report 功能正常運作

**前置條件**：
- AC101 裝置已安裝新版本韌體（1.20.0）
- AC101 裝置已配對並登入
- 網路連線正常

**測試步驟**：
1. 確認 AC101 裝置正常運作
2. 啟動連線狀態監控
3. 驗證連線狀態監控正常運作
4. 累計離線時長資料
5. 等待上報時機
6. 驗證 API 上傳正常運作
7. 模擬 SD 卡錯誤
8. 驗證 SD 卡錯誤處理正常運作
9. 驗證即時影像功能正常
10. 驗證錄影功能正常
11. 驗證事件偵測功能正常

**預期結果**：
- AC101 裝置上連線狀態監控正常
- AC101 裝置上 API 上傳正常
- AC101 裝置上 SD 卡錯誤處理正常

---

### 8.2 AC201 裝置測試 ⭐ P0
**測試目標**：驗證 AC201 裝置上 Connection Report 功能正常運作

**前置條件**：
- AC201 裝置已安裝新版本韌體（1.20.0）
- AC201 裝置已配對並登入
- 網路連線正常

**測試步驟**：
1. 確認 AC201 裝置正常運作
2. 啟動連線狀態監控
3. 驗證連線狀態監控正常運作
4. 累計離線時長資料
5. 等待上報時機
6. 驗證 API 上傳正常運作
7. 模擬 SD 卡錯誤
8. 驗證 SD 卡錯誤處理正常運作
9. 驗證即時影像功能正常
10. 驗證錄影功能正常
11. 驗證事件偵測功能正常

**預期結果**：
- AC201 裝置上連線狀態監控正常
- AC201 裝置上 API 上傳正常
- AC201 裝置上 SD 卡錯誤處理正常

---

### 8.3 AC202 裝置測試 ⭐ P0
**測試目標**：驗證 AC202 裝置上 Connection Report 功能正常運作

**前置條件**：
- AC202 裝置已安裝新版本韌體（1.20.0）
- AC202 裝置已配對並登入
- 網路連線正常

**測試步驟**：
1. 確認 AC202 裝置正常運作
2. 啟動連線狀態監控
3. 驗證連線狀態監控正常運作
4. 累計離線時長資料
5. 等待上報時機
6. 驗證 API 上傳正常運作
7. 模擬 SD 卡錯誤
8. 驗證 SD 卡錯誤處理正常運作
9. 驗證即時影像功能正常
10. 驗證錄影功能正常
11. 驗證事件偵測功能正常

**預期結果**：
- AC202 裝置上連線狀態監控正常
- AC202 裝置上 API 上傳正常
- AC202 裝置上 SD 卡錯誤處理正常

---

## 9. HW Camera 數據清空測試 (HW Camera Data Clear Tests)

### 9.1 HW Camera 數據清空測試 - Reboot ⭐ P0
**測試目標**：驗證 HW Camera 在 Reboot（重開機）後，connection offline 資料被清空

**前置條件**：
- HW Camera 裝置（AC101/AC201/AC202）已配對並登入
- HW Camera 裝置已啟動連線狀態監控
- HW Camera 裝置已累計離線時長資料（Cache 中有資料）
- 網路連線正常

**測試步驟**：
1. 確認 HW Camera 裝置正常運作
2. 啟動連線狀態監控
3. 累計離線時長資料：
   - 在 13:30-13:35 模擬斷線 5 分鐘（300 秒）
   - 確認離線時長記錄在 Cache 中（如：`{start_time: "2026-01-20T13:35:00Z", offline: [0,0,0,0,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0,0,0,0]}`）
4. 確認 Cache 中有資料（未上報）
5. 執行 Reboot（重開機）：
   - 方法 1：透過系統設定執行重開機
   - 方法 2：透過硬體按鈕執行重開機
   - 方法 3：透過 API 或遠端控制執行重開機
6. 等待 HW Camera 裝置重開機完成並重新連線
7. 檢查 Cache 是否已清空：
   - 確認 Cache 中無 connection offline 資料
   - 確認 Cache 為空或重置為初始狀態
8. 重新啟動連線狀態監控
9. 驗證重新開始累計離線時長資料（從重開機後的時間開始）

**預期結果**：
- Reboot 後，connection offline 資料被清空
- Cache 中無之前的離線時長資料
- 重新開始累計離線時長資料

---

### 9.2 HW Camera 數據清空測試 - 登出 ⭐ P0
**測試目標**：驗證 HW Camera 在登出後，connection offline 資料被清空

**前置條件**：
- HW Camera 裝置（AC101/AC201/AC202）已配對並登入
- HW Camera 裝置已啟動連線狀態監控
- HW Camera 裝置已累計離線時長資料（Cache 中有資料）
- 網路連線正常

**測試步驟**：
1. 確認 HW Camera 裝置正常運作
2. 啟動連線狀態監控
3. 累計離線時長資料：
   - 在 13:30-13:35 模擬斷線 5 分鐘（300 秒）
   - 確認離線時長記錄在 Cache 中（如：`{start_time: "2026-01-20T13:35:00Z", offline: [0,0,0,0,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0,0,0,0]}`）
4. 確認 Cache 中有資料（未上報）
5. 執行登出操作：
   - 方法 1：透過 Viewer 端 App 執行登出
   - 方法 2：透過系統設定執行登出
   - 方法 3：透過 API 執行登出
6. 等待登出完成
7. 檢查 Cache 是否已清空：
   - 確認 Cache 中無 connection offline 資料
   - 確認 Cache 為空或重置為初始狀態
8. 重新登入並啟動連線狀態監控
9. 驗證重新開始累計離線時長資料（從登入後的時間開始）

**預期結果**：
- 登出後，connection offline 資料被清空
- Cache 中無之前的離線時長資料
- 重新登入後，重新開始累計離線時長資料

---

### 9.3 HW Camera 數據清空測試 - Crash ⭐ P0
**測試目標**：驗證 HW Camera 在 Crash（崩潰）後重開機，connection offline 資料被清空

**前置條件**：
- HW Camera 裝置（AC101/AC201/AC202）已配對並登入
- HW Camera 裝置已啟動連線狀態監控
- HW Camera 裝置已累計離線時長資料（Cache 中有資料）
- 網路連線正常
- 可模擬 Crash 情境

**測試步驟**：
1. 確認 HW Camera 裝置正常運作
2. 啟動連線狀態監控
3. 累計離線時長資料：
   - 在 13:30-13:35 模擬斷線 5 分鐘（300 秒）
   - 確認離線時長記錄在 Cache 中（如：`{start_time: "2026-01-20T13:35:00Z", offline: [0,0,0,0,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0,0,0,0]}`）
4. 確認 Cache 中有資料（未上報）
5. 模擬 Crash 情境：
   - 方法 1：強制終止 App 進程（如：kill -9）
   - 方法 2：模擬記憶體不足導致崩潰
   - 方法 3：模擬系統異常導致崩潰
6. 確認 HW Camera 裝置已崩潰（無回應或自動重開機）
7. 等待 HW Camera 裝置自動重開機完成並重新連線（或手動重開機）
8. 檢查 Cache 是否已清空：
   - 確認 Cache 中無 connection offline 資料
   - 確認 Cache 為空或重置為初始狀態
9. 重新啟動連線狀態監控
10. 驗證重新開始累計離線時長資料（從重開機後的時間開始）

**預期結果**：
- Crash 後重開機，connection offline 資料被清空
- Cache 中無之前的離線時長資料
- 重新開始累計離線時長資料

---

### 9.4 HW Camera 數據清空測試 - 更新版本 Reboot ⭐ P0
**測試目標**：驗證 HW Camera 在更新版本後 Reboot，connection offline 資料被清空

**前置條件**：
- HW Camera 裝置（AC101/AC201/AC202）已配對並登入
- HW Camera 裝置已啟動連線狀態監控
- HW Camera 裝置已累計離線時長資料（Cache 中有資料）
- 網路連線正常
- 有新版本韌體可供更新

**測試步驟**：
1. 確認 HW Camera 裝置正常運作（當前版本，如：1.19.0）
2. 啟動連線狀態監控
3. 累計離線時長資料：
   - 在 13:30-13:35 模擬斷線 5 分鐘（300 秒）
   - 確認離線時長記錄在 Cache 中（如：`{start_time: "2026-01-20T13:35:00Z", offline: [0,0,0,0,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0,0,0,0]}`）
4. 確認 Cache 中有資料（未上報）
5. 執行韌體更新：
   - 方法 1：透過 Viewer 端 App 執行 OTA 更新
   - 方法 2：透過系統設定執行韌體更新
   - 方法 3：透過 API 執行韌體更新
6. 等待韌體更新完成
7. 確認 HW Camera 裝置自動 Reboot（重開機）
8. 等待 HW Camera 裝置重開機完成並重新連線
9. 確認韌體版本已更新（如：1.20.0）
10. 檢查 Cache 是否已清空：
    - 確認 Cache 中無 connection offline 資料
    - 確認 Cache 為空或重置為初始狀態
11. 重新啟動連線狀態監控
12. 驗證重新開始累計離線時長資料（從重開機後的時間開始）

**預期結果**：
- 更新版本後 Reboot，connection offline 資料被清空
- Cache 中無之前的離線時長資料
- 重新開始累計離線時長資料

---

### 9.5 HW Camera 數據清空測試 - Reset 重新配對 ⭐ P0
**測試目標**：驗證 HW Camera 在 Reset 重新配對後，connection offline 資料被清空

**前置條件**：
- HW Camera 裝置（AC101/AC201/AC202）已配對並登入
- HW Camera 裝置已啟動連線狀態監控
- HW Camera 裝置已累計離線時長資料（Cache 中有資料）
- 網路連線正常

**測試步驟**：
1. 確認 HW Camera 裝置正常運作
2. 啟動連線狀態監控
3. 累計離線時長資料：
   - 在 13:30-13:35 模擬斷線 5 分鐘（300 秒）
   - 確認離線時長記錄在 Cache 中（如：`{start_time: "2026-01-20T13:35:00Z", offline: [0,0,0,0,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0,0,0,0]}`）
4. 確認 Cache 中有資料（未上報）
5. 執行 Reset 操作：
   - 方法 1：透過硬體 Reset 按鈕執行重置
   - 方法 2：透過系統設定執行重置
   - 方法 3：透過 API 執行重置
6. 等待 Reset 完成（裝置會自動重開機）
7. 等待 HW Camera 裝置重開機完成
8. 執行重新配對操作：
   - 透過 Viewer 端 App 重新配對 HW Camera 裝置
   - 確認配對成功
9. 檢查 Cache 是否已清空：
   - 確認 Cache 中無 connection offline 資料
   - 確認 Cache 為空或重置為初始狀態
10. 重新啟動連線狀態監控
11. 驗證重新開始累計離線時長資料（從重新配對後的時間開始）

**預期結果**：
- Reset 重新配對後，connection offline 資料被清空
- Cache 中無之前的離線時長資料
- 重新開始累計離線時長資料

---

## 10. 整合測試 (Integration Tests)

### 10.1 端到端測試 - 完整流程 ⭐ P0
**測試目標**：驗證從 Embedded/SW Camera 端上報到 Viewer 端顯示的完整流程

**前置條件**：
- Embedded/SW Camera 裝置已配對
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常
- API 服務正常運作

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置正常運作
2. 啟動連線狀態監控
3. 累計離線時長資料：
   - 在 13:30-13:35 模擬斷線 5 分鐘（300 秒）
   - 確認離線時長記錄在 `offline[13]` = 300
4. 等待上報時機（開始 Logger + 1 hour，且必須滿足整點，如：14:00）
5. 驗證 Embedded/SW Camera 端上報成功：
   - 確認 API 端點為 `POST /device/v1/stats`
   - 確認 Payload：
     - `start_time`: app 啟動連上線的實際時間（如：`2026-01-20T13:35:00Z`，非整點，UTC 時間）
     - `end_time`: 切齊整點的時間（如：`2026-01-20T14:00:00Z`，UTC 時間）
     - `offline`: `[0,0,0,0,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0,0,0,0]`
   - 確認 Status Code 為 201
6. 在 Viewer 端開啟 Connection Report 頁面
7. 驗證 Viewer 端正確顯示資料：
   - 確認 Viewer 端呼叫 `GET /device/v1/stats/:jid` API
   - 確認 Response 包含 `offline_stats` array
   - 確認 13:00-14:00 時段顯示離線時長 300 秒
8. 驗證資料一致性（Embedded/SW Camera 端上報的資料與 Viewer 端顯示的資料一致）：
   - Embedded/SW Camera 端上報：`offline[13]` = 300
   - Viewer 端顯示：13:00-14:00 時段離線時長 = 300 秒
9. 驗證時間軸顯示正確：
   - 確認時間軸顯示 24 小時（0-23）
   - 確認時區轉換正確（UTC → 使用者時區）
10. 驗證 Timeline slot 顏色標示正確：
    - **null**：該時段無資料，呈現灰色
    - **0~5 秒**：該時段正常，呈現綠色
    - **6~1440 秒**：該時段有 offline 秒數介於 6~1440（24 分鐘），呈現黃色
    - **1441 秒以上**：該時段有 offline 秒數 >= 1441 秒，呈現紅色
    - 範例：300 秒離線應顯示為黃色（300 秒介於 6~1440 秒範圍）

**預期結果**：
- 完整流程正常運作
- Embedded/SW Camera 端上報成功
- Viewer 端正確顯示資料
- 資料一致性正確

---

### 10.2 多台裝置同時上報測試 ⭐ P1
**測試目標**：驗證多台 Embedded/SW Camera 裝置同時上報時，API 和系統穩定

**前置條件**：
- 多台 Embedded/SW Camera 裝置（至少 3 台）已配對
- 所有 Embedded/SW Camera 裝置已啟動連線狀態監控
- 所有 Embedded/SW Camera 裝置已累計離線時長資料
- 網路連線正常

**測試步驟**：
1. 確認所有 Embedded/SW Camera 裝置正常運作（至少 3 台：AC101、AC201、AC202）
2. 同步所有 Embedded/SW Camera 裝置的上報時機（如：都在整點時上報，14:00）
3. 為每台裝置設定不同的離線時長資料：
   - 裝置 1（AC101）：`offline[13]` = 300 秒
   - 裝置 2（AC201）：`offline[13]` = 600 秒
   - 裝置 3（AC202）：`offline[13]` = 900 秒
4. 等待上報時機（14:00）
5. 觀察所有 Embedded/SW Camera 裝置是否同時執行上報
6. 使用網路封包監控工具監控 API 請求：
   - 確認同時收到 3 個 `POST /device/v1/stats` 請求
   - 確認每個請求的 Payload 正確
7. 確認 API 正常處理多台裝置同時上報：
   - 確認所有請求的 Status Code 為 201
   - 確認 API 回應時間正常（< 1 秒）
8. 檢查系統穩定性（無崩潰或異常）：
   - 確認 Embedded/SW Camera 裝置無崩潰
   - 確認 API 服務無異常
9. 檢查每台裝置的上報是否成功：
   - 裝置 1：Status Code 201，Payload 包含 `offline[13]` = 300
   - 裝置 2：Status Code 201，Payload 包含 `offline[13]` = 600
   - 裝置 3：Status Code 201，Payload 包含 `offline[13]` = 900
10. 驗證每台裝置的資料是否正確上報：
    - 確認資料未混淆（每台裝置的資料獨立）
    - 確認資料完整性（24 小時資料完整）

**預期結果**：
- API 正常處理多台裝置同時上報
- 系統穩定，無崩潰或異常
- 每台裝置的上報成功

---

### 10.3 Embedded/SW Camera 端 Camera Capability 發送測試 ⭐ P0
**測試目標**：驗證 Embedded/SW Camera 端正確發送 Camera Capability `camera_health: 2`

**前置條件**：
- Embedded/SW Camera 裝置（AC101/AC201/AC202）已安裝新版本韌體（1.20.0）
- Embedded/SW Camera 裝置已配對並登入
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置正常運作
2. 確認 Embedded/SW Camera 裝置已配對並連線
3. 使用網路封包監控工具（如：Wireshark、mitmproxy）監控 XMPP 或 API 通訊
4. 檢查 Embedded/SW Camera 端發送的 Camera Capability：
   - 確認包含 `camera_health` 欄位
   - 確認 `camera_health` 值為 `2`（新版）
5. 驗證 Camera Capability 發送時機：
   - 確認在配對時發送
   - 確認在連線建立時發送
6. 驗證 Camera Capability 格式正確：
   - 確認格式符合規格（如：JSON 格式或 XMPP capability 格式）

**預期結果**：
- Embedded/SW Camera 端正確發送 Camera Capability `camera_health: 2`
- Camera Capability 發送時機正確
- Camera Capability 格式正確

---

### 10.4 Viewer 端 Camera Capability 判斷測試 - 舊版 Camera (camera_health = 1) ⭐ P0
**測試目標**：驗證 Viewer 端正確判斷舊版 Camera（`camera_health = 1`）並顯示舊版 WebView 頁面

**前置條件**：
- 舊版 Embedded/SW Camera 裝置（`camera_health = 1`）已配對
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常

**測試步驟**：
1. 確認舊版 Embedded/SW Camera 裝置正常運作（`camera_health = 1`）
2. 在 Viewer 端開啟 Connection Report 頁面
3. 檢查 Viewer 端是否正確讀取 Camera Capability：
   - 確認 Viewer 端取得 `camera_health = 1`
4. 驗證 Viewer 端顯示方式：
   - 確認 Viewer 端開啟舊版 WebView 頁面（`stats/offline.html`）
   - 確認未開啟新版離線報告 UI
5. 驗證舊版 WebView 頁面正常運作：
   - 確認頁面正常載入
   - 確認離線資訊正常顯示

**預期結果**：
- Viewer 端正確判斷舊版 Camera（`camera_health = 1`）
- Viewer 端開啟舊版 WebView 頁面（`stats/offline.html`）
- 舊版 WebView 頁面正常運作

---

### 10.5 Viewer 端 Camera Capability 判斷測試 - 新版 Camera (camera_health = 2) ⭐ P0
**測試目標**：驗證 Viewer 端正確判斷新版 Camera（`camera_health = 2`）並開啟新版離線報告 UI

**前置條件**：
- 新版 Embedded/SW Camera 裝置（`camera_health = 2`）已配對
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常
- Embedded/SW Camera 端已有上報的離線統計資料

**測試步驟**：
1. 確認新版 Embedded/SW Camera 裝置正常運作（`camera_health = 2`）
2. 確認 Embedded/SW Camera 端已上報離線統計資料
3. 在 Viewer 端開啟 Connection Report 頁面
4. 檢查 Viewer 端是否正確讀取 Camera Capability：
   - 確認 Viewer 端取得 `camera_health = 2`
5. 驗證 Viewer 端顯示方式：
   - 確認 Viewer 端開啟新版離線報告 UI（Native UI）
   - 確認未開啟舊版 WebView 頁面
6. 驗證新版離線報告 UI 正常運作：
   - 確認頁面正常載入
   - 確認離線資訊正常顯示
   - 確認時間軸顯示正確
   - 確認 Timeline slot 顏色標示正確

**預期結果**：
- Viewer 端正確判斷新版 Camera（`camera_health = 2`）
- Viewer 端開啟新版離線報告 UI（Native UI）
- 新版離線報告 UI 正常運作

---

### 10.6 Viewer 端 Camera Capability 預設行為測試 ⭐ P1
**測試目標**：驗證 Viewer 端無法取得 Camera Capability `camera_health` 值時，預設行為當作 `camera_health = 2`

**前置條件**：
- Embedded/SW Camera 裝置已配對（但無法取得 `camera_health` 值）
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置正常運作
2. 模擬無法取得 Camera Capability `camera_health` 值的情況：
   - 方法 1：模擬 XMPP 連線異常，導致無法取得 capability
   - 方法 2：模擬 API 回應中缺少 `camera_health` 欄位
   - 方法 3：模擬 `camera_health` 值為 `null` 或 `undefined`
3. 在 Viewer 端開啟 Connection Report 頁面
4. 檢查 Viewer 端預設行為：
   - 確認 Viewer 端將 `camera_health` 預設為 `2`（新版）
   - 確認 Viewer 端開啟新版離線報告 UI（Native UI）
   - 確認未開啟舊版 WebView 頁面
5. 驗證新版離線報告 UI 正常運作：
   - 確認頁面正常載入
   - 確認功能正常運作（即使無法取得 `camera_health` 值）

**預期結果**：
- Viewer 端無法取得 `camera_health` 值時，預設行為當作 `camera_health = 2`
- Viewer 端開啟新版離線報告 UI（Native UI）
- 新版離線報告 UI 正常運作

---

### 10.7 Viewer 端 Amplitude 事件測試 - 從 camera_settings 入口 ⭐ P1
**測試目標**：驗證 Viewer 端從 `camera_settings` 入口點擊 Connection Report 時，正確上傳 Amplitude 事件

**前置條件**：
- Embedded/SW Camera 裝置已配對
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常
- Amplitude Analytics 服務正常運作
- 可監控 Amplitude 事件（如：使用 Amplitude Dashboard 或 API）

**測試步驟**：
1. 確認 Embedded/SW Camera 裝置正常運作
2. 確認 Viewer 端 App 已登入並連線到 Camera 裝置
3. 開啟 Amplitude 事件監控工具（如：Amplitude Dashboard、API 監控、或開發者工具）
4. 在 Viewer 端 App 中，從 `camera_settings` 入口點擊 Connection Report：
   - 進入 Camera Settings 頁面，點擊 Connection Stability 選項
5. 確認 Connection Report 頁面正常開啟
6. 檢查 Amplitude 事件是否正確上傳：
   - 確認事件名稱（Event Name）為 `"pageview: connection stability"`
   - 確認事件屬性（Event Properties）包含：
     - Key: `"from"`
     - Value: `"camera_settings"`
7. 驗證事件上傳時機：
   - 確認事件在點擊入口時立即上傳（而非頁面載入完成後）
   - 確認事件只上傳一次（不重複上傳）
8. 驗證事件格式正確：
   - 確認事件名稱格式正確（無拼寫錯誤）
   - 確認事件屬性 key 和 value 格式正確
   - 確認事件包含必要的使用者識別資訊（如：User ID、Device ID）

**預期結果**：
- 從 `camera_settings` 入口點擊 Connection Report 時，正確上傳 Amplitude 事件
- 事件名稱：`"pageview: connection stability"`
- 事件屬性：`{"from": "camera_settings"}`
- 事件上傳時機正確（點擊時立即上傳）

---

### 10.8 Viewer 端 Amplitude 事件測試 - 從 camera_health 入口 ⭐ P1
**測試目標**：驗證 Viewer 端從 `camera_health` 入口點擊 Connection Report 時，正確上傳 Amplitude 事件

**前置條件**：
- Camera 裝置已配對
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常
- Amplitude Analytics 服務正常運作
- 可監控 Amplitude 事件（如：使用 Amplitude Dashboard 或 API）

**測試步驟**：
1. 確認 Camera 裝置正常運作
2. 確認 Viewer 端 App 已登入並連線到 Camera 裝置
3. 開啟 Amplitude 事件監控工具（如：Amplitude Dashboard、API 監控、或開發者工具）
4. 在 Viewer 端 App 中，從 `camera_health` 入口點擊 Connection Report：
   - 從 Camera List 點擊 Check 進入 Camera Health 頁面，點擊 Connection Stability 選項
5. 確認 Connection Report 頁面正常開啟
6. 檢查 Amplitude 事件是否正確上傳：
   - 確認事件名稱（Event Name）為 `"pageview: connection stability"`
   - 確認事件屬性（Event Properties）包含：
     - Key: `"from"`
     - Value: `"camera_health"`
7. 驗證事件上傳時機：
   - 確認事件在點擊入口時立即上傳（而非頁面載入完成後）
   - 確認事件只上傳一次（不重複上傳）
8. 驗證事件格式正確：
   - 確認事件名稱格式正確（無拼寫錯誤）
   - 確認事件屬性 key 和 value 格式正確
   - 確認事件包含必要的使用者識別資訊（如：User ID、Device ID）
9. 驗證兩個入口的事件屬性不同：
   - 從 `camera_settings` 入口：`{"from": "camera_settings"}`
   - 從 `camera_health` 入口：`{"from": "camera_health"}`

**預期結果**：
- 從 `camera_health` 入口點擊 Connection Report 時，正確上傳 Amplitude 事件
- 事件名稱：`"pageview: connection stability"`
- 事件屬性：`{"from": "camera_health"}`
- 事件上傳時機正確（點擊時立即上傳）
- 兩個入口的事件屬性正確區分

---

### 10.9 Viewer 端 Connection Stability 頁面 UI 測試 ⭐ P0
**測試目標**：驗證 Viewer 端 Connection Stability 頁面 UI 符合 Figma 設計規格

**前置條件**：
- Camera 裝置已配對
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常
- API 服務正常運作
- Embedded/SW Camera 端已有上報的離線統計資料
- 可參考 Figma 設計：[Connection Stability UI](https://www.figma.com/design/0XjlIeVcUWlnASWCcYJoYW/CAMERA-6186--Connection-Report-Mechanism-Refactoring?node-id=12466-5017&t=BPnXfI5YXkK47XW8-0)

**測試步驟**：
1. 確認 Camera 裝置正常運作
2. 確認 Embedded/SW Camera 端已有上報的離線統計資料
3. 在 Viewer 端開啟 Connection Stability 頁面（從 `camera_settings` 或 `camera_health` 入口）
4. 驗證 Header Section（頁面頂部）：
   - 確認左側有 Back Arrow（返回按鈕）
   - 確認中間顯示頁面標題 "Connection Stability"（粗體、置中）
   - 確認右側有 Help Icon（問號圖示，圓形背景）
   - 驗證點擊 Back Arrow 可返回上一頁
   - 驗證點擊 Help Icon 可開啟說明或幫助頁面
5. 驗證 Date Selection Section（日期選擇區）：
   - 確認顯示當前日期（格式：`YYYY/MM/DD (Today)`，如：`2025/12/10 (Today)`）
   - 確認日期下方顯示提示文字："Select dates from the past 7 days to view."
   - 確認右側有 Settings Icon（齒輪圖示）
   - 驗證點擊日期可開啟日期選擇器
   - 驗證日期選擇器僅允許選擇過去 7 天的日期
   - 驗證點擊 Settings Icon 可開啟設定頁面
6. 驗證 24-Hour Connection Status Chart Section（24 小時連線狀態圖表區）：
   - 確認區塊標題顯示 "24-HOUR CONNECTION STATUS"（橘色、大寫）
   - 確認顯示橫向長條圖（24 個時段，對應 0-23 小時）
   - 驗證時間標籤顯示正確：
     - 確認顯示 "00:00"、"06:00"、"12:00"、"18:00" 標籤
     - 確認標籤下方有虛線對齊
   - 驗證顏色標示正確：
     - **null**：該時段無資料，呈現灰色（Gray）
     - **0~5 秒**：該時段正常，呈現綠色（Green），表示 "Stable"（穩定連線）
     - **6~1440 秒**：該時段有 offline 秒數介於 6~1440（24 分鐘），呈現黃色（Orange），表示 "Weak"（弱連線）
     - **1441 秒以上**：該時段有 offline 秒數 >= 1441 秒，呈現紅色（Red），表示 "Disconnected"（斷線）
   - 驗證圖例（Legend）顯示正確：
     - 確認圖例位於圖表下方
     - 確認包含四個顏色方塊和對應文字：
       - 綠色方塊 + "Stable"
       - 橘色方塊 + "Weak"
       - 紅色方塊 + "Disconnected"
       - 灰色方塊 + "No Data"
   - 驗證圖表互動功能：
     - 確認點擊圖表時段可顯示詳細資訊（如：離線時長、時間範圍）
     - 確認圖表可正確顯示 24 小時資料
7. 驗證 Offline Events & Diagnosis Section（離線事件與診斷區）：
   - 確認區塊標題顯示 "Offline events & diagnosis:"
   - 確認顯示診斷原因列表（項目符號列表）：
     - "Unstable Wi-Fi signal"（不穩定的 Wi-Fi 訊號）
     - "Issues with your internet service provider"（網路服務提供者問題）
     - "The app was moved to the background"（App 移至背景）
     - "Connected to a VPN"（連接到 VPN）
     - "Battery optimization is limiting the app"（電池優化限制 App）
     - "Low battery issues"（低電量問題）
     - "Device overheating"（裝置過熱）
   - 驗證列表格式正確（項目符號、文字對齊、間距）
8. 驗證整體 UI 布局：
   - 確認各區塊間距適當
   - 確認文字大小和字體符合設計規格
   - 確認顏色使用符合設計規格
   - 確認在不同螢幕尺寸（手機、平板）上顯示正常
   - 確認在深色模式和淺色模式下顯示正常
9. 驗證資料顯示正確性：
   - 確認圖表顯示的資料與 API 回應的資料一致
   - 確認顏色標示與實際離線時長對應正確
   - 確認時間標籤與時區轉換正確
10. 驗證響應式設計：
    - 確認橫向和縱向顯示都正常
    - 確認在不同裝置尺寸上布局正確
    - 確認文字不會被截斷或重疊

**預期結果**：
- Connection Stability 頁面 UI 完全符合 Figma 設計規格
- 所有 UI 元素（Header、Date Selection、Chart、Legend、Diagnosis）都正確顯示
- 顏色標示正確（Green/Orange/Red/Gray 對應正確的連線狀態）
- 圖表互動功能正常
- 診斷原因列表完整顯示
- 響應式設計正常運作

---

### 10.10 Viewer 端 Firebase ScreenName 事件測試 ⭐ P1
**測試目標**：驗證 Viewer 端開啟 Connection Stability 頁面時，正確上傳 Firebase ScreenName 事件

**前置條件**：
- Camera 裝置已配對
- Viewer 端設備（iOS/Android）已安裝新版本 App
- 網路連線正常
- Firebase Analytics 服務正常運作
- 可監控 Firebase 事件（如：使用 Firebase Console、DebugView、或開發者工具）

**測試步驟**：
1. 確認 Camera 裝置正常運作
2. 確認 Viewer 端 App 已登入並連線到 Camera 裝置
3. 開啟 Firebase 事件監控工具（如：Firebase Console、DebugView、或開發者工具）
4. 在 Viewer 端 App 中，開啟 Connection Stability 頁面：
   - 方法 1：從 `camera_settings` 入口點擊 Connection Stability
   - 方法 2：從 `camera_health` 入口點擊 Connection Stability
5. 確認 Connection Stability 頁面正常開啟
6. 檢查 Firebase ScreenName 事件是否正確上傳：
   - 確認事件名稱（Event Name）為 `"ScreenName"`
   - 確認事件參數（Event Parameters）包含：
     - Screen Name 值為 `"4.6.2 Connection Stability"`
7. 驗證事件上傳時機：
   - 確認事件在頁面載入時立即上傳（而非點擊入口時）
   - 確認事件只上傳一次（不重複上傳）
8. 驗證事件格式正確：
   - 確認事件名稱格式正確（`ScreenName`）
   - 確認 Screen Name 值格式正確（`"4.6.2 Connection Stability"`）
   - 確認事件包含必要的使用者識別資訊（如：User ID、Device ID）
9. 驗證舊版事件已更新：
   - 確認不再使用舊的 ScreenName `"4.6.2 Offline Statistics"`
   - 確認新版本使用 ScreenName `"4.6.2 Connection Stability"`
   - 驗證舊版 App 和新版 App 的 ScreenName 事件不同（如果可測試）
10. 驗證不同入口的事件一致：
    - 從 `camera_settings` 入口：ScreenName 為 `"4.6.2 Connection Stability"`
    - 從 `camera_health` 入口：ScreenName 為 `"4.6.2 Connection Stability"`
    - 確認兩個入口的 ScreenName 事件相同

**預期結果**：
- 開啟 Connection Stability 頁面時，正確上傳 Firebase ScreenName 事件
- 事件名稱：`"ScreenName"`
- Screen Name 值：`"4.6.2 Connection Stability"`
- 事件上傳時機正確（頁面載入時立即上傳）
- 舊版事件 `"4.6.2 Offline Statistics"` 已更新為 `"4.6.2 Connection Stability"`
- 不同入口的 ScreenName 事件一致

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
- **Parent Epic**：[CAMERA-6186](https://alfredlabs.atlassian.net/browse/CAMERA-6186) - Connection Report Mechanism Refactoring
- **API 規格**：[Connection Report API v2 (WIP)](https://alfredlabs.atlassian.net/wiki/spaces/PD/pages/4583030786/Connection+Report+API+v2+WIP)
- **Tech Spec**：[Camera 離線報告優化 Tech Spec](https://alfredlabs.atlassian.net/wiki/spaces/MOB/pages/4598628353/Camera+Tech+Spec)

### C. 影響裝置
- AC101 (Embedded/SW Camera - AC101 1.20.0)
- AC201 (Embedded/SW Camera - AC201 1.20.0)
- AC202 (Embedded/SW Camera - AC202 1.20.0)

---

**測試案例版本**：v1.0  
**最後更新日期**：2026-01-20  
**負責人**：QA Team - Jessie
