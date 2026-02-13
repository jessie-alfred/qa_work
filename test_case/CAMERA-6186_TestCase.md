# CAMERA-6186 Connection Report Mechanism Refactoring 測試案例

## 📋 測試概述

**Ticket**: CAMERA-6186  
**功能**: Connection Report Mechanism Refactoring - 優化現有的 Connection Report 離線資訊頁面，讓離線資訊能真正幫助用戶獲得排除問題的資訊  
**Parent Epic**: CAMERA-6186  
**技術規格文件**: 
- [Connection Report API v2 (WIP)](https://alfredlabs.atlassian.net/wiki/spaces/PD/pages/4583030786/Connection+Report+API+v2+WIP)
- [Camera 離線報告優化 Tech Spec](https://alfredlabs.atlassian.net/wiki/spaces/MOB/pages/4598628353/Camera+Tech+Spec)
**設計文件**: 
- [Camera Health Offline Dashboard Redesign - 20251210 flow](https://www.figma.com/file/0XjlIeVcUWlnASWCcYJoYW?node-id=12006%3A3428)
**Fix Versions**: 2026.3.0  
**建立日期**: 2026-01-20  
**負責人**: QA Team - Jessie  
**狀態**: Testing

**產品專有名詞參考**：本測試案例中使用的專有名詞請參考 [Terminology Table v2](https://alfredlabs.atlassian.net/wiki/spaces/~590960658/pages/3834085744/Terminology+Table+v2)

### 變更重點
本專案為 Connection Report 機制重構，主要包含：
1. **API v2 實作**：
   - 新增 POST `/device/v1/stats` API（上傳裝置離線統計資料）
   - 新增 GET `/device/v1/stats/:jid` API（取得裝置離線統計資料）
   - 資料儲存於 `device_stats` collection，包含 24 小時的離線時長統計

2. **Camera 端（上報端）實作**：
   - Logger 機制：第一次 XMPP 連線成功後開始記錄
   - 每 1 小時記錄一次，累計 `xmpp_disconnect` → `xmpp_connected` 之間的斷線時長
   - 上報時機：開始 Logger + 1 hour（Debug 環境每 10 分鐘檢查，Production 每 60 分鐘檢查）
   - 上報條件：必須滿足整點才會上傳
   - Cache 管理：上報成功清空、上報失敗保留、App 退到背景（iOS）丟棄、使用者登出清空

3. **Viewer 端（顯示端）實作**：
   - 根據 Camera 的 `cameraHealth` capability 值決定顯示方式
   - `cameraHealth = 1`：開啟舊版 WebView `stats/offline.html`
   - `cameraHealth = 2`：開啟新版離線報告 UI

4. **UI 顯示邏輯**：
   - Timeline slot 定義：
     - `null`：該時段無資料，呈現灰色
     - `0-5`：該時段正常（0-5 秒離線），呈現綠色
     - `6-1440`：該時段有 offline 秒數介於 6-1440 秒（1%-40%），呈現黃色
     - `1441+`：該時段有 offline 秒數 > 1441 秒（>40%），呈現紅色

### 核心變更
1. **API 層面**：
   - 新增 device stats 上傳和查詢 API
   - 支援時區轉換（UTC 儲存，顯示時轉換為使用者時區）
   - 支援日期範圍查詢（start_date, end_date）

2. **Camera 端**：
   - 實作離線時長累計機制
   - 實作定時上報機制（Debug/Production 環境不同頻率）
   - 實作 Cache 管理機制（成功/失敗/背景/登出處理）

3. **Viewer 端**：
   - 實作版本判斷邏輯（根據 cameraHealth capability）
   - 實作新版離線報告 UI
   - 實作時區轉換和時間軸顯示

4. **資料格式**：
   - 斷線時間小於 1 秒，無條件進位到 1 秒上報
   - 每個上報時間會切齊整點的資料

---

## 🎯 測試重點與風險評估

### 影響模組/功能
1. **Connection Report 離線資訊頁面** - 高影響
   - 新版 UI 顯示邏輯
   - 時區轉換和時間軸顯示
   - Timeline slot 顏色標示（灰色/綠色/黃色/紅色）

2. **Camera 端離線統計上報機制** - 高影響
   - Logger 機制（XMPP 連線狀態監聽）
   - 離線時長累計機制
   - 定時上報機制（Debug/Production 環境差異）
   - Cache 管理機制（成功/失敗/背景/登出處理）

3. **Viewer 端版本判斷與顯示** - 中影響
   - 根據 `cameraHealth` capability 判斷顯示方式
   - 舊版 WebView 與新版 Native UI 切換

4. **API 整合** - 高影響
   - POST `/device/v1/stats` API 上傳
   - GET `/device/v1/stats/:jid` API 查詢
   - 時區轉換處理
   - 日期範圍查詢

5. **即時影像與連線 (Live Feed & Connection)** - 中影響
   - XMPP 連線狀態監聽（影響 Logger 機制）
   - 連線中斷後的恢復能力（影響離線統計）

### 迴歸風險區
1. **現有 Connection Report 功能**：
   - 舊版 Camera（cameraHealth = 1）仍使用原本的 WebView 實作
   - 需驗證舊版顯示不受影響

2. **XMPP 連線機制**：
   - XMPP 連線/斷線事件觸發正常
   - 連線恢復功能正常

3. **即時影像功能**：
   - 即時串流功能正常
   - 串流體驗不受影響

4. **使用者登入/登出流程**：
   - 登入功能正常
   - 登出時 Cache 清空機制正常

5. **App 生命週期管理**：
   - iOS App 退到背景/回到前景處理正常
   - Android App 生命週期處理正常

### 具體測試場景建議（含邊緣案例）
1. **Logger 機制測試**：
   - 第一次 XMPP 連線成功後開始記錄
   - 每 1 小時記錄一次
   - 斷線時長累計正確性

2. **上報機制測試**：
   - Debug 環境每 10 分鐘檢查，Production 每 60 分鐘檢查
   - 上報條件：必須滿足整點才會上傳
   - 上報失敗後重試機制

3. **Cache 管理測試**：
   - 上報成功後清空 Cache
   - 上報失敗後保留 Cache
   - iOS App 退到背景時丟棄資料
   - 使用者登出時清空 Cache

4. **時區轉換測試**：
   - UTC 儲存，顯示時轉換為使用者時區
   - 跨日資料處理
   - 不同時區使用者顯示正確性

5. **UI 顯示測試**：
   - Timeline slot 顏色標示正確性（灰色/綠色/黃色/紅色）
   - 時段資料顯示正確性
   - 無資料時段顯示（null）

6. **邊緣案例測試**：
   - 短暫斷線（小於 1 秒進位到 1 秒）
   - 超長斷線（跨多個小時）
   - 跨日上報
   - 網路異常時上報處理
   - 多台 Camera 同時上報

---

## 📝 測試案例

## 1. 功能與業務邏輯測試 (Functional & Business Logic)

### 1.1 Camera 端 Logger 機制啟動測試
**測試目標**：驗證 Camera 端 Logger 機制在第一次 XMPP 連線成功後正確啟動

**前置條件**：
- Camera 端設備（iOS/Android）
- Viewer 端設備（iOS/Android）
- 已配對的 Camera 和 Viewer
- 網路連線正常

**測試步驟**：
1. 在 Camera 端登入帳號
2. 確認 XMPP 連線成功（可透過 Viewer 端查看 Camera 狀態為 Online）
3. 檢查 Camera 端 Logger 是否已啟動
4. 等待 1 小時，確認每 1 小時記錄一次
5. 檢查記錄內容是否包含離線時長統計

**預期結果**：
- Logger 機制在第一次 XMPP 連線成功後正確啟動
- 每 1 小時記錄一次
- 記錄內容包含離線時長統計（offline array，0-23 小時）

---

### 1.2 Camera 端離線時長累計測試
**測試目標**：驗證 Camera 端正確累計 `xmpp_disconnect` → `xmpp_connected` 之間的斷線時長

**前置條件**：
- Camera 端設備已啟動 Logger
- XMPP 連線正常

**測試步驟**：
1. 確認 Camera 端 XMPP 連線正常
2. 模擬網路中斷（如：關閉 Wi-Fi 或切換到飛航模式）
3. 等待 5 分鐘
4. 恢復網路連線
5. 確認 XMPP 重新連線成功
6. 檢查離線時長是否正確累計（應約為 5 分鐘 = 300 秒）
7. 重複步驟 2-6，模擬多次斷線
8. 檢查累計的離線時長是否正確（應為多次斷線時長的總和）

**預期結果**：
- 離線時長正確累計
- 多次斷線的時長正確累計
- 斷線時長記錄在對應的時段（小時）中

---

### 1.3 Camera 端上報機制測試 - Debug 環境
**測試目標**：驗證 Debug 環境中上報機制正常運作（每 10 分鐘檢查一次）

**前置條件**：
- Camera 端設備安裝 Debug Build
- Camera 端已啟動 Logger
- 網路連線正常

**測試步驟**：
1. 在 13:35 啟動 App，開啟 Logger（設定 startTime = 13:35）
2. 等待 10 分鐘（13:45），檢查是否嘗試上報
   - 預期：❌ 不上傳（尚未到整點 14:00）
3. 等待 10 分鐘（13:55），檢查是否嘗試上報
   - 預期：❌ 不上傳（尚未到整點 14:00）
4. 等待 10 分鐘（14:05），檢查是否嘗試上報
   - 預期：✅ 上傳 13:00~14:00 的資料
5. 檢查上報的 Payload 是否正確：
   - `start_time` 為 13:00:00（切齊整點）
   - `end_time` 為 14:00:00
   - `offline` array 包含對應時段的離線時長

**預期結果**：
- Debug 環境每 10 分鐘檢查一次
- 上報條件：必須滿足整點才會上傳
- 上報的 Payload 格式正確，時間切齊整點

---

### 1.4 Camera 端上報機制測試 - Production 環境
**測試目標**：驗證 Production 環境中上報機制正常運作（每 60 分鐘檢查一次）

**前置條件**：
- Camera 端設備安裝 Production Build
- Camera 端已啟動 Logger
- 網路連線正常

**測試步驟**：
1. 在 13:35 啟動 App，開啟 Logger（設定 startTime = 13:35）
2. 等待 60 分鐘（14:35），檢查是否嘗試上報
   - 預期：✅ 上傳 13:00~14:00 的資料
3. 檢查上報的 Payload 是否正確：
   - `start_time` 為 13:00:00（切齊整點）
   - `end_time` 為 14:00:00
   - `offline` array 包含對應時段的離線時長

**預期結果**：
- Production 環境每 60 分鐘檢查一次
- 上報條件：必須滿足整點才會上傳
- 上報的 Payload 格式正確，時間切齊整點

---

### 1.5 Camera 端 Cache 管理測試 - 上報成功
**測試目標**：驗證上報成功後 Cache 正確清空

**前置條件**：
- Camera 端設備已啟動 Logger
- 網路連線正常
- 已有累計的離線時長資料

**測試步驟**：
1. 確認 Camera 端已有累計的離線時長資料（Cache）
2. 等待上報時機（Debug 環境：10 分鐘後；Production 環境：60 分鐘後）
3. 確認上報成功（可透過 API 或後台確認）
4. 檢查 Cache 是否已清空
5. 等待下一次記錄時機，確認重新開始累計

**預期結果**：
- 上報成功後 Cache 正確清空
- 下次記錄時重新開始累計

---

### 1.6 Camera 端 Cache 管理測試 - 上報失敗
**測試目標**：驗證上報失敗後 Cache 正確保留

**前置條件**：
- Camera 端設備已啟動 Logger
- 已有累計的離線時長資料
- 可模擬網路異常（如：關閉網路）

**測試步驟**：
1. 確認 Camera 端已有累計的離線時長資料（Cache）
2. 模擬網路異常（關閉網路或切換到無網路環境）
3. 等待上報時機
4. 確認上報失敗（網路異常導致）
5. 檢查 Cache 是否保留
6. 恢復網路連線
7. 等待下一次上報時機
8. 確認上報成功，且包含之前保留的資料

**預期結果**：
- 上報失敗後 Cache 正確保留
- 下次上報時包含之前保留的資料

---

### 1.7 Camera 端 Cache 管理測試 - iOS App 退到背景
**測試目標**：驗證 iOS App 退到背景時正確丟棄資料

**前置條件**：
- iOS Camera 端設備已啟動 Logger
- 已有累計的離線時長資料（尚未上報）

**測試步驟**：
1. 確認 iOS Camera 端已有累計的離線時長資料（Cache）
2. 確認尚未到上報時機
3. 將 App 退到背景（按 Home 鍵或切換 App）
4. 檢查 Cache 是否已丟棄
5. 將 App 回到前景
6. 檢查是否重新開始記錄（startTime 重新設定）

**預期結果**：
- iOS App 退到背景時 Cache 正確丟棄
- App 回到前景時重新開始記錄

---

### 1.8 Camera 端 Cache 管理測試 - 使用者登出
**測試目標**：驗證使用者登出時 Cache 正確清空

**前置條件**：
- Camera 端設備已啟動 Logger
- 已有累計的離線時長資料

**測試步驟**：
1. 確認 Camera 端已有累計的離線時長資料（Cache）
2. 執行使用者登出
3. 檢查 Cache 是否已清空
4. 重新登入
5. 檢查是否重新開始記錄（startTime 重新設定）

**預期結果**：
- 使用者登出時 Cache 正確清空
- 重新登入後重新開始記錄

---

### 1.9 短暫斷線進位測試
**測試目標**：驗證斷線時間小於 1 秒時，無條件進位到 1 秒上報

**前置條件**：
- Camera 端設備已啟動 Logger
- 可模擬短暫斷線（小於 1 秒）

**測試步驟**：
1. 確認 Camera 端 XMPP 連線正常
2. 模擬短暫斷線（小於 1 秒，如：快速切換網路）
3. 確認 XMPP 重新連線成功
4. 等待上報時機
5. 檢查上報的 Payload 中，對應時段的離線時長是否為 1 秒（而非 0 秒）

**預期結果**：
- 斷線時間小於 1 秒時，無條件進位到 1 秒上報
- 上報的 Payload 中對應時段顯示 1 秒

---

### 1.10 超長斷線測試（跨多個小時）
**測試目標**：驗證超長斷線（跨多個小時）時，離線時長正確累計和上報

**前置條件**：
- Camera 端設備已啟動 Logger
- 可模擬長時間斷線（如：5 小時）

**測試步驟**：
1. 在 10:00 確認 Camera 端 XMPP 連線正常
2. 在 10:30 模擬網路中斷
3. 等待 5 小時（15:30）
4. 恢復網路連線，確認 XMPP 重新連線成功
5. 等待上報時機（16:00）
6. 檢查上報的 Payload：
   - `start_time` 為 10:00:00
   - `end_time` 為 16:00:00
   - `offline` array 包含 6 個時段的資料：
     - 10:00~11:00：1800 秒（30 分鐘）
     - 11:00~15:00：每小時 3600 秒（全斷線）× 4
     - 15:00~16:00：1800 秒（30 分鐘）

**預期結果**：
- 超長斷線時，離線時長正確累計到對應的時段
- 上報的 Payload 包含所有受影響的時段
- 每個時段的離線時長計算正確

---

### 1.11 跨日上報測試
**測試目標**：驗證跨日時上報機制正常運作

**前置條件**：
- Camera 端設備已啟動 Logger
- 可在接近午夜時進行測試（如：23:30）

**測試步驟**：
1. 在 23:30 啟動 App，開啟 Logger（設定 startTime = 23:30）
2. 確認 XMPP 連線正常
3. 等待跨日（00:00），確認記錄第一小時（23:00~00:00）
4. 等待上報時機（00:30），確認上報成功
5. 檢查上報的 Payload：
   - `start_time` 為前一天的 23:00:00
   - `end_time` 為當天的 00:00:00
   - `offline` array 包含對應時段的資料
6. 繼續運作，在 00:45 模擬斷線 2 分鐘
7. 等待上報時機（01:30），確認上報成功
8. 檢查上報的 Payload：
   - `start_time` 為當天的 00:30:00
   - `end_time` 為當天的 01:00:00
   - `offline` array 包含 120 秒（2 分鐘）

**預期結果**：
- 跨日時上報機制正常運作
- 上報的 Payload 日期正確
- 跨日後的資料正確記錄和上報

---

### 1.12 Viewer 端版本判斷測試 - 舊版 Camera (cameraHealth = 1)
**測試目標**：驗證 Viewer 端正確判斷舊版 Camera 並顯示舊版 WebView

**前置條件**：
- Viewer 端設備（iOS/Android）
- 舊版 Camera（cameraHealth = 1）
- 已配對的 Camera 和 Viewer

**測試步驟**：
1. 在 Viewer 端登入帳號
2. 進入 Camera 設定頁面
3. 點擊「Connection Report」或「離線報告」
4. 檢查是否開啟舊版 WebView（`stats/offline.html`）
5. 檢查舊版 WebView 內容是否正常顯示

**預期結果**：
- Viewer 端正確判斷舊版 Camera（cameraHealth = 1）
- 開啟舊版 WebView（`stats/offline.html`）
- 舊版 WebView 內容正常顯示

---

### 1.13 Viewer 端版本判斷測試 - 新版 Camera (cameraHealth = 2)
**測試目標**：驗證 Viewer 端正確判斷新版 Camera 並顯示新版 Native UI

**前置條件**：
- Viewer 端設備（iOS/Android）
- 新版 Camera（cameraHealth = 2）
- 已配對的 Camera 和 Viewer
- Camera 端已有上報的離線統計資料

**測試步驟**：
1. 在 Viewer 端登入帳號
2. 進入 Camera 設定頁面
3. 點擊「Connection Report」或「離線報告」
4. 檢查是否開啟新版 Native UI（而非 WebView）
5. 檢查新版 UI 內容是否正常顯示

**預期結果**：
- Viewer 端正確判斷新版 Camera（cameraHealth = 2）
- 開啟新版 Native UI（而非 WebView）
- 新版 UI 內容正常顯示

---

### 1.14 Viewer 端時間軸顯示測試 - 正常時段（綠色）
**測試目標**：驗證 Viewer 端正確顯示正常時段（0-5 秒離線，綠色）

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料（某時段離線 0-5 秒）

**測試步驟**：
1. 在 Viewer 端進入 Connection Report 頁面
2. 檢查時間軸顯示
3. 確認離線 0-5 秒的時段顯示為綠色
4. 檢查時段標示是否正確（小時標示）

**預期結果**：
- 離線 0-5 秒的時段顯示為綠色
- 時段標示正確

---

### 1.15 Viewer 端時間軸顯示測試 - 輕微離線（黃色）
**測試目標**：驗證 Viewer 端正確顯示輕微離線時段（6-1440 秒，黃色）

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料（某時段離線 6-1440 秒）

**測試步驟**：
1. 在 Viewer 端進入 Connection Report 頁面
2. 檢查時間軸顯示
3. 確認離線 6-1440 秒的時段顯示為黃色
4. 檢查時段標示是否正確

**預期結果**：
- 離線 6-1440 秒的時段顯示為黃色
- 時段標示正確

---

### 1.16 Viewer 端時間軸顯示測試 - 嚴重離線（紅色）
**測試目標**：驗證 Viewer 端正確顯示嚴重離線時段（>1441 秒，紅色）

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料（某時段離線 >1441 秒）

**測試步驟**：
1. 在 Viewer 端進入 Connection Report 頁面
2. 檢查時間軸顯示
3. 確認離線 >1441 秒的時段顯示為紅色
4. 檢查時段標示是否正確

**預期結果**：
- 離線 >1441 秒的時段顯示為紅色
- 時段標示正確

---

### 1.17 Viewer 端時間軸顯示測試 - 無資料時段（灰色）
**測試目標**：驗證 Viewer 端正確顯示無資料時段（null，灰色）

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端部分時段有資料，部分時段無資料（null）

**測試步驟**：
1. 在 Viewer 端進入 Connection Report 頁面
2. 檢查時間軸顯示
3. 確認無資料的時段（null）顯示為灰色
4. 檢查時段標示是否正確

**預期結果**：
- 無資料的時段（null）顯示為灰色
- 時段標示正確

---

### 1.18 Viewer 端時區轉換測試
**測試目標**：驗證 Viewer 端正確處理時區轉換（UTC 儲存，顯示時轉換為使用者時區）

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料（UTC 時區）
- Viewer 端設定不同時區（如：Asia/Taipei UTC+8）

**測試步驟**：
1. 在 Viewer 端設定時區為 Asia/Taipei（UTC+8）
2. 進入 Connection Report 頁面
3. 檢查時間軸顯示的時間是否為 Asia/Taipei 時區
4. 檢查時段對應是否正確（UTC 與本地時區的轉換）
5. 切換到其他時區（如：America/New_York UTC-5）
6. 重新進入 Connection Report 頁面
7. 檢查時間軸顯示的時間是否為新時區
8. 檢查時段對應是否正確

**預期結果**：
- Viewer 端正確處理時區轉換
- 時間軸顯示的時間為使用者時區
- 時段對應正確（UTC 與本地時區的轉換）

---

### 1.19 Viewer 端日期範圍查詢測試
**測試目標**：驗證 Viewer 端正確查詢指定日期範圍的離線統計資料

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的多日離線統計資料

**測試步驟**：
1. 在 Viewer 端進入 Connection Report 頁面
2. 選擇日期範圍（如：2025-12-22 至 2025-12-24）
3. 檢查是否正確顯示該日期範圍的資料
4. 切換到其他日期範圍
5. 檢查是否正確顯示新日期範圍的資料
6. 選擇單日範圍（start_date = end_date）
7. 檢查是否正確顯示單日資料

**預期結果**：
- Viewer 端正確查詢指定日期範圍的資料
- 日期範圍切換正常
- 單日查詢正常

---

## 2. API 測試 (API Testing)

### 2.1 POST /device/v1/stats API 測試 - 正常上報
**測試目標**：驗證 POST `/device/v1/stats` API 正常上報離線統計資料

**前置條件**：
- Camera 端設備已啟動 Logger
- 已有累計的離線時長資料
- 網路連線正常
- 有效的 KV_TOKEN

**測試步驟**：
1. 確認 Camera 端已有累計的離線時長資料
2. 等待上報時機
3. 使用 API 工具（如：Postman）或檢查網路請求，確認 POST `/device/v1/stats` API 被呼叫
4. 檢查 Request：
   - Header：`Authorization: Bearer KV_TOKEN`
   - Body：包含 `start_time`、`end_time`、`offline` array
5. 檢查 Response：
   - Status Code：201
   - Response Body：包含 `status_code: "succeeded"`、`data` 物件

**預期結果**：
- POST API 正常上報
- Request 格式正確
- Response 格式正確，Status Code 為 201

---

### 2.2 POST /device/v1/stats API 測試 - 無效 Token
**測試目標**：驗證 POST `/device/v1/stats` API 在無效 Token 時正確處理

**前置條件**：
- 可模擬無效 Token（如：過期 Token、錯誤 Token）

**測試步驟**：
1. 使用無效 Token 呼叫 POST `/device/v1/stats` API
2. 檢查 Response：
   - Status Code：應為 401 或 403
   - Response Body：包含錯誤訊息

**預期結果**：
- API 正確拒絕無效 Token
- Status Code 為 401 或 403
- Response 包含錯誤訊息

---

### 2.3 POST /device/v1/stats API 測試 - 缺少必要參數
**測試目標**：驗證 POST `/device/v1/stats` API 在缺少必要參數時正確處理

**前置條件**：
- 有效的 KV_TOKEN

**測試步驟**：
1. 使用缺少 `start_time` 的 Request 呼叫 POST `/device/v1/stats` API
2. 檢查 Response：
   - Status Code：應為 400
   - Response Body：包含錯誤訊息（如：缺少必要參數）
3. 使用缺少 `end_time` 的 Request 呼叫 API
4. 檢查 Response 是否正確
5. 使用缺少 `offline` 的 Request 呼叫 API
6. 檢查 Response 是否正確

**預期結果**：
- API 正確拒絕缺少必要參數的 Request
- Status Code 為 400
- Response 包含錯誤訊息

---

### 2.4 GET /device/v1/stats/:jid API 測試 - 正常查詢
**測試目標**：驗證 GET `/device/v1/stats/:jid` API 正常查詢離線統計資料

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料
- 有效的 KV_TOKEN
- 正確的 jid（需 URL encode）

**測試步驟**：
1. 在 Viewer 端進入 Connection Report 頁面
2. 使用 API 工具（如：Postman）或檢查網路請求，確認 GET `/device/v1/stats/:jid` API 被呼叫
3. 檢查 Request：
   - Header：`Authorization: Bearer KV_TOKEN`
   - URL：包含正確的 jid（URL encode）
   - Query Params：包含 `start_date`、`end_date`、`timezone`、`details`（可選）
4. 檢查 Response：
   - Status Code：200
   - Response Body：包含 `status_code: "succeeded"`、`data.offline_stats` array

**預期結果**：
- GET API 正常查詢
- Request 格式正確（jid URL encode）
- Response 格式正確，Status Code 為 200
- Response 包含正確的離線統計資料

---

### 2.5 GET /device/v1/stats/:jid API 測試 - 日期範圍查詢
**測試目標**：驗證 GET `/device/v1/stats/:jid` API 正確處理日期範圍查詢

**前置條件**：
- 有效的 KV_TOKEN
- 正確的 jid
- Camera 端已有上報的多日離線統計資料

**測試步驟**：
1. 使用單日範圍（start_date = end_date = 2025-12-22）呼叫 GET API
2. 檢查 Response：
   - `offline_stats` array 包含 1 個物件
   - 物件的 `date` 為 "2025-12-22"
3. 使用多日範圍（start_date = 2025-12-22, end_date = 2025-12-24）呼叫 GET API
4. 檢查 Response：
   - `offline_stats` array 包含 3 個物件
   - 物件的 `date` 分別為 "2025-12-22"、"2025-12-23"、"2025-12-24"

**預期結果**：
- API 正確處理日期範圍查詢
- 單日查詢返回 1 個物件
- 多日查詢返回對應數量的物件

---

### 2.6 GET /device/v1/stats/:jid API 測試 - 時區轉換
**測試目標**：驗證 GET `/device/v1/stats/:jid` API 正確處理時區轉換

**前置條件**：
- 有效的 KV_TOKEN
- 正確的 jid
- Camera 端已有上報的離線統計資料（UTC 時區）

**測試步驟**：
1. 使用 timezone = "Asia/Taipei" 呼叫 GET API
2. 檢查 Response：
   - `offline_stats` array 中物件的 `timezone` 為 "Asia/Taipei"
   - `timeline` 的時間對應為 Asia/Taipei 時區
3. 使用 timezone = "America/New_York" 呼叫 GET API
4. 檢查 Response：
   - `offline_stats` array 中物件的 `timezone` 為 "America/New_York"
   - `timeline` 的時間對應為 America/New_York 時區

**預期結果**：
- API 正確處理時區轉換
- Response 中的 `timezone` 正確
- `timeline` 的時間對應正確

---

### 2.7 GET /device/v1/stats/:jid API 測試 - details 參數
**測試目標**：驗證 GET `/device/v1/stats/:jid` API 正確處理 `details` 參數

**前置條件**：
- 有效的 KV_TOKEN
- 正確的 jid
- Camera 端已有上報的離線統計資料

**測試步驟**：
1. 使用 details = false（或省略）呼叫 GET API
2. 檢查 Response：
   - Response 格式符合規格（不包含額外詳細資訊）
3. 使用 details = true 呼叫 GET API
4. 檢查 Response：
   - Response 格式符合規格（可能包含額外詳細資訊，依 API 規格而定）

**預期結果**：
- API 正確處理 `details` 參數
- `details = false` 時返回基本資料
- `details = true` 時返回詳細資料（依 API 規格而定）

---

### 2.8 GET /device/v1/stats/:jid API 測試 - 無資料
**測試目標**：驗證 GET `/device/v1/stats/:jid` API 在無資料時正確處理

**前置條件**：
- 有效的 KV_TOKEN
- 正確的 jid
- Camera 端尚未上報離線統計資料（或查詢日期範圍無資料）

**測試步驟**：
1. 使用無資料的日期範圍呼叫 GET API
2. 檢查 Response：
   - Status Code：200
   - Response Body：包含 `status_code: "succeeded"`、`data.offline_stats` 為空 array 或包含 null 的 timeline

**預期結果**：
- API 正確處理無資料情況
- Status Code 為 200
- Response 包含空資料或 null timeline

---

## 3. 穩定性與可靠性測試 (Stability & Reliability)

### 3.1 長時間運作測試
**測試目標**：驗證 Camera 端長時間運作時，Logger 機制和上報機制穩定

**前置條件**：
- Camera 端設備
- 網路連線正常

**測試步驟**：
1. 啟動 Camera 端 App，開啟 Logger
2. 讓 App 持續運作 24 小時
3. 期間模擬數次斷線和恢復
4. 檢查 Logger 是否持續正常運作
5. 檢查上報機制是否正常運作
6. 檢查 App 是否崩潰或異常
7. 檢查 App 耗電量是否在合理範圍

**預期結果**：
- Logger 機制持續正常運作
- 上報機制持續正常運作
- App 無崩潰或異常
- App 耗電量在合理範圍

---

### 3.2 網路異常處理測試
**測試目標**：驗證 Camera 端在網路異常時正確處理上報

**前置條件**：
- Camera 端設備已啟動 Logger
- 已有累計的離線時長資料

**測試步驟**：
1. 確認 Camera 端已有累計的離線時長資料
2. 模擬網路異常（如：關閉網路、切換到無網路環境）
3. 等待上報時機
4. 確認上報失敗（網路異常導致）
5. 檢查 Cache 是否保留
6. 恢復網路連線
7. 等待下一次上報時機
8. 確認上報成功，且包含之前保留的資料

**預期結果**：
- 網路異常時上報失敗，Cache 保留
- 網路恢復後上報成功，包含之前保留的資料

---

### 3.3 多台 Camera 同時上報測試
**測試目標**：驗證多台 Camera 同時上報時，API 和系統穩定

**前置條件**：
- 多台 Camera 端設備（至少 3 台）
- 所有 Camera 端已啟動 Logger
- 網路連線正常

**測試步驟**：
1. 同時啟動多台 Camera 端 App，開啟 Logger
2. 讓所有 Camera 端同時運作
3. 等待上報時機（所有 Camera 端同時上報）
4. 檢查 API 是否正常處理所有上報請求
5. 檢查系統是否穩定（無崩潰、無異常）
6. 檢查每台 Camera 端的上報是否成功

**預期結果**：
- API 正常處理多台 Camera 同時上報
- 系統穩定，無崩潰或異常
- 每台 Camera 端的上報成功

---

### 3.4 大量資料上報測試
**測試目標**：驗證 Camera 端上報大量資料時，API 和系統穩定

**前置條件**：
- Camera 端設備已啟動 Logger
- 可模擬大量離線時長資料（如：跨多個小時的斷線）

**測試步驟**：
1. 模擬 Camera 端累計大量離線時長資料（如：跨 10 個小時的斷線）
2. 等待上報時機
3. 檢查上報的 Payload 大小是否合理
4. 檢查 API 是否正常處理大量資料
5. 檢查上報是否成功
6. 檢查 Viewer 端是否正確顯示大量資料

**預期結果**：
- API 正常處理大量資料上報
- 上報成功
- Viewer 端正確顯示大量資料

---

## 4. 使用者體驗測試 (User Experience)

### 4.1 Connection Report 頁面載入速度測試
**測試目標**：驗證 Connection Report 頁面載入速度符合使用者體驗要求

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料

**測試步驟**：
1. 在 Viewer 端進入 Camera 設定頁面
2. 點擊「Connection Report」或「離線報告」
3. 測量頁面載入時間（從點擊到內容完全顯示）
4. 檢查頁面載入過程是否有適當的載入指示（如：Loading spinner）
5. 檢查頁面載入後內容是否完整顯示

**預期結果**：
- 頁面載入時間在合理範圍內（建議 < 3 秒）
- 頁面載入過程有適當的載入指示
- 頁面載入後內容完整顯示

---

### 4.2 Connection Report 頁面 UI 顯示測試
**測試目標**：驗證 Connection Report 頁面 UI 顯示符合設計規範

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料
- 設計文件（Figma）

**測試步驟**：
1. 在 Viewer 端進入 Connection Report 頁面
2. 對照設計文件（Figma），檢查 UI 元素：
   - 時間軸顯示
   - 顏色標示（灰色/綠色/黃色/紅色）
   - 時段標示
   - 日期選擇器
   - 其他 UI 元素
3. 檢查 UI 元素是否符合設計規範（顏色、字型、間距等）

**預期結果**：
- UI 元素符合設計規範
- 顏色標示正確
- 時段標示清晰
- 整體 UI 美觀易用

---

### 4.3 Connection Report 頁面互動測試
**測試目標**：驗證 Connection Report 頁面互動功能正常

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的多日離線統計資料

**測試步驟**：
1. 在 Viewer 端進入 Connection Report 頁面
2. 測試日期選擇器：
   - 選擇不同日期範圍
   - 檢查時間軸是否正確更新
3. 測試時間軸互動：
   - 點擊不同時段
   - 檢查是否顯示詳細資訊（如有實作）
4. 測試其他互動功能（如有）

**預期結果**：
- 日期選擇器正常運作
- 時間軸互動正常
- 其他互動功能正常

---

### 4.4 Connection Report 頁面錯誤處理測試
**測試目標**：驗證 Connection Report 頁面在錯誤情況下的使用者體驗

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- 可模擬錯誤情況（如：API 錯誤、無資料）

**測試步驟**：
1. 模擬 API 錯誤（如：網路異常、API 返回錯誤）
2. 在 Viewer 端進入 Connection Report 頁面
3. 檢查是否顯示適當的錯誤訊息
4. 檢查錯誤訊息是否清楚易懂
5. 檢查是否有重試機制（如有）
6. 模擬無資料情況
7. 檢查是否顯示適當的無資料訊息

**預期結果**：
- 錯誤情況下有適當的錯誤訊息
- 錯誤訊息清楚易懂
- 無資料情況下有適當的無資料訊息

---

## 5. 平台差異測試 (Platform Differences)

### 5.1 iOS vs Android Camera 端差異測試
**測試目標**：驗證 iOS 和 Android Camera 端實作一致

**前置條件**：
- iOS Camera 端設備
- Android Camera 端設備
- 相同的測試場景

**測試步驟**：
1. 在 iOS Camera 端執行基本功能測試（Logger 啟動、離線累計、上報等）
2. 在 Android Camera 端執行相同的測試
3. 比較兩平台的實作差異：
   - Logger 機制
   - 離線累計機制
   - 上報機制
   - Cache 管理機制
4. 特別注意 iOS 特殊行為（App 退到背景丟棄資料）

**預期結果**：
- iOS 和 Android Camera 端基本功能一致
- iOS 特殊行為（App 退到背景）正確實作
- 其他功能無明顯差異

---

### 5.2 iOS vs Android Viewer 端差異測試
**測試目標**：驗證 iOS 和 Android Viewer 端實作一致

**前置條件**：
- iOS Viewer 端設備
- Android Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- 相同的測試場景

**測試步驟**：
1. 在 iOS Viewer 端執行基本功能測試（版本判斷、UI 顯示、時區轉換等）
2. 在 Android Viewer 端執行相同的測試
3. 比較兩平台的實作差異：
   - UI 顯示（spacing、back icon、date picker、字型等）
   - 功能實作
4. 對照設計文件，檢查平台差異是否符合設計規範

**預期結果**：
- iOS 和 Android Viewer 端基本功能一致
- UI 差異符合設計規範（spacing、back icon、date picker、字型等）
- 其他功能無明顯差異

---

## 6. 邊緣案例測試 (Edge Cases)

### 6.1 時區邊界測試
**測試目標**：驗證時區轉換在邊界情況下的正確性

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料
- 可切換不同時區（包含 UTC+0、UTC+12、UTC-12 等極端時區）

**測試步驟**：
1. 設定 Viewer 端時區為 UTC+0
2. 進入 Connection Report 頁面，檢查時間軸顯示
3. 設定 Viewer 端時區為 UTC+12
4. 進入 Connection Report 頁面，檢查時間軸顯示
5. 設定 Viewer 端時區為 UTC-12
6. 進入 Connection Report 頁面，檢查時間軸顯示
7. 檢查跨日邊界情況（如：UTC+12 可能導致日期顯示不同）

**預期結果**：
- 時區轉換在邊界情況下正確
- 跨日邊界情況處理正確

---

### 6.2 日期範圍邊界測試
**測試目標**：驗證日期範圍查詢在邊界情況下的正確性

**前置條件**：
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- Camera 端已有上報的離線統計資料

**測試步驟**：
1. 查詢未來日期範圍（如：2026-12-31 至 2027-01-01）
2. 檢查 Response 是否正確處理（應為無資料或錯誤）
3. 查詢過去很遠的日期範圍（如：2020-01-01 至 2020-01-02）
4. 檢查 Response 是否正確處理（應為無資料，因為資料有 TTL 30 天）
5. 查詢 start_date > end_date 的情況
6. 檢查 Response 是否正確處理（應為錯誤）

**預期結果**：
- 日期範圍邊界情況正確處理
- 未來日期返回無資料或錯誤
- 過去很遠的日期返回無資料（TTL 30 天）
- start_date > end_date 返回錯誤

---

### 6.3 資料完整性測試
**測試目標**：驗證資料在各種情況下的完整性

**前置條件**：
- Camera 端設備
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）

**測試步驟**：
1. 在 Camera 端模擬各種斷線情況（短暫、長時間、多次等）
2. 等待上報成功
3. 在 Viewer 端查詢離線統計資料
4. 檢查資料完整性：
   - 所有時段的資料是否正確
   - 離線時長計算是否正確
   - 時間對應是否正確
5. 檢查資料一致性（Camera 端上報的資料與 Viewer 端顯示的資料一致）

**預期結果**：
- 資料完整性正確
- 所有時段的資料正確
- 離線時長計算正確
- 時間對應正確
- 資料一致性正確

---

## 7. 迴歸測試 (Regression Testing)

### 7.1 舊版 Camera 顯示測試
**測試目標**：驗證舊版 Camera（cameraHealth = 1）仍正常顯示舊版 WebView

**前置條件**：
- Viewer 端設備
- 舊版 Camera（cameraHealth = 1）
- 已配對的 Camera 和 Viewer

**測試步驟**：
1. 在 Viewer 端登入帳號
2. 進入 Camera 設定頁面
3. 點擊「Connection Report」或「離線報告」
4. 檢查是否開啟舊版 WebView（`stats/offline.html`）
5. 檢查舊版 WebView 功能是否正常
6. 檢查舊版 WebView 內容是否正常顯示

**預期結果**：
- 舊版 Camera 仍正常顯示舊版 WebView
- 舊版 WebView 功能正常
- 舊版 WebView 內容正常顯示

---

### 7.2 XMPP 連線功能測試
**測試目標**：驗證 XMPP 連線功能不受影響

**前置條件**：
- Camera 端設備
- Viewer 端設備
- 已配對的 Camera 和 Viewer

**測試步驟**：
1. 在 Camera 端登入帳號
2. 確認 XMPP 連線成功
3. 在 Viewer 端查看 Camera 狀態為 Online
4. 模擬網路中斷
5. 確認 XMPP 斷線
6. 恢復網路連線
7. 確認 XMPP 重新連線成功
8. 在 Viewer 端查看 Camera 狀態恢復為 Online

**預期結果**：
- XMPP 連線功能正常
- XMPP 斷線和恢復正常
- Camera 狀態顯示正確

---

### 7.3 即時影像功能測試
**測試目標**：驗證即時影像功能不受影響

**前置條件**：
- Camera 端設備
- Viewer 端設備
- 已配對的 Camera 和 Viewer
- 網路連線正常

**測試步驟**：
1. 在 Viewer 端開啟即時影像
2. 確認即時影像正常顯示
3. 確認即時影像延遲在合理範圍內
4. 模擬網路中斷
5. 確認即時影像中斷
6. 恢復網路連線
7. 確認即時影像恢復

**預期結果**：
- 即時影像功能正常
- 即時影像延遲在合理範圍內
- 即時影像中斷和恢復正常

---

## 8. 效能測試 (Performance Testing)

### 8.1 API 回應時間測試
**測試目標**：驗證 API 回應時間符合效能要求

**前置條件**：
- 有效的 KV_TOKEN
- 正確的 jid
- Camera 端已有上報的離線統計資料

**測試步驟**：
1. 使用 API 工具（如：Postman）呼叫 GET `/device/v1/stats/:jid` API
2. 測量 API 回應時間
3. 重複測試多次（至少 10 次）
4. 計算平均回應時間
5. 檢查回應時間是否符合效能要求（建議 < 1 秒）

**預期結果**：
- API 回應時間在合理範圍內（建議 < 1 秒）
- API 回應時間穩定

---

### 8.2 大量資料查詢效能測試
**測試目標**：驗證大量資料查詢時的效能

**前置條件**：
- 有效的 KV_TOKEN
- 正確的 jid
- Camera 端已有上報的大量離線統計資料（如：30 天的資料）

**測試步驟**：
1. 使用大日期範圍（如：30 天）呼叫 GET `/device/v1/stats/:jid` API
2. 測量 API 回應時間
3. 檢查 Response 大小
4. 檢查 Viewer 端載入時間
5. 檢查 Viewer 端渲染時間

**預期結果**：
- 大量資料查詢時 API 回應時間在合理範圍內
- Viewer 端載入和渲染時間在合理範圍內

---

## 9. 安全性測試 (Security Testing)

### 9.1 API 授權測試
**測試目標**：驗證 API 授權機制正常運作

**前置條件**：
- 有效的 KV_TOKEN
- 無效的 KV_TOKEN（如：過期、錯誤）

**測試步驟**：
1. 使用有效的 KV_TOKEN 呼叫 POST `/device/v1/stats` API
2. 確認 API 正常運作
3. 使用無效的 KV_TOKEN 呼叫 API
4. 確認 API 正確拒絕（Status Code 401 或 403）
5. 使用無 Token 的 Request 呼叫 API
6. 確認 API 正確拒絕（Status Code 401）

**預期結果**：
- API 授權機制正常運作
- 無效 Token 正確拒絕
- 無 Token Request 正確拒絕

---

### 9.2 資料隱私測試
**測試目標**：驗證使用者只能查詢自己的 Camera 資料

**前置條件**：
- 兩個不同的使用者帳號（User A 和 User B）
- User A 的 Camera（jid_A）
- User B 的 Camera（jid_B）
- User A 的 KV_TOKEN
- User B 的 KV_TOKEN

**測試步驟**：
1. 使用 User A 的 KV_TOKEN 查詢 User A 的 Camera（jid_A）
2. 確認查詢成功
3. 使用 User A 的 KV_TOKEN 查詢 User B 的 Camera（jid_B）
4. 確認查詢失敗（Status Code 403 或 404）
5. 使用 User B 的 KV_TOKEN 查詢 User A 的 Camera（jid_A）
6. 確認查詢失敗（Status Code 403 或 404）

**預期結果**：
- 使用者只能查詢自己的 Camera 資料
- 查詢其他使用者的 Camera 資料時正確拒絕

---

## 10. 整合測試 (Integration Testing)

### 10.1 端到端測試 - 完整流程
**測試目標**：驗證從 Camera 端上報到 Viewer 端顯示的完整流程

**前置條件**：
- Camera 端設備
- Viewer 端設備
- 新版 Camera（cameraHealth = 2）
- 已配對的 Camera 和 Viewer

**測試步驟**：
1. 在 Camera 端登入帳號，啟動 Logger
2. 模擬斷線情況（如：斷線 10 分鐘）
3. 等待上報時機，確認上報成功
4. 在 Viewer 端進入 Connection Report 頁面
5. 檢查離線統計資料是否正確顯示
6. 檢查時間軸顏色標示是否正確（應為黃色，因為 10 分鐘 = 600 秒，介於 6-1440 秒）
7. 檢查時區轉換是否正確

**預期結果**：
- 完整流程正常運作
- Camera 端上報成功
- Viewer 端正確顯示資料
- 時間軸顏色標示正確
- 時區轉換正確

---

### 10.2 多台 Camera 整合測試
**測試目標**：驗證多台 Camera 同時運作時的整合

**前置條件**：
- 多台 Camera 端設備（至少 3 台）
- Viewer 端設備
- 所有 Camera 為新版（cameraHealth = 2）
- 所有 Camera 已配對

**測試步驟**：
1. 同時啟動多台 Camera 端 App，開啟 Logger
2. 在不同 Camera 端模擬不同的斷線情況
3. 等待上報時機，確認所有 Camera 端上報成功
4. 在 Viewer 端切換不同 Camera，進入各自的 Connection Report 頁面
5. 檢查每台 Camera 的離線統計資料是否正確顯示
6. 檢查資料是否互相不影響（每台 Camera 的資料獨立）

**預期結果**：
- 多台 Camera 同時運作正常
- 每台 Camera 的資料正確顯示
- 資料互相不影響

---

## 附錄

### A. 測試環境
- **Dev 環境**：https://api.my-alfred-dev.com/
- **Pre-prod 環境**：https://api.my-alfred-pre.com/
- **Prod 環境**：https://api.my-alfred.com/

### B. API 規格參考
- [Connection Report API v2 (WIP)](https://alfredlabs.atlassian.net/wiki/spaces/PD/pages/4583030786/Connection+Report+API+v2+WIP)

### C. Tech Spec 參考
- [Camera 離線報告優化 Tech Spec](https://alfredlabs.atlassian.net/wiki/spaces/MOB/pages/4598628353/Camera+Tech+Spec)

### D. 設計文件參考
- [Camera Health Offline Dashboard Redesign - 20251210 flow](https://www.figma.com/file/0XjlIeVcUWlnASWCcYJoYW?node-id=12006%3A3428)

### E. 專有名詞參考
- [Terminology Table v2](https://alfredlabs.atlassian.net/wiki/spaces/~590960658/pages/3834085744/Terminology+Table+v2)

---

**測試案例版本**：v1.0  
**最後更新日期**：2026-01-20  
**負責人**：QA Team - Jessie
