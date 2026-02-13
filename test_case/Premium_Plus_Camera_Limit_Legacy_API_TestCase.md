# Premium Plus Camera Limit - Legacy API 測試案例

## 文件資訊

| 項目 | 說明 |
|------|------|
| **規格來源** | [Premium Plus Camera Limit - Legacy API Spec](https://alfredlabs.atlassian.net/wiki/spaces/PD/pages/4353654790/Premium+Plus+Camera+Limit+-+Legacy+API+Spec) |
| **最後更新** | 2025-01-27 |
| **涵蓋 API** | POST /v2.5/device、GET /v2.5/device/camera、DELETE /v2.5/device/camera/:id、POST /v3.0/device/{jid}/signout |

---

## 詞彙對照

| 詞彙 | 說明 |
|------|------|
| **License** | 允許裝置作為 Camera 運作的授權 |
| **JID** | Jabber ID，裝置的唯一識別碼 |
| **Camera** | 具有錄影功能的裝置類型（`type: 'camera'`） |
| **Viewer** | 僅觀看的裝置類型（`type: 'viewer'`，不受 license 限制） |

---

## 1. POST /v2.5/device（註冊裝置）API 測試案例

### 1.1 License 檢查觸發條件

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P2.5-DEV-001 | `os` 為 `web` 時不觸發 license | `POST /v2.5/device`，body: `{ "os": "web", "type": "camera", ... }` | 不呼叫 License Service，依既有邏輯註冊 | 註冊成功，回應**不含** `is_assigned` 或依既有格式 |
| P2.5-DEV-002 | `os` 為 `embedded` 時不觸發 license | `POST /v2.5/device`，body: `{ "os": "embedded", "type": "camera", ... }` | 不呼叫 License Service，依既有邏輯註冊 | 註冊成功，回應**不含** `is_assigned` 或依既有格式 |
| P2.5-DEV-003 | `os` 為 `android` 且 `type` 為 `camera` 時觸發 license 檢查 | `POST /v2.5/device`，body: `{ "os": "android", "type": "camera", ... }` | 呼叫 License Service 檢查 camera license 額度 | 依額度回傳 `is_assigned: true/false`（見 1.2、1.3） |
| P2.5-DEV-004 | `os` 為 `ios` 且 `type` 為 `camera` 時觸發 license 檢查 | `POST /v2.5/device`，body: `{ "os": "ios", "type": "camera", ... }` | 呼叫 License Service 檢查 camera license 額度 | 依額度回傳 `is_assigned: true/false` |
| P2.5-DEV-005 | `os` 為 `android` 且 `type` 為 `viewer` 時釋放 license | `POST /v2.5/device`，body: `{ "os": "android", "type": "viewer", ... }`（該裝置原為 camera 且曾有 license） | 透過 License Service 移除該裝置的 license | 註冊成功；若原本有 license 則被釋放 |
| P2.5-DEV-006 | `os` 為 `ios` 且 `type` 為 `viewer` 時釋放 license | `POST /v2.5/device`，body: `{ "os": "ios", "type": "viewer", ... }`（該裝置原為 camera 且曾有 license） | 透過 License Service 移除該裝置的 license | 註冊成功；若原本有 license 則被釋放 |
| P2.5-DEV-007 | `type` 為其他類型時不觸發 license | `POST /v2.5/device`，body: `{ "os": "android", "type": "other_type", ... }` | 不執行 license 相關操作 | 註冊成功，依既有邏輯回應 |

### 1.2 額度充足時的行為

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P2.5-DEV-008 | 額度充足時自動分配 license | 用戶有剩餘 camera 額度，註冊 `os: android/ios`, `type: camera` | License Service 回傳額度足夠 → 自動分配 license → 完成註冊 | HTTP 2xx，root 含 `is_assigned: true` |
| P2.5-DEV-009 | License 分配成功後註冊流程正常 | 同上 | 分配成功後仍執行既有註冊邏輯（寫 DB、回傳 device 等） | 回應含完整裝置資訊且 `is_assigned: true` |

### 1.3 額度不足時的行為

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P2.5-DEV-010 | 額度不足時不分配 license | 用戶已用滿 camera 額度，註冊 `os: android/ios`, `type: camera` | License Service 回傳額度不足 | HTTP 2xx，root 含 `is_assigned: false` |
| P2.5-DEV-011 | 額度為 0 時新 camera 註冊 | 用戶額度 0，嘗試註冊新 camera | 不分配 license | `is_assigned: false`，裝置仍可註冊（依規格「允許註冊」） |

### 1.4 重複註冊 / 已有 license 時的行為

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P2.5-DEV-012 | 該裝置已有 license 之重複註冊 | 同一 camera 再次呼叫 `POST /v2.5/device`（相同 JID/識別） | 不重複分配 license，允許註冊繼續 | 註冊成功，root 含 `is_assigned: true` |
| P2.5-DEV-013 | 重複註冊時不產生額外 license 紀錄 | 同上 | License Service 不新增一筆 license，僅沿用既有的 | 查詢該用戶 license 使用數不因重複註冊而增加 |

### 1.5 Camera 切換為 Viewer 時的行為

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P2.5-DEV-014 | 裝置從 Camera 改為 Viewer 時釋放 license | 原為 camera 且已分配 license，改為 `type: viewer` 再呼叫 `POST /v2.5/device` | 透過 License Service 釋放該裝置 license | 註冊成功；該裝置不再佔用 camera 額度 |
| P2.5-DEV-015 | 該裝置沒有 license 時改為 Viewer | 從未分配過或已釋放，改為 `type: viewer` 註冊 | License Service 無紀錄 → 記錄日誌、不視為錯誤 | 註冊成功，無錯誤回應 |

---

## 2. GET /v2.5/device/camera（取得相機清單）API 測試案例

### 2.1 License 額度與狀態

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P2.5-CAM-001 | 回傳含 license 資訊 | `GET /v2.5/device/camera`（已登入用戶） | 呼叫 License Service 查詢用戶額度與各裝置 license 狀態 | 回應中每個裝置具 `license` 欄位 |
| P2.5-CAM-002 | 已分配 license 之裝置格式 | 清單中含已分配 license 的 camera | 每個已分配裝置之 `license` 含 `is_assigned: true` 與 `assigned_at`（ISO 8601） | `license: { "is_assigned": true, "assigned_at": "2024-01-01T10:00:00Z" }` |
| P2.5-CAM-003 | 未分配 license 之裝置格式 | 清單中含未分配 license 的 camera | 該裝置 `license` 為 `is_assigned: false`, `assigned_at: null` | `license: { "is_assigned": false, "assigned_at": null }` |
| P2.5-CAM-004 | 空清單時不報錯 | 用戶無任何 camera | 正常回傳空陣列，若有額度欄位則一併回傳 | `devices: []` 或等效結構 |

### 2.2 回應結構範例

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P2.5-CAM-005 | 回應含既有欄位與 license | `GET /v2.5/device/camera` | 每個 device 保留既有欄位（如 `jid`, `name` 等）並新增 `license` | 結構符合規格範例：`status`, `devices[].jid`, `devices[].name`, `devices[].license` |

### 2.3 效能與查詢方式

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期結果 |
|---------|----------|----------|----------|----------|
| P2.5-CAM-006 | License 狀態使用批量查詢 | `GET /v2.5/device/camera`，用戶有多台 camera | 以批量查詢（如 `$in`）一次取得所有裝置 license 狀態 | 無 N+1 查詢，日誌或監控可驗證 |
| P2.5-CAM-007 | 回應時間增幅 | 同上（多台 camera） | License 查詢與合併不顯著拖慢 API | 相較未加 license 前，增加不超過 100ms（可訂監控/門檻） |

---

## 3. DELETE /v2.5/device/camera/:id（刪除相機）API 測試案例

### 3.1 License 自動釋放

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P3-DEL-001 | 刪除有 license 的 camera 時釋放 | `DELETE /v2.5/device/camera/:id`，該 camera 已分配 license | 執行既有刪除邏輯後，透過 License Service 釋放該裝置 license | HTTP 2xx，刪除成功；該 license 可被其他 camera 使用 |
| P3-DEL-002 | 刪除成功時日誌 | 同上 | 記錄日誌：`License released for device: ${jid}` | 日誌可檢核 |
| P3-DEL-003 | 刪除之裝置無 license（如 Viewer） | 刪除的裝置為 viewer 或從未分配 license | License Service 回傳 NOT_FOUND → 僅記錄日誌，不視為錯誤 | HTTP 2xx，刪除成功 |
| P3-DEL-004 | Legacy 用戶 camera 無 license 紀錄 | 刪除舊版用戶的 camera（可能無 license 紀錄） | License Service 回傳 NOT_FOUND → 記錄日誌，刪除流程仍完成 | HTTP 2xx，刪除成功 |

### 3.2 License 釋放失敗不影響刪除

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P3-DEL-005 | License 釋放失敗（如 Entitlement 不可用） | 模擬 License/Entitlement 錯誤 | 記錄錯誤日誌，**不**讓刪除 API 回傳失敗 | HTTP 2xx，刪除成功；錯誤僅在日誌/監控中可見 |
| P3-DEL-006 | 回應格式維持既有 | 任意成功刪除 | 不新增欄位標記「license 是否釋放」 | 回應格式與現有 DELETE 規範一致 |

### 3.3 向下相容

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P3-DEL-007 | 刪除非 camera 裝置 | `DELETE /v2.5/device/camera/:id` 指向 viewer 或非 camera | 依既有邏輯處理，License 查不到對應記錄 | 與既有行為一致，無異常錯誤 |

---

## 4. POST /v3.0/device/{jid}/signout（裝置登出）API 測試案例

### 4.1 License 自動釋放

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P3-SO-001 | 登出有 license 的 camera 時釋放 | `POST /v3.0/device/{jid}/signout`，該 jid 為已分配 license 的 camera | 執行既有登出邏輯後，透過 License Service 釋放該裝置 license | HTTP 2xx，登出成功；該 license 可被其他 camera 使用 |
| P3-SO-002 | 登出成功時日誌 | 同上 | 記錄日誌：`License released for device: ${jid}` | 日誌可檢核 |
| P3-SO-003 | 登出之裝置無 license（如 Viewer） | 登出的裝置為 viewer 或從未分配 license | License Service 回傳 NOT_FOUND → 僅記錄日誌，不視為錯誤 | HTTP 2xx，登出成功 |
| P3-SO-004 | Legacy 用戶 camera 無 license 紀錄 | 登出舊版用戶的 camera（可能無 license 紀錄） | License Service 回傳 NOT_FOUND → 記錄日誌，登出流程仍完成 | HTTP 2xx，登出成功 |

### 4.2 License 釋放失敗不影響登出

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P3-SO-005 | License 釋放失敗（如 Entitlement 不可用） | 模擬 License/Entitlement 錯誤 | 記錄錯誤日誌，**不**讓登出 API 回傳失敗 | HTTP 2xx，登出成功；錯誤僅在日誌/監控中可見 |
| P3-SO-006 | 回應格式維持既有 | 任意成功登出 | 不新增欄位標記「license 是否釋放」 | 回應格式與現有 signout 規範一致 |

### 4.3 向下相容

| 測項 ID | 測試情境 | 預期請求 | 預期行為 | 預期回應 |
|---------|----------|----------|----------|----------|
| P3-SO-007 | 登出非 camera 裝置 | `POST /v3.0/device/{jid}/signout`，jid 為 viewer 或非 camera | License 查不到對應記錄，依既有邏輯完成登出 | 與既有行為一致，無異常錯誤 |

---

## 5. 跨 API 情境測試（選填）

| 測項 ID | 測試情境 | 操作步驟 | 預期結果 |
|---------|----------|----------|----------|
| P-X-001 | 註冊 → 清單 → 刪除 | 1) POST /v2.5/device 註冊 camera（額度足夠）<br>2) GET /v2.5/device/camera<br>3) DELETE /v2.5/device/camera/:id | 1) `is_assigned: true`<br>2) 該裝置 `license.is_assigned: true`<br>3) 刪除成功，額度釋出 |
| P-X-002 | 註冊 → 登出 | 1) POST /v2.5/device 註冊 camera（額度足夠）<br>2) POST /v3.0/device/{jid}/signout | 1) `is_assigned: true`<br>2) 登出成功，該裝置 license 釋出 |
| P-X-003 | 額度用滿後註冊與清單 | 1) 註冊 N 台 camera 直至額度用滿<br>2) 再註冊第 N+1 台<br>3) GET /v2.5/device/camera | 2) 第 N+1 台 `is_assigned: false`<br>3) 前 N 台 `license.is_assigned: true`，第 N+1 台 `license.is_assigned: false` |
| P-X-004 | Camera 改 Viewer 後額度可重用 | 1) 註冊 camera A（額度 1/1）<br>2) 同裝置改 type=viewer 再註冊<br>3) 註冊新 camera B | 2) A 的 license 釋放<br>3) B 可取得 license（`is_assigned: true`） |

---

## 6. 測試資料與環境假設

- **Authorization**：依現有 /v2.5、/v3.0 所使用之 token 或 session。
- **用戶額度**：需可控制 Entitlement/License Service 之測試環境（或 mock），以製造「額度足夠 / 不足 / 為 0」。
- **裝置識別**：JID 或 `:id` 需與規格一致；重複註冊、Camera/Viewer 切換等需使用可追蹤的裝置識別。
- **Legacy 用戶**：可透過無 Premium/無 license 之測試帳號或 mock 模擬 NOT_FOUND。

---

## 7. 測項 ID 對照表（依 API）

| API | 測項 ID 區間 |
|-----|----------------|
| POST /v2.5/device | P2.5-DEV-001 ~ P2.5-DEV-015 |
| GET /v2.5/device/camera | P2.5-CAM-001 ~ P2.5-CAM-007 |
| DELETE /v2.5/device/camera/:id | P3-DEL-001 ~ P3-DEL-007 |
| POST /v3.0/device/{jid}/signout | P3-SO-001 ~ P3-SO-007 |
| 跨 API | P-X-001 ~ P-X-004 |

---

**文件結束**
