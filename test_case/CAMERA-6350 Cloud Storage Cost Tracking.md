# CAMERA-6350 Cloud Storage Cost Tracking 測試案例

## 📋 測試概述

**Ticket**: CAMERA-6350  
**功能**: Cloud Storage Cost Tracking  
**Design Document**: [Cloud Storage Cost Tracking](https://alfredlabs.atlassian.net/wiki/spaces/PD/pages/4353359876/Cloud+Storage+Cost+Tracking)  
**建立日期**: 2025-11-10  
**負責人**: QA Team - Jessie

### 功能重點
本功能實作 Cloud Storage Cost Tracking，用於追蹤不同用戶群體（訂閱方案、地區、相機數量）的雲端資源使用情況，用於成本分析、方案定價優化、用戶行為分析：
- **事件名稱**：`camera: active`（相機心跳上報事件）
- **Event Properties 記錄**：在 `camera: active` 事件中附加資源使用增量數據（period 欄位）
- **持久化數據更新**：當 snapshot/video 上傳成功後（包含 retry）更新持久化數據
- **重置機制**：在特定時機點重置 period 欄位相關持久化數據

### 核心功能
1. **Event Properties 附加**：在 `camera: active` 事件中加上 period 欄位（`period_snapshot_count`、`period_snapshot_size_kb`、`period_video_count`、`period_video_duration_sec`、`period_video_size_kb`）
2. **Snapshot 上傳追蹤**：當相機端每一次上傳 snapshot 成功後（包含 retry），更新持久化數據
3. **Video 上傳追蹤**：當相機端每一次上傳 video 成功後（包含 retry），更新持久化數據（包含手動錄影）
4. **重置機制**：在每次上報後、相機端登出（包含切換至 viewer）、超過時間間隔（正式版 48 小時，內測版 30 分鐘）時重置持久化數據
---
## 🎯 測試重點

### 成本記錄邏輯重點
1. **事件觸發**：驗證 `camera: active` 事件正確觸發（相機心跳上報時）
2. **Event Properties 附加**：驗證 `camera: active` 事件中正確附加 period 欄位
3. **上傳觸發記錄**：驗證 snapshot/video 上傳至 Cloud Storage 成功後（包含 retry）正確更新持久化數據
4. **記錄時機**：驗證持久化數據更新的時機正確（上傳成功後，包含 retry 成功的情況）
5. **記錄內容**：驗證持久化數據包含必要資訊（snapshot 數量、大小、video 數量、時長、大小等）
6. **記錄準確性**：驗證記錄的資料準確無誤
7. **記錄完整性**：驗證所有上傳至 Cloud Storage 的 snapshot/video（包含 retry 和手動錄影）都被正確記錄

### Event Properties 重點
1. **屬性完整性**：驗證 `camera: active` 事件的 Event Properties 包含所有必要屬性（period_snapshot_count、period_snapshot_size_kb、period_video_count、period_video_duration_sec、period_video_size_kb）
2. **屬性類型正確性**：驗證每個屬性的資料類型正確（period_snapshot_count: integer、period_snapshot_size_kb: long、period_video_count: integer、period_video_duration_sec: integer、period_video_size_kb: long）
3. **屬性值正確性**：驗證每個屬性的值正確且與實際資料一致
4. **屬性格式**：驗證每個屬性的格式正確（資料類型、格式規範等）
5. **邊界值處理**：驗證極值、空值等邊界條件下的屬性處理
6. **週期累計邏輯**：驗證 period 相關屬性的累計邏輯正確（自上次上報以來 snapshot/video 的數量、大小、時長等）
7. **重置時機點**：驗證 Event Properties 在正確的時機點重置（每次上報後、相機端登出包含切換至 viewer、超過時間間隔：正式版 48 小時，內測版 30 分鐘）
8. **Analytics 傳遞**：驗證 Event Properties 正確傳遞到 Analytics 系統（Amplitude 等）

### 上傳追蹤重點
1. **Snapshot 上傳追蹤**：驗證 snapshot 上傳成功後（包含 retry）正確更新持久化數據（period_snapshot_count++、period_snapshot_size_kb += fileSize）
2. **Video 上傳追蹤**：驗證 video 上傳成功後（包含 retry）正確更新持久化數據（period_video_count++、period_video_duration_sec += duration、period_video_size_kb += fileSize），包含手動錄影
3. **Retry 機制**：驗證 retry 成功後也正確更新持久化數據
4. **檔案大小追蹤**：驗證上傳檔案的 size 正確記錄（單位：KB）
5. **累計邏輯**：驗證使用量正確累計（總大小、總數量、總時長等）
6. **持久化數據更新**：驗證持久化數據即時更新

### 核心功能區域
1. **`camera: active` 事件**：相機心跳上報事件，附加 period 欄位
2. **持久化數據管理**：管理 period 欄位相關的持久化數據（DVR api 的 snapshot）
3. **上傳追蹤服務**：追蹤 snapshot/video 上傳並更新持久化數據
4. **重置機制**：在特定時機點重置持久化數據

---

## 📝 測試案例

## 0. 成本記錄邏輯測試

### 0.1 Snapshot 上傳成功時持久化數據更新驗證
**測試目標**：驗證 snapshot 成功上傳至 Cloud Storage 時（包含 retry）正確更新持久化數據

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 設備已配對並正常運作
- Analytics 追蹤系統已啟用

**測試步驟**：
1. 記錄初始持久化數據狀態（period_snapshot_count、period_snapshot_size_kb）
2. 觸發 snapshot 上傳至 Cloud Storage
3. 確認上傳成功（HTTP 200）
4. 檢查持久化數據是否正確更新：
   - `period_snapshot_count` 是否增加 1
   - `period_snapshot_size_kb` 是否增加檔案大小（KB）
5. 驗證持久化數據的資料準確性
6. 等待 `camera: active` 事件觸發（相機心跳上報）
7. 檢查 `camera: active` 事件的 Event Properties 是否包含正確的 period 欄位值

**預期結果**：
- Snapshot 上傳成功後持久化數據正確更新
- `period_snapshot_count` 正確增加 1
- `period_snapshot_size_kb` 正確增加檔案大小（KB）
- 持久化數據的資料準確無誤
- `camera: active` 事件中的 Event Properties 包含正確的 period 欄位值
- 無遺漏或錯誤記錄
Test Result： PASS
---

### 0.2 Snapshot 上傳失敗時持久化數據驗證
**測試目標**：驗證 snapshot 上傳至 Cloud Storage 失敗時（未包含 retry 成功）的持久化數據處理

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 可模擬上傳失敗（如網路中斷、URL 過期等）

**測試步驟**：
1. 記錄初始持久化數據狀態
2. 觸發 snapshot 上傳至 Cloud Storage
3. 模擬上傳失敗（如網路中斷、URL 過期等），且 retry 也失敗
4. 檢查持久化數據是否未更新：
   - `period_snapshot_count` 不應增加
   - `period_snapshot_size_kb` 不應增加
5. 驗證失敗時持久化數據未更新

**預期結果**：
- Snapshot 上傳失敗且 retry 也失敗時，持久化數據不應更新
- `period_snapshot_count` 不應增加
- `period_snapshot_size_kb` 不應增加
- 只有上傳成功（包含 retry 成功）時才更新持久化數據
- 錯誤處理機制正確

Test Result： PASS
---

### 0.3 Snapshot Retry 成功時持久化數據更新驗證
**測試目標**：驗證 snapshot 上傳失敗後 retry 成功時正確更新持久化數據

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 可模擬上傳失敗後 retry 成功

**測試步驟**：
1. 記錄初始持久化數據狀態
2. 觸發 snapshot 上傳至 Cloud Storage
3. 模擬第一次上傳失敗
4. 確認 retry 機制觸發
5. 確認 retry 上傳成功（HTTP 200）
6. 檢查持久化數據是否正確更新：
   - `period_snapshot_count` 是否增加 1
   - `period_snapshot_size_kb` 是否增加檔案大小（KB）
7. 驗證 retry 成功後持久化數據正確更新

**預期結果**：
- Snapshot 上傳失敗後 retry 成功時，持久化數據正確更新
- `period_snapshot_count` 正確增加 1
- `period_snapshot_size_kb` 正確增加檔案大小（KB）
- Retry 成功後才更新持久化數據
- 時機符合業務邏輯要求（上傳成功後，包含 retry 成功）
---
Test Result： PASS

### 0.4 Video 上傳成功時持久化數據更新驗證（包含手動錄影）
**測試目標**：驗證 video 成功上傳至 Cloud Storage 時（包含 retry 和手動錄影）正確更新持久化數據

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 設備已配對並正常運作
- Analytics 追蹤系統已啟用

**測試步驟**：
1. 記錄初始持久化數據狀態（period_video_count、period_video_duration_sec、period_video_size_kb）
2. 觸發 video 上傳至 Cloud Storage（自動錄影）
3. 確認上傳成功（HTTP 200）
4. 檢查持久化數據是否正確更新：
   - `period_video_count` 是否增加 1
   - `period_video_duration_sec` 是否增加 video 時長（秒）
   - `period_video_size_kb` 是否增加檔案大小（KB）
5. 觸發手動錄影並上傳至 Cloud Storage
6. 確認上傳成功
7. 檢查持久化數據是否正確更新（手動錄影也應更新）
8. 驗證持久化數據的資料準確性
9. 等待 `camera: active` 事件觸發
10. 檢查 `camera: active` 事件的 Event Properties 是否包含正確的 period 欄位值

**預期結果**：
- Video 上傳成功後（包含 retry）持久化數據正確更新
- 手動錄影上傳成功後也正確更新持久化數據
- `period_video_count` 正確增加（自動錄影和手動錄影都計入）
- `period_video_duration_sec` 正確增加 video 時長（秒）
- `period_video_size_kb` 正確增加檔案大小（KB）
- `camera: active` 事件中的 Event Properties 包含正確的 period 欄位值
- 無遺漏或錯誤記錄
Test Result： PASS
---

### 0.5 `camera: active` 事件 Event Properties 完整性驗證
**測試目標**：驗證 `camera: active` 事件的 Event Properties 包含所有必要屬性

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 設備已配對
- Analytics 追蹤系統已啟用（Amplitude）

**測試步驟**：
1. 在週期內上傳 snapshot 和 video 至 Cloud Storage
2. 確認上傳成功
3. 等待 `camera: active` 事件觸發（相機心跳上報）
4. 檢查 `camera: active` 事件的 Event Properties，驗證以下屬性是否存在：
   - `period_snapshot_count`：自上次上報以來上傳的 snapshot 數量（integer）
   - `period_snapshot_size_kb`：自上次上報以來上傳的 snapshot 總大小（long，KB）
   - `period_video_count`：自上次上報以來上傳的 video 數量（integer）
   - `period_video_duration_sec`：自上次上報以來上傳的 video 總時長（integer，秒）
   - `period_video_size_kb`：自上次上報以來上傳的 video 總大小（long，KB）
5. 驗證所有必要屬性都存在
6. 驗證屬性名稱拼寫正確

**預期結果**：
- `camera: active` 事件的 Event Properties 包含所有必要屬性
- 所有必要屬性都存在且不為 null
- 屬性名稱符合規格文件定義：
  - `period_snapshot_count` 存在（integer）
  - `period_snapshot_size_kb` 存在（long）
  - `period_video_count` 存在（integer）
  - `period_video_duration_sec` 存在（integer）
  - `period_video_size_kb` 存在（long）
- 無遺漏必要屬性
Test Result： PASS
---

### 0.6 Event Properties 值正確性驗證
**測試目標**：驗證 `camera: active` 事件中 Event Properties 的每個屬性值正確且符合預期

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 設備已配對
- 記錄自上次上報以來實際上傳的資料（snapshot 數量、大小、video 數量、時長、大小等）

**測試步驟**：
1. 記錄自上次上報以來實際上傳資料：
   - Snapshot 數量
   - Snapshot 總大小（KB）
   - Video 數量（包含手動錄影）
   - Video 總時長（秒）
   - Video 總大小（KB）
2. 在週期內觸發多個 snapshot 和 video 上傳至 Cloud Storage（包含 retry 成功的情況）
3. 確認所有上傳成功
4. 等待 `camera: active` 事件觸發
5. 檢查 `camera: active` 事件的 Event Properties 中每個屬性的值：
   - `period_snapshot_count`：與自上次上報以來實際上傳的 snapshot 數量一致
   - `period_snapshot_size_kb`：與自上次上報以來實際上傳的 snapshot 總大小一致（單位：KB）
   - `period_video_count`：與自上次上報以來實際上傳的 video 數量一致（包含手動錄影）
   - `period_video_duration_sec`：與自上次上報以來實際上傳的 video 總時長一致（單位：秒）
   - `period_video_size_kb`：與自上次上報以來實際上傳的 video 總大小一致（單位：KB）
6. 比對 Event Properties 值與實際資料的一致性

**預期結果**：
- 所有 Event Properties 的值正確
- `period_snapshot_count` 與實際 snapshot 數量一致
- `period_snapshot_size_kb` 與實際 snapshot 總大小一致（單位：KB）
- `period_video_count` 與實際 video 數量一致（包含手動錄影）
- `period_video_duration_sec` 與實際 video 總時長一致（單位：秒）
- `period_video_size_kb` 與實際 video 總大小一致（單位：KB）
- 所有值與實際資料一致
Test Result： PASS
---

### 0.7 Event Properties 格式與類型驗證
**測試目標**：驗證 `camera: active` 事件中 Event Properties 的每個屬性格式和資料類型正確

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- Analytics 追蹤系統已啟用

**測試步驟**：
1. 在週期內上傳 snapshot 和 video 至 Cloud Storage
2. 確認上傳成功
3. 等待 `camera: active` 事件觸發
4. 檢查 `camera: active` 事件的 Event Properties 中每個屬性的格式和類型：
   - `period_snapshot_count`：整數格式（integer），非負整數
   - `period_snapshot_size_kb`：長整數格式（long），單位為 KB，非負數
   - `period_video_count`：整數格式（integer），非負整數
   - `period_video_duration_sec`：整數格式（integer），單位為秒，非負數
   - `period_video_size_kb`：長整數格式（long），單位為 KB，非負數
5. 驗證每個屬性的資料類型正確
6. 驗證格式符合規格文件定義

**預期結果**：
- 所有 Event Properties 的格式正確
- `period_snapshot_count` 為整數（integer），非負數
- `period_snapshot_size_kb` 為長整數（long），單位為 KB，非負數
- `period_video_count` 為整數（integer），非負數
- `period_video_duration_sec` 為整數（integer），單位為秒，非負數
- `period_video_size_kb` 為長整數（long），單位為 KB，非負數
- 所有格式符合規格文件定義
Test Result： PASS
---

### 0.8 Event Properties 邊界值驗證
**測試目標**：驗證 Event Properties 在邊界條件下的正確性

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 測試週期內無上傳的情況：
   - 在週期內不上傳任何 snapshot 或 video
   - 驗證 `period_snapshot_count` 為 0
   - 驗證 `period_snapshot_size_kb` 為 0
   - 驗證 `period_video_count` 為 0
   - 驗證 `period_video_duration_sec` 為 0
   - 驗證 `period_video_size_kb` 為 0
2. 測試極小檔案上傳（如 < 1KB）：
   - 上傳極小的 snapshot 和 video
   - 驗證 `period_snapshot_size_kb` 和 `period_video_size_kb` 正確記錄（可能為 0 或接近 0）
3. 測試極大檔案上傳（如 > 100MB）：
   - 上傳極大的 snapshot 和 video
   - 驗證 `period_snapshot_size_kb` 和 `period_video_size_kb` 正確記錄（單位為 KB）
4. 測試極短時長 video（如 < 1 秒）：
   - 上傳極短時長的 video
   - 驗證 `period_video_duration_sec` 正確記錄（可能為 0 或接近 0）
5. 測試極長時長 video（如 > 1 小時）：
   - 上傳極長時長的 video
   - 驗證 `period_video_duration_sec` 正確記錄（單位為秒）
6. 測試空值或 null 值處理：
   - 驗證必要屬性不會為 null
   - 驗證數值屬性不會為負數

**預期結果**：
- 週期內無上傳時，所有 count 和 size 屬性為 0
- 極小檔案上傳時 Event Properties 正確記錄
- 極大檔案上傳時 Event Properties 正確記錄（單位為 KB）
- 極短時長 video 時 `period_video_duration_sec` 正確記錄
- 極長時長 video 時 `period_video_duration_sec` 正確記錄（單位為秒）
- 空值或 null 值正確處理（必要屬性不為 null）
- 數值邊界正確處理（非負數）
- 無格式錯誤或資料損壞
Test Result： PASS
---

### 0.9 Event Properties 週期累計邏輯驗證（自上次上報以來）
**測試目標**：驗證 period 相關屬性的累計邏輯正確（自上次上報以來）

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 觸發第一次 `camera: active` 事件上報（記錄初始狀態）
2. 在週期內（自上次上報以來）上傳多個 snapshot：
   - 上傳 snapshot 1（大小：100 KB）
   - 上傳 snapshot 2（大小：200 KB）
   - 上傳 snapshot 3（大小：150 KB）
   - 檢查持久化數據：驗證 `period_snapshot_count` 累計為 3
   - 檢查持久化數據：驗證 `period_snapshot_size_kb` 累計為 450 KB
3. 在週期內（自上次上報以來）上傳多個 video（包含手動錄影）：
   - 上傳 video 1（時長：10 秒，大小：500 KB）
   - 上傳 video 2（時長：20 秒，大小：1000 KB）
   - 手動錄影 video 3（時長：15 秒，大小：750 KB）
   - 檢查持久化數據：驗證 `period_video_count` 累計為 3
   - 檢查持久化數據：驗證 `period_video_duration_sec` 累計為 45 秒
   - 檢查持久化數據：驗證 `period_video_size_kb` 累計為 2250 KB
4. 驗證混合上傳（snapshot + video）：
   - 同時上傳 snapshot 和 video
   - 驗證 snapshot 和 video 的屬性分別正確累計
5. 觸發第二次 `camera: active` 事件上報
6. 檢查 Event Properties 是否包含正確的累計值
7. 驗證上報後持久化數據重置為 0

**預期結果**：
- `period_snapshot_count` 正確累計自上次上報以來的 snapshot 數量
- `period_snapshot_size_kb` 正確累計自上次上報以來的 snapshot 總大小（KB）
- `period_video_count` 正確累計自上次上報以來的 video 數量（包含手動錄影）
- `period_video_duration_sec` 正確累計自上次上報以來的 video 總時長（秒）
- `period_video_size_kb` 正確累計自上次上報以來的 video 總大小（KB）
- 混合上傳時 snapshot 和 video 屬性分別正確累計
- `camera: active` 事件中的 Event Properties 包含正確的累計值
- 上報後持久化數據正確重置為 0
Test Result： PASS
---

### 0.10 Event Properties 在多次上傳中的累計驗證（包含 Retry）
**測試目標**：驗證多次上傳時 Event Properties 的正確累計

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 觸發第一次 `camera: active` 事件上報（記錄初始狀態）
2. 在週期內（自上次上報以來）連續上傳多個 snapshot 和 video（如各 5-10 個），包含部分 retry 成功的情況
3. 記錄每次上傳的資料（包含 retry 成功的）：
   - 每個 snapshot 的大小（KB）
   - 每個 video 的時長（秒）和大小（KB）
   - 標記哪些是 retry 成功後才記錄的
4. 檢查每次上傳成功後（包含 retry 成功）的持久化數據：
   - 驗證 `period_snapshot_count` 逐步累計
   - 驗證 `period_snapshot_size_kb` 逐步累計
   - 驗證 `period_video_count` 逐步累計
   - 驗證 `period_video_duration_sec` 逐步累計
   - 驗證 `period_video_size_kb` 逐步累計
5. 手動計算累計值（只計算成功上傳的，包含 retry 成功）：
   - 計算 snapshot 總數量 = 所有成功上傳的 snapshot 數量總和（包含 retry 成功）
   - 計算 snapshot 總大小 = 所有成功上傳的 snapshot 大小總和（KB）
   - 計算 video 總數量 = 所有成功上傳的 video 數量總和（包含 retry 成功和手動錄影）
   - 計算 video 總時長 = 所有成功上傳的 video 時長總和（秒）
   - 計算 video 總大小 = 所有成功上傳的 video 大小總和（KB）
6. 觸發第二次 `camera: active` 事件上報
7. 檢查 Event Properties 值與手動計算值是否一致

**預期結果**：
- `period_snapshot_count` 正確累計，與實際成功上傳的 snapshot 數量總和一致（包含 retry 成功）
- `period_snapshot_size_kb` 正確累計，與實際成功上傳的 snapshot 大小總和一致（KB）
- `period_video_count` 正確累計，與實際成功上傳的 video 數量總和一致（包含 retry 成功和手動錄影）
- `period_video_duration_sec` 正確累計，與實際成功上傳的 video 時長總和一致（秒）
- `period_video_size_kb` 正確累計，與實際成功上傳的 video 大小總和一致（KB）
- Event Properties 值與手動計算值完全一致
- Retry 成功後也正確累計
- 無遺漏或錯誤累計
Test Result： PASS
---

### 0.11 `camera: active` 事件在 Analytics 系統中的傳遞驗證
**測試目標**：驗證 `camera: active` 事件及其 Event Properties 正確傳遞到 Analytics 系統（Amplitude）

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- Analytics 系統已啟用（Amplitude）

**測試步驟**：
1. 在週期內（自上次上報以來）上傳多個 snapshot 和 video 至 Cloud Storage
2. 確認所有上傳成功（包含 retry 成功和手動錄影）
3. 等待 `camera: active` 事件觸發（相機心跳上報）
4. 檢查 Analytics 系統（Amplitude）中的 `camera: active` 事件：
   - 驗證 `camera: active` 事件正確記錄到 Analytics 系統
   - 驗證 Event Properties 正確傳遞
   - 驗證所有 5 個屬性都在 Analytics 系統中可見：
     - `period_snapshot_count`（integer）
     - `period_snapshot_size_kb`（long）
     - `period_video_count`（integer）
     - `period_video_duration_sec`（integer）
     - `period_video_size_kb`（long）
5. 比對 Event Properties 與 Analytics 系統中的屬性：
   - 屬性名稱是否一致（拼寫正確）
   - 屬性值是否一致
   - 屬性格式是否一致（資料類型：integer 或 long）
6. 驗證 Analytics 系統可以正確查詢和分析這些屬性：
   - 可以根據屬性進行篩選
   - 可以根據屬性進行分組統計
   - 可以根據屬性進行排序

**預期結果**：
- `camera: active` 事件正確記錄到 Analytics 系統（Amplitude）
- Event Properties 正確傳遞到 Analytics 系統
- 所有 5 個屬性都在 Analytics 系統中可見：
  - `period_snapshot_count` 可見且正確（integer）
  - `period_snapshot_size_kb` 可見且正確（long）
  - `period_video_count` 可見且正確（integer）
  - `period_video_duration_sec` 可見且正確（integer）
  - `period_video_size_kb` 可見且正確（long）
- 屬性名稱、值、格式在 Analytics 系統中一致
- Analytics 系統可以正確查詢和分析這些屬性
- 無屬性遺漏或格式轉換錯誤
Test Result： PASS
---

### 0.12 Event Properties 重置時機點驗證 - 每次上報後
**測試目標**：驗證每次 `camera: active` 事件上報後，持久化數據正確重置

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- Analytics 追蹤系統已啟用

**測試步驟**：
1. 在週期內（自上次上報以來）上傳多個 snapshot 和 video 至 Cloud Storage
2. 記錄上報前的持久化數據值：
   - `period_snapshot_count`
   - `period_snapshot_size_kb`
   - `period_video_count`
   - `period_video_duration_sec`
   - `period_video_size_kb`
3. 觸發 `camera: active` 事件上報（相機心跳上報）
4. 確認上報成功
5. 檢查上報後的持久化數據：
   - 驗證所有 5 個屬性是否重置為 0
   - 驗證持久化數據是否重置
6. 在重置後再次上傳 snapshot 和 video
7. 驗證新的持久化數據從 0 開始累計
8. 等待下一次 `camera: active` 事件上報
9. 驗證新的 Event Properties 從 0 開始累計

**預期結果**：
- 每次 `camera: active` 事件上報後，持久化數據正確重置
- 上報後所有 5 個屬性重置為 0：
  - `period_snapshot_count` = 0
  - `period_snapshot_size_kb` = 0
  - `period_video_count` = 0
  - `period_video_duration_sec` = 0
  - `period_video_size_kb` = 0
- 持久化數據正確重置
- 重置後新的上傳從 0 開始正確累計
- 無資料遺漏或錯誤
Test Result： PASS
---

### 0.13 Event Properties 重置時機點驗證 - 相機端登出（包含切換至 viewer）
**測試目標**：驗證相機端登出時（包含切換至 viewer），持久化數據正確重置

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 設備已配對並正常運作
- Analytics 追蹤系統已啟用

**測試步驟（相機端登出）**：
1. 在週期內上傳多個 snapshot 和 video 至 Cloud Storage
2. 記錄登出前的持久化數據值
3. 執行相機端登出操作
4. 檢查登出後的持久化數據：
   - 驗證所有 5 個屬性是否重置為 0
   - 驗證持久化數據是否重置
5. 重新登入相機端
6. 上傳新的 snapshot 和 video
7. 驗證新的持久化數據從 0 開始累計
8. 等待 `camera: active` 事件觸發
9. 驗證新的 Event Properties 從 0 開始累計

**測試步驟（切換至 viewer）**：
1. 在相機端上傳多個 snapshot 和 video 至 Cloud Storage
2. 記錄切換前的持久化數據值
3. 切換至 viewer 模式
4. 檢查切換後的持久化數據：
   - 驗證所有 5 個屬性是否重置為 0
   - 驗證持久化數據是否重置
5. 切換回相機端
6. 上傳新的 snapshot 和 video
7. 驗證新的持久化數據從 0 開始累計
8. 等待 `camera: active` 事件觸發
9. 驗證新的 Event Properties 從 0 開始累計

**預期結果**：
- 相機端登出時，持久化數據正確重置
- 切換至 viewer 時，持久化數據正確重置
- 登出/切換後所有 5 個屬性重置為 0：
  - `period_snapshot_count` = 0
  - `period_snapshot_size_kb` = 0
  - `period_video_count` = 0
  - `period_video_duration_sec` = 0
  - `period_video_size_kb` = 0
- 持久化數據正確重置
- 重新登入/切換回相機端後，新的上傳從 0 開始正確累計
- 無資料遺漏或錯誤
Test Result： PASS
---

### 0.14 Event Properties 重置時機點驗證 - 超過時間間隔
**測試目標**：驗證本次 `camera: active` 事件上報距離上次上報超過時間間隔時，Event Properties 帶上 0 並重置持久化數據

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- Analytics 追蹤系統已啟用
- 了解時間間隔設定（正式版：48 小時，內測版：30 分鐘）

**測試步驟（正式版 - 48 小時）**：
1. 在週期內上傳多個 snapshot 和 video 至 Cloud Storage
2. 觸發第一次 `camera: active` 事件上報
3. 確認上報成功
4. 等待超過 48 小時（或手動調整系統時間）
5. 觸發第二次 `camera: active` 事件上報（即使沒有新的上傳）
6. 檢查第二次上報的 Event Properties：
   - 驗證所有 5 個屬性是否為 0
   - 驗證持久化數據是否重置
7. 驗證 `camera: active` 事件中包含 Event Properties，且值為 0

**測試步驟（內測版 - 30 分鐘）**：
1. 在週期內上傳多個 snapshot 和 video 至 Cloud Storage
2. 觸發第一次 `camera: active` 事件上報
3. 確認上報成功
4. 等待超過 30 分鐘（或手動調整系統時間）
5. 觸發第二次 `camera: active` 事件上報（即使沒有新的上傳）
6. 檢查第二次上報的 Event Properties：
   - 驗證所有 5 個屬性是否為 0
   - 驗證持久化數據是否重置
7. 驗證 `camera: active` 事件中包含 Event Properties，且值為 0

**測試步驟（未超過時間間隔）**：
1. 在週期內上傳多個 snapshot 和 video 至 Cloud Storage
2. 觸發第一次 `camera: active` 事件上報
3. 確認上報成功
4. 在時間間隔內（正式版 < 48 小時，內測版 < 30 分鐘）觸發第二次上報
5. 檢查第二次上報的 Event Properties：
   - 驗證屬性值為累計值（非 0）
   - 驗證持久化數據未重置

**預期結果**：
- 超過時間間隔（正式版 48 小時，內測版 30 分鐘）時：
  - Event Properties 所有 5 個屬性為 0
  - 持久化數據正確重置
  - `camera: active` 事件中包含 Event Properties，且值為 0
- 未超過時間間隔時：
  - Event Properties 為累計值（非 0）
  - 持久化數據未重置
  - `camera: active` 事件中包含正確的累計值
- 時間間隔判斷邏輯正確
- 無資料遺漏或錯誤
Test Result： PASS
**備註**：
- 正式版時間間隔：48 小時
- 內測版時間間隔：30 分鐘
- 測試時可手動調整系統時間以加速測試

---

### 0.15 多次上傳持久化數據更新驗證（包含 Retry 和手動錄影）
**測試目標**：驗證多次上傳至 Cloud Storage 時（包含 retry 成功和手動錄影）所有上傳都被正確更新到持久化數據

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 連續上傳多個 snapshot 和 video 至 Cloud Storage（如各 5-10 個），包含部分 retry 成功和手動錄影
2. 記錄每個成功上傳的檔案大小和時長（包含 retry 成功後才記錄的）
3. 檢查持久化數據：
   - 每個成功上傳是否都被更新到持久化數據
   - 持久化數據的數量是否正確
   - 持久化數據的資料是否準確
4. 驗證無遺漏或重複記錄
5. 等待 `camera: active` 事件觸發
6. 驗證 Event Properties 包含正確的累計值

**預期結果**：
- 所有成功上傳（包含 retry 成功和手動錄影）都被正確更新到持久化數據
- 持久化數據數量與實際成功上傳數量一致
- 無遺漏記錄
- 無重複記錄
- 每個記錄的資料準確
- `camera: active` 事件的 Event Properties 包含正確的累計值
Test Result： PASS
---

### 0.16 並發上傳持久化數據更新驗證
**測試目標**：驗證並發上傳至 Cloud Storage 時持久化數據更新的正確性

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 同時觸發多個 snapshot 和 video 上傳至 Cloud Storage（如各 5-10 個）
2. 監控並發上傳的處理
3. 檢查持久化數據：
   - 所有並發上傳成功後是否都被更新到持久化數據
   - 持久化數據是否有衝突或錯誤
   - 持久化數據的資料是否準確
4. 驗證並發處理的正確性
5. 等待 `camera: active` 事件觸發
6. 驗證 Event Properties 包含正確的累計值

**預期結果**：
- 所有並發上傳成功後都被正確更新到持久化數據
- 無持久化數據衝突或錯誤
- 持久化數據的資料準確
- 並發處理機制正確
- 無資料遺失或損壞
- `camera: active` 事件的 Event Properties 包含正確的累計值
Test Result： PASS
---

## 1. 持久化數據與 Event Properties 整合測試

### 1.1 持久化數據與 Event Properties 一致性驗證
**測試目標**：驗證持久化數據與 `camera: active` 事件中 Event Properties 的一致性

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- Analytics 追蹤系統已啟用

**測試步驟**：
1. 在週期內（自上次上報以來）上傳多個 snapshot 和 video 至 Cloud Storage
2. 記錄持久化數據的值：
   - `period_snapshot_count`
   - `period_snapshot_size_kb`
   - `period_video_count`
   - `period_video_duration_sec`
   - `period_video_size_kb`
3. 觸發 `camera: active` 事件上報
4. 檢查 `camera: active` 事件的 Event Properties 值
5. 比對持久化數據與 Event Properties 的一致性

**預期結果**：
- 持久化數據與 Event Properties 完全一致
- 所有 5 個屬性的值在持久化數據和 Event Properties 中一致
- 無資料不一致或錯誤
Test Result： PASS
---



## 2. 錯誤處理與邊界測試

### 2.1 持久化數據更新失敗處理驗證
**測試目標**：驗證持久化數據更新失敗時的處理機制

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 可模擬持久化數據更新失敗（如 DVR api 連線失敗）

**測試步驟**：
1. 上傳 snapshot/video 至 Cloud Storage 成功
2. 模擬持久化數據更新失敗（如 DVR api 連線失敗）
3. 觀察錯誤處理機制：
   - 是否有重試機制
   - 是否有暫存機制（queue）
   - 錯誤訊息是否清晰
4. 恢復持久化數據系統
5. 驗證暫存的更新是否正確處理
6. 驗證後續上傳的持久化數據更新是否正常

**預期結果**：
- 持久化數據更新失敗時有適當的錯誤處理
- 如有重試機制，自動重試更新
- 如有暫存機制，更新暫存並在系統恢復後處理
- 錯誤訊息清晰且有用
- 無資料遺失
- 系統恢復後更新正確處理
Test Result： PASS
---

### 2.2 持久化數據資料一致性驗證
**測試目標**：驗證持久化數據與實際上傳資料的一致性

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 上傳多個 snapshot 和 video 至 Cloud Storage（包含 retry 成功和手動錄影）
2. 記錄每個成功上傳的實際資料（檔案大小、時長等）
3. 檢查持久化數據中的資料
4. 比對實際資料與持久化數據的一致性
5. 驗證資料無衝突或錯誤
6. 等待 `camera: active` 事件觸發
7. 驗證 Event Properties 與實際資料的一致性

**預期結果**：
- 持久化數據與實際資料一致
- Event Properties 與實際資料一致
- 無資料衝突或錯誤
- 資料完整性正確
- 無資料遺失或損壞
Test Result： PASS
---

### 2.3 持久化數據邊界條件測試
**測試目標**：驗證邊界條件下的持久化數據更新處理

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 測試極小檔案上傳（如 < 1KB）：
   - 上傳極小的 snapshot 和 video
   - 驗證持久化數據正確更新（可能為 0 或接近 0）
2. 測試極大檔案上傳（如 > 100MB）：
   - 上傳極大的 snapshot 和 video
   - 驗證持久化數據正確更新（單位：KB）
3. 測試極短時長 video（如 < 1 秒）：
   - 上傳極短時長的 video
   - 驗證 `period_video_duration_sec` 正確更新（可能為 0 或接近 0）
4. 測試極長時長 video（如 > 1 小時）：
   - 上傳極長時長的 video
   - 驗證 `period_video_duration_sec` 正確更新（單位：秒）
5. 驗證持久化數據的處理
6. 等待 `camera: active` 事件觸發
7. 驗證 Event Properties 正確反映邊界條件

**預期結果**：
- 極小檔案正確更新到持久化數據
- 極大檔案正確更新到持久化數據（單位：KB）
- 極短時長 video 正確更新 `period_video_duration_sec`
- 極長時長 video 正確更新 `period_video_duration_sec`（單位：秒）
- 邊界條件正確處理
- Event Properties 正確反映邊界條件
- 無異常或錯誤
Test Result： PASS
---

### 2.4 `camera: active` 事件觸發時機驗證
**測試目標**：驗證 `camera: active` 事件在正確的時機觸發（相機心跳上報）

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號
- 了解相機心跳上報週期

**測試步驟**：
1. 在週期內上傳多個 snapshot 和 video 至 Cloud Storage
2. 監控 `camera: active` 事件的觸發時機：
   - 是否在相機心跳上報時觸發
   - 觸發頻率是否符合預期
3. 驗證事件觸發時機是否符合預期
4. 測試多次上報驗證時機一致性
5. 檢查 Event Properties 是否在每次 `camera: active` 事件中正確包含

**預期結果**：
- `camera: active` 事件在相機心跳上報時正確觸發
- 事件觸發時機一致且可預測
- Event Properties 在每次事件中正確包含
- 時機符合業務邏輯要求
Test Result： PASS
---

## 3. 效能與穩定性測試

### 3.1 大量上傳持久化數據更新效能測試
**測試目標**：驗證大量 snapshot/video 上傳時持久化數據更新的效能

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 連續上傳多個 snapshot 和 video 至 Cloud Storage（如各 10-20 個）
2. 監控持久化數據更新的處理：
   - 更新速度
   - 系統資源使用（CPU、記憶體）
   - 更新成功率
3. 驗證所有成功上傳的資料都被正確更新到持久化數據
4. 檢查持久化數據系統是否有效能下降
5. 等待 `camera: active` 事件觸發
6. 驗證 Event Properties 是否及時包含正確的累計值

**預期結果**：
- 大量上傳時持久化數據更新成功完成
- 持久化數據更新速度在可接受範圍內
- 系統資源使用正常
- 無明顯效能下降
- 所有成功上傳的資料都被正確更新到持久化數據
- Event Properties 及時包含正確的累計值
- 無記憶體洩漏或資源耗盡
Test Result： PASS
---

### 3.2 並發上傳持久化數據更新穩定性測試
**測試目標**：驗證並發上傳時持久化數據更新的穩定性

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 同時觸發多個 snapshot 和 video 上傳至 Cloud Storage（如各 5-10 個）
2. 監控並發上傳的持久化數據更新處理
3. 驗證所有成功上傳的資料都被正確更新到持久化數據
4. 檢查持久化數據是否有衝突或錯誤
5. 驗證累計邏輯正確
6. 等待 `camera: active` 事件觸發
7. 驗證 Event Properties 包含正確的累計值

**預期結果**：
- 並發上傳時持久化數據更新成功處理
- 無持久化數據衝突或錯誤
- 所有成功上傳的資料都被正確更新到持久化數據
- 累計邏輯正確
- Event Properties 包含正確的累計值
- 無系統不穩定或崩潰
Test Result： PASS
---

### 3.3 長時間運行成本記錄穩定性測試
**測試目標**：驗證長時間運行下成本記錄的穩定性

**前置條件**：
- 使用符合 Cloud Storage 條件的帳號

**測試步驟**：
1. 持續上傳 footages 至 Cloud Storage 一段時間（如 1-2 小時）
2. 定期檢查成本記錄系統狀態
3. 監控記憶體使用和資源消耗
4. 驗證成本記錄功能持續正常運作
5. 檢查成本記錄是否有遺漏或錯誤
6. 檢查是否有記憶體洩漏或效能下降

**預期結果**：
- 長時間運行下成本記錄穩定
- 無記憶體洩漏
- 成本記錄功能持續正常運作
- 無成本記錄遺漏或錯誤
- 無效能下降
- 無系統崩潰或異常
Test Result： PASS
---

## 4. 相容性測試

### 4.1 跨平台成本記錄驗證
**測試目標**：驗證不同平台上成本記錄的一致性

**前置條件**：
- 準備 iOS 和 Android 測試設備

**測試步驟**：
1. 在 iOS 設備上上傳 footages 至 Cloud Storage
2. 檢查 iOS 平台的成本記錄
3. 在 Android 設備上上傳 footages 至 Cloud Storage
4. 檢查 Android 平台的成本記錄
5. 比較兩平台的成本記錄一致性
6. 驗證成本記錄在兩平台都正常運作

**預期結果**：
- iOS 和 Android 平台成本記錄正常運作
- 兩平台成本記錄格式一致
- 成本記錄資料一致
- 無平台特定問題
Test Result： PASS
---

### 4.2 不同 App 版本成本記錄相容性
**測試目標**：驗證不同 App 版本成本記錄的相容性

**前置條件**：
- 準備不同版本的 App

**測試步驟**：
1. 使用舊版本 App 上傳 footages 至 Cloud Storage
2. 檢查舊版本的成本記錄
3. 升級到新版本
4. 上傳 footages 至 Cloud Storage
5. 檢查新版本的成本記錄
6. 驗證成本記錄格式相容性
7. 檢查是否有相容性問題

**預期結果**：
- 舊版本 App 成本記錄正常（如有支援）
- 升級後成本記錄正常運作
- 成本記錄格式相容
- 無相容性問題
- 歷史成本記錄資料正確保留
Test Result： PASS
---

## 📊 測試總結

### 測試覆蓋範圍
- ✅ 成本記錄邏輯測試（包含 Event Properties 測試）
- ✅ Event Properties 完整性、正確性、格式驗證
- ✅ Event Properties 邊界值、週期累計邏輯、Analytics 傳遞驗證
- ✅ Event Properties 重置時機點驗證（每次上報後、相機端登出、超過時間間隔）
- ✅ 成本追蹤測試
- ✅ 錯誤處理與邊界測試
- ✅ 效能與穩定性測試
- ✅ 相容性測試


### 關鍵測試項目
1. **成本記錄邏輯**：上傳至 Cloud Storage 時的成本記錄觸發、時機、內容完整性
2. **Event Properties**：5 個事件屬性的完整性、值正確性、格式驗證、邊界值處理、週期累計邏輯、重置時機點、Analytics 傳遞
   - `period_snapshot_count`：週期內 snapshot 數量
   - `period_snapshot_size_kb`：週期內 snapshot 總大小（KB）
   - `period_video_count`：週期內 video 數量
   - `period_video_duration_sec`：週期內 video 總時長（秒）
   - `period_video_size_kb`：週期內 video 總大小（KB）
3. **Event Properties 重置時機點**：
   - 每次上報後重置
   - 相機端登出時重置（包含切換至 viewer）
   - 超過時間間隔時重置（正式版 48 小時，內測版 30 分鐘）
4. **使用量追蹤**：Cloud Storage 使用量正確追蹤（檔案大小、儲存時間等）
5. **成本計算**：根據使用量計算 Cloud Storage 成本
6. **錯誤處理**：成本記錄失敗、資料一致性、邊界條件處理

### 風險評估
- **高風險項目**：成本記錄邏輯準確性、Event Properties 週期累計邏輯正確性、Event Properties 值正確性、Event Properties 重置時機點正確性、成本計算準確性、使用量追蹤完整性、Event Properties 在 Analytics 系統中的傳遞
- **中風險項目**：大量上傳時成本記錄效能、並發上傳成本記錄穩定性、Event Properties 格式驗證、邊界值處理、時間間隔判斷邏輯
- **低風險項目**：Event Properties 屬性名稱拼寫

### 測試建議
1. **優先測試 Event Properties**：確保 5 個必要屬性（period_snapshot_count、period_snapshot_size_kb、period_video_count、period_video_duration_sec、period_video_size_kb）正確記錄和傳遞
2. **優先測試 Event Properties 重置時機點**：確保在正確的時機點（每次上報後、相機端登出、超過時間間隔）正確重置
3. 優先測試成本記錄邏輯，確保上傳至 Cloud Storage 時正確記錄成本
4. 重點驗證 Event Properties 的週期累計邏輯，確保 snapshot 和 video 的數量、大小、時長正確累計
5. 重點驗證 Event Properties 的值正確性和格式，確保與實際資料一致（單位：KB、秒）
6. 重點驗證時間間隔判斷邏輯（正式版 48 小時，內測版 30 分鐘），確保超過時間間隔時正確重置
7. 執行大量上傳和並發上傳測試，驗證成本記錄和 Event Properties 的效能和穩定性
8. 驗證 Event Properties 正確傳遞到 Analytics 系統（Amplitude、Firebase 等），確保所有 5 個屬性都正確傳遞
9. 測試各種錯誤情況下的成本記錄和 Event Properties 處理機制
