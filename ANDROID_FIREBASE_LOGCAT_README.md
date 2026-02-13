# Android / iOS Firebase 事件 log 擷取與驗證

用 **Android** 的 `adb logcat` 或 **iOS** 的 `idevicesyslog` 擷取 app 輸出的 `[Alfred][Event]` Firebase 事件 log，並依規則或 `firebase_event_specs/*.md` 驗證事件是否正確送出。

## 前置條件

**Android**
- 已安裝 [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)（含 `adb`）
- 裝置已接上並 `adb devices` 可看到裝置

**iOS**
- 已安裝 [libimobiledevice](https://libimobiledevice.org/)（`brew install libimobiledevice`）
- iOS 裝置以 USB 連接 Mac，必要時在裝置上點「信任此電腦」
- 執行 `idevicesyslog` 可看到裝置 log 即表示環境正常

**共通**
- App 為 **Development Build**，會輸出 `[Alfred][Event]` 開頭的 log（格式為其後接 JSON）

## Log 格式範例

```
[Alfred][Event] {"type":"firebase","event_name":"event_play","attributes":{"entry":"event list","event_id":"698ad62d955c638b8b143e46","event_tags":"motion","event_source":"cloud"}}
```

## 使用方式

### 1. 擷取事件到檔案（建議先清 logcat）

```bash
# 清掉舊 log，再擷取（可另開終端操作 app）
adb logcat -c
python android_firebase_logcat.py capture --output events.jsonl
# 或只抓 100 筆後自動結束
python android_firebase_logcat.py capture --output events.jsonl --limit 100
```

### 2. 即時顯示事件（不寫檔）

```bash
python android_firebase_logcat.py stream
```

### 3. 驗證：依規則檢查事件

**從已擷取的 JSONL 檔案驗證：**

```bash
python android_firebase_logcat.py verify --rules android_firebase_event_rules_example.json --input events.jsonl
```

**即時從 logcat 驗證（需手動 Ctrl+C 結束，或設 timeout）：**

```bash
adb logcat -c
# 操作 app 觸發事件後…
python android_firebase_logcat.py verify --rules android_firebase_event_rules_example.json --timeout 30
```

- 通過：stderr 印出 `[PASS]`、最後 `All rules passed.`，exit code 0  
- 失敗：stderr 印出 `[FAIL]`，exit code 1，可依此做自動化測試

## 驗證規則格式（JSON）

規則放在一個 JSON 檔，可為單一物件或 `{"rules": [...]}` 陣列。

每條規則可包含：

| 欄位 | 說明 |
|------|------|
| `name` | 規則名稱（驗證輸出時顯示） |
| `event_name` | 事件名稱需完全符合 |
| `event_name_regex` | 或用正則匹配事件名稱（與 `event_name` 二擇一） |
| `type` | 可選，例如 `"firebase"` |
| `attributes` | 可選，key-value 需完全符合；值可為 `"regex:..."` 表示用正則匹配 |
| `attributes_contains` | 可選，列出必須存在的 key（值為 true 表示該 key 須存在且非空） |
| `match_once` | 可選，預設 true：每條規則只匹配一筆事件 |

範例見 `android_firebase_event_rules_example.json`。

## 建議流程（手動測試）

1. `adb logcat -c` 清 log  
2. 執行 `python android_firebase_logcat.py capture -o events.jsonl`（或加 `--limit`）  
3. 在裝置上操作 app，觸發要驗證的流程（例如從 event list 點事件播放）  
4. 停止 capture（Ctrl+C）  
5. 執行 `python android_firebase_logcat.py verify -r android_firebase_event_rules_example.json -i events.jsonl`  
6. 依輸出調整規則或確認行為

## 依 firebase_event_specs 驗證（verify-specs）

等同在 command line 跑 `adb logcat -v time | grep -E "\[Alfred\]\[Event\].*firebase|firebase.*\[Alfred\]\[Event\]"`，並把擷取到的事件依 `firebase_event_specs/*.md` 做規範驗證（檢查必填屬性是否都有帶）。

```bash
# 即時擷取並驗證（手動 Ctrl+C 結束）
python android_firebase_logcat.py verify-specs

# 擷取 30 秒後自動結束並驗證
python android_firebase_logcat.py verify-specs --timeout 30

# 從已擷取的 JSONL 驗證（不跑 logcat）
python android_firebase_logcat.py verify-specs --input events.jsonl

# 將驗證結果寫入檔案
python android_firebase_logcat.py verify-specs --timeout 30 --output verify_result.txt

# iOS 裝置（需先安裝 libimobiledevice、裝置接 USB）
python android_firebase_logcat.py verify-specs --platform ios --timeout 30 --output verify_result.txt
python android_firebase_logcat.py capture --platform ios --output events_ios.jsonl

# 錄製期間同時錄製裝置畫面（僅 Android，檔名同結果 .mp4，輔助參考）
python android_firebase_logcat.py verify-specs --timeout 30 --output verify_result.txt --record-screen
```

- 通過：stderr 顯示「所有事件均符合 firebase_event_specs 規範。」，exit code 0  
- 失敗：stderr 列出不符合的事件與缺少的必填屬性，exit code 1  
- 使用 `--output` / `-o` 可將相同內容寫入指定檔案，方便留存或 CI 使用。
- 使用 `--record-screen` 會在擷取期間同時錄製 Android 裝置畫面，產出與結果同檔名的 `.mp4` 作為輔助參考。

規範來自 `firebase_event_specs/` 目錄下的 `*_event_spec.md`，每個事件的 **Mandatory** 屬性必須存在且非空。

## 在自動化測試中使用

- 在測試流程開始前清 logcat、啟動 `capture` 寫入暫存檔，或直接 `verify --timeout N`  
- 操作完成後對暫存檔做 `verify`，或依 timeout 結束後的 verify 結果判斷 pass/fail  
- 依 exit code 決定測試通過與否
