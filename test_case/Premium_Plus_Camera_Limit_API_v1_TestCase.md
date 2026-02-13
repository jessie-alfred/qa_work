# Premium Plus Camera Limit API v1 測試案例

## 文件資訊

| 項目 | 說明 |
|------|------|
| **規格來源** | [Premium Plus Camera Limit API - API 端點規格](https://alfredlabs.atlassian.net/wiki/spaces/PD/pages/4325113860/Premium+Plus+Camera+Limit+API#API-%E7%AB%AF%E9%BB%9E%E8%A6%8F%E6%A0%BC) |
| **最後更新** | 2025-01-27 |
| **涵蓋 API** | GET /device/v1/license、GET /device/v1/license/status、POST /device/v1/license、DELETE /device/v1/license/:jid |

---

## 詞彙與回應格式對照

### 詞彙

| 詞彙 | 說明 |
|------|------|
| **License** | 允許裝置作為 Camera 運作的授權 |
| **JID** | Jabber ID，裝置的唯一識別碼（格式如 `user@domain/device123`） |
| **Entitlement** | 用戶的 camera:limit 額度（1 / 3 / unlimited 或無） |

### 統一回應格式（規格）

| HTTP | status_code 範例 | 用途 |
|------|------------------|------|
| 200 | `succeeded` | 業務處理成功 |
| 404 | `not_found` | 資源不存在 |
| 422 | `quota_exceeded`、`already_assigned`、`no_permission` | 業務邏輯失敗 |
| 423 | `locked` | 配額變動，請重試 |
| 401 | `error` | 認證失敗 |
| 403 | `error` / `no_permission` | 無權限 |
| 500 | `error` | 伺服器錯誤 |

---

## 1. GET /device/v1/license（查詢 License 額度）API 測試案例

### 1.1 認證與成功回應

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-LIC-001 | 有效 JWT 查詢額度 | `GET /device/v1/license`，Header: `Authorization: Bearer <valid_jwt>` | 從 Entitlement 取 total_limit，從 DB 取 used_count、devices | HTTP 200，`status_code: succeeded`，`data` 含 `total_limit`、`used_count`、`available_count`、`devices` |
| P1-LIC-002 | 額度結構正確 | 同上，用戶有 2 台已分配 | `data.total_limit`、`data.used_count`、`data.available_count` 為數字；`data.devices` 為陣列 | `data.devices[].jid`、`data.devices[].assigned_at`（ISO 8601） |
| P1-LIC-003 | 無已分配裝置時 | 用戶額度 > 0 且 used_count = 0 | `data.used_count: 0`，`data.available_count` = total_limit，`data.devices: []` | HTTP 200，`status_code: succeeded` |
| P1-LIC-004 | unlimited 額度用戶 | entitlement 為 `camera:limit:unlimited` | total_limit 為無上限表示，available_count 不受限 | HTTP 200，依規格實作之無上限表示（如特殊值或欄位說明） |

### 1.2 認證與錯誤

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-LIC-005 | 無或無效 JWT | `GET /device/v1/license` 無 Authorization 或 token 無效/過期 | 拒絕請求 | HTTP 401，`status_code: error`，`status_message` 含 Unauthorized / Invalid or expired token |
| P1-LIC-006 | 伺服器錯誤時 | 模擬 Entitlement 或 DB 異常 | 回傳系統錯誤格式 | HTTP 500，`status_code: error`，`status_message` 如 Internal server error |

### 1.3 效能（NFR-3.5）

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期結果 |
|---------|----------|----------|----------|----------|
| P1-LIC-007 | 查詢回應時間 | `GET /device/v1/license`，正常負載 | P95 回應時間 ≤ 500ms | 可透過監控或壓測驗證 |

---

## 2. GET /device/v1/license/status（檢查裝置 License 分配狀態）API 測試案例

### 2.1 成功回應

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-STS-001 | JWT 含 user_id、jid 且裝置已分配 | `GET /device/v1/license/status`，JWT 含正確 user_id 與 jid | 從 DB 查該 user 的該 jid 是否已分配 | HTTP 200，`status_code: succeeded`，`data.jid`、`data.is_assigned: true`、`data.license_info.assigned_at`（ISO 8601） |
| P1-STS-002 | 裝置未分配 | JWT 含 user_id、jid，該 jid 尚未分配 license | 查詢結果為未分配 | HTTP 200，`data.is_assigned: false`，`data.license_info` 為 null 或無 assigned_at |

### 2.2 認證與錯誤

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-STS-003 | 無或無效 JWT | 無 Authorization 或 token 無效 | 拒絕請求 | HTTP 401，`status_code: error` |
| P1-STS-004 | JWT 缺 jid 或 user_id | token 無法解析出 jid / user_id | 依規格視為參數或認證錯誤 | HTTP 401 或 400，依實作與規格一致 |
| P1-STS-005 | 伺服器錯誤 | 模擬 DB 異常 | 回傳系統錯誤格式 | HTTP 500，`status_code: error` |

---

## 3. POST /device/v1/license（分配 License 給裝置）API 測試案例

### 3.1 成功與正常流程

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-ASN-001 | 額度足夠且裝置未分配 | `POST /device/v1/license`，body: `{ "jid": "user@domain/device789" }`，有效 JWT | 驗證額度 → 寫入 DB → 回傳成功 | HTTP 200，`status_code: succeeded`，`data.jid`、`data.assigned_at`（ISO 8601） |
| P1-ASN-002 | 分配後額度正確 | 同上，原 used_count = 2，total_limit = 5 | 分配後 used_count = 3，available_count = 2 | 再呼叫 GET /device/v1/license 可驗證 |

### 3.2 業務邏輯失敗（HTTP 422）

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-ASN-003 | 額度不足 | 用戶已用滿（used_count = total_limit），POST 新 jid | 不寫入，回傳額度不足 | HTTP 422，`status_code: quota_exceeded`，`status_message` 含額度說明（如 Current limit: 5, Used: 5） |
| P1-ASN-004 | 裝置已分配 | 同一 jid 已存在於 device_licenses | 不重複寫入 | HTTP 422，`status_code: already_assigned`，`status_message` 如 "Device already has a license assigned" |

### 3.3 並發與鎖（HTTP 423）

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-ASN-005 | 配額變動導致需重試 | 並發分配導致配額在處理中變化 | 依規格使用鎖或樂觀控管 | HTTP 423，`status_code: locked`，必要時在 status_message 說明請重試 |

### 3.4 認證與系統錯誤

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-ASN-006 | 無或無效 JWT | POST 無 Authorization 或 token 無效 | 拒絕請求 | HTTP 401，`status_code: error` |
| P1-ASN-007 | body 缺 jid 或格式錯誤 | body 無 `jid` 或非字串 | 驗證失敗 | HTTP 400 或 422，依規格與實作一致 |
| P1-ASN-008 | 伺服器錯誤 | 模擬 Entitlement / DB 異常 | 回傳系統錯誤格式 | HTTP 500，`status_code: error` |

---

## 4. DELETE /device/v1/license/:jid（移除裝置 License）API 測試案例

### 4.1 成功與冪等

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-RMV-001 | 裝置已分配且屬該用戶 | `DELETE /device/v1/license/{jid}`，有效 JWT，該 jid 已分配且屬於 token 的 user | 從 DB 刪除該筆分配，觸發後續 Reload（Pub/Sub → XMPP） | HTTP 200，`status_code: succeeded`，`data.jid` 為被移除的 jid |
| P1-RMV-002 | 冪等：重複刪除同一 jid | 對已移除的 jid 再次呼叫 DELETE | 依規格為 Idempotent，不報錯或回傳與首次成功一致 | HTTP 200 或 404，依規格實作；若 404 則 `status_code: not_found` |

### 4.2 資源不存在（HTTP 404）

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-RMV-003 | 裝置不存在或未分配 | DELETE 的 jid 不在 device_licenses 或非該用戶 | 不刪除 | HTTP 404，`status_code: not_found`，`status_message` 如 "Device not found or not assigned" |

### 4.3 無權限（HTTP 403 / 422）

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-RMV-004 | 裝置屬其他用戶 | JWT 的 user_id 與 jid 所屬 user 不一致 | 拒絕操作 | HTTP 403 或 422，`status_code: no_permission`，`status_message` 如 "No permission" / "No permission to remove this device license" |

### 4.4 認證與系統錯誤

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P1-RMV-005 | 無或無效 JWT | DELETE 無 Authorization 或 token 無效 | 拒絕請求 | HTTP 401，`status_code: error` |
| P1-RMV-006 | 伺服器錯誤 | 模擬 DB 異常 | 回傳系統錯誤格式 | HTTP 500，`status_code: error` |

### 4.5 後續行為（非阻擋 API 成功）

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期結果 |
|---------|----------|----------|----------|----------|
| P1-RMV-007 | 刪除後觸發 Reload | DELETE 成功後 | 經 Pub/Sub 觸發 XMPP 對該 jid 送 Reload（stanza 格式 TBD） | 非同步完成，不影響 DELETE 的 200 回應 |

---

## 5. 統一回應格式與 HTTP 狀態碼

| 測項 ID | 測試情境 | 預期行為 | 預期結果 |
|---------|----------|----------|----------|
| P1-FMT-001 | 所有成功回應 | 含 `status_code`、`status_message`、`data` | 符合規格統一回應格式 |
| P1-FMT-002 | 業務邏輯失敗（422） | 含 `status_code`（quota_exceeded / already_assigned / no_permission）、`status_message` | 不含 `data` 或為 null，依規格 |
| P1-FMT-003 | 資源不存在（404） | 含 `status_code: not_found`、`status_message` | 不含 `data` 或為 null，依規格 |
| P1-FMT-004 | 系統錯誤（401/403/500） | 含 `status_code: error`（或 no_permission）、`status_message` | HTTP 狀態碼與規格一致 |

---

## 6. 跨 API 情境測試

| 測項 ID | 測試情境 | 操作步驟 | 預期結果 |
|---------|----------|----------|----------|
| P1-E2E-001 | 查詢 → 分配 → 再查詢 | 1) GET /device/v1/license 2) POST /device/v1/license { jid } 3) GET /device/v1/license | 1) 取得初始額度 2) 200 succeeded，有 assigned_at 3) used_count +1，devices 含新 jid |
| P1-E2E-002 | 分配 → 移除 → 再分配 | 1) POST /device/v1/license { jid } 2) DELETE /device/v1/license/:jid 3) POST /device/v1/license { jid } | 1) 200 2) 200，額度釋出 3) 200，可再次分配 |
| P1-E2E-003 | 額度用滿後無法再分配 | 1) 重複 POST 直到 used_count = total_limit 2) 再 POST 新 jid | 2) HTTP 422，status_code: quota_exceeded |
| P1-E2E-004 | 已分配裝置重複 POST | 對已分配之 jid 再 POST /device/v1/license | HTTP 422，status_code: already_assigned |
| P1-E2E-005 | 查詢狀態與額度一致 | 1) GET /device/v1/license 記下 devices 2) GET /device/v1/license/status（JWT 含某 device jid） | 該 jid 的 is_assigned 與 GET /license 的 devices 清單一致 |

---

## 7. 測試資料與環境假設

| 項目 | 說明 |
|------|------|
| **認證** | 使用有效 JWT，具 `user_id`；GET /license/status、POST、DELETE 之 jid 需與權限一致 |
| **Entitlement** | 需可模擬 `camera:limit:1`、`camera:limit:3`、`camera:limit:unlimited`、無 entitlement（Legacy） |
| **JID 格式** | `user@domain/device123` 等，與規格及 Auth 解析一致 |
| **資料庫** | device_licenses  collection/table 可重置或隔離，以便驗證 used_count、devices |

---

## 8. 測項 ID 對照表（依 API）

| API | 測項 ID 區間 |
|-----|----------------|
| GET /device/v1/license | P1-LIC-001 ~ P1-LIC-007 |
| GET /device/v1/license/status | P1-STS-001 ~ P1-STS-005 |
| POST /device/v1/license | P1-ASN-001 ~ P1-ASN-008 |
| DELETE /device/v1/license/:jid | P1-RMV-001 ~ P1-RMV-007 |
| 統一回應格式 | P1-FMT-001 ~ P1-FMT-004 |
| 跨 API / E2E | P1-E2E-001 ~ P1-E2E-005 |

---

**文件結束**
