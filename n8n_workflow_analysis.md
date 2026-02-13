# n8n Workflow 分析：build_number undefined 問題

## 問題描述

在 workflow `Remote config - iOS NewHelpCenterURL` 中，`Update Value - NewHelpCenterURL` 節點從 `parse-version-build-number` 節點取得 `build_number` 時，可能出現 `undefined` 的情況。

## 相關節點配置

### 1. parse-version-build-number 節點
- **類型**: `@n8n/n8n-nodes-langchain.openAi`
- **模型**: GPT-4O-MINI
- **配置**: `jsonOutput: true`
- **輸入訊息**: 
  ```
  抽取 {{ $json.values[0].name }} 字串，設為二個參數
  1. version : 曆年制的版本號，例如 2025.xx.xx 
  2. build number : 取最前面4位數，如果沒有 build number 就使用預設值 99999
  ```

### 2. Update Value - NewHelpCenterURL 節點
- **類型**: `n8n-nodes-base.code`
- **取得 build_number 的方式**:
  ```javascript
  const build_number = $('parse-version-build-number')
    .first()
    .json
    .message
    .content
    .build_number;
  ```

## 可能導致 build_number 為 undefined 的原因

### 原因 1: OpenAI 節點輸出結構不穩定 ⚠️ 高風險

**問題**:
- OpenAI langchain 節點在 `jsonOutput: true` 時，輸出結構可能因模型回應而異
- 如果 OpenAI 返回的 JSON 格式不符合預期，`message.content` 可能是：
  - 字串而非物件
  - 缺少 `build_number` 欄位
  - 結構完全不同

**可能的輸出結構變異**:
```javascript
// 預期結構
{
  message: {
    content: {
      version: "2025.1.0",
      build_number: "1234"
    }
  }
}

// 可能的變異 1: content 是字串
{
  message: {
    content: '{"version":"2025.1.0","build_number":"1234"}'
  }
}

// 可能的變異 2: 缺少 build_number
{
  message: {
    content: {
      version: "2025.1.0"
      // build_number 不存在
    }
  }
}

// 可能的變異 3: 結構完全不同
{
  message: {
    content: {
      version_number: "2025.1.0",
      build: "1234"
    }
  }
}
```

### 原因 2: 節點執行失敗或無輸出 ⚠️ 中風險

**問題**:
- 如果 `parse-version-build-number` 節點執行失敗
- 如果節點沒有產生任何輸出
- `$('parse-version-build-number').first()` 可能返回 `undefined` 或空物件

**檢查方式**:
```javascript
const parseNode = $('parse-version-build-number').first();
if (!parseNode || !parseNode.json) {
  // 節點執行失敗或無輸出
}
```

### 原因 3: 路徑存取錯誤 ⚠️ 中風險

**問題**:
- 如果 `message` 不存在
- 如果 `message.content` 不存在
- 如果 `message.content` 不是物件

**檢查方式**:
```javascript
const parseNode = $('parse-version-build-number').first();
if (!parseNode?.json?.message?.content) {
  // 路徑不存在
}
```

### 原因 4: OpenAI 回應格式不符合要求 ⚠️ 高風險

**問題**:
- OpenAI 可能無法正確解析版本號
- OpenAI 可能返回錯誤的 JSON 格式
- OpenAI 可能返回包含額外欄位的 JSON，但缺少 `build_number`

**範例**:
```javascript
// OpenAI 可能返回
{
  message: {
    content: {
      version: "2025.1.0",
      error: "無法解析 build number"
      // build_number 不存在
    }
  }
}
```

### 原因 5: 版本號格式不符合預期 ⚠️ 低風險

**問題**:
- 如果 JIRA 版本號格式與預期不符
- OpenAI 可能無法正確提取 build_number
- 例如：版本號為 "iOS 2025.1.0" 而非 "2025.1.0"

## 建議的解決方案

### 方案 1: 增加防禦性檢查和錯誤處理 ⭐ 推薦

```javascript
// 從前一個 HTTP Request 節點抓完整回應
const items = $input.all();

// 從 parse-version-build-number 節點取得 build_number（增加防禦性檢查）
const parseNode = $('parse-version-build-number').first();

if (!parseNode || !parseNode.json) {
  throw new Error('parse-version-build-number 節點執行失敗或無輸出');
}

// 檢查 message 是否存在
if (!parseNode.json.message) {
  throw new Error('parse-version-build-number 節點輸出缺少 message 欄位');
}

// 處理 content 可能是字串或物件的情況
let content = parseNode.json.message.content;
if (typeof content === 'string') {
  try {
    content = JSON.parse(content);
  } catch (e) {
    throw new Error(`無法解析 content JSON: ${e.message}`);
  }
}

if (typeof content !== 'object' || content === null) {
  throw new Error('content 不是有效的物件');
}

// 取得 build_number，如果不存在則使用預設值
const build_number = content.build_number || content.buildNumber || '99999';

// 驗證 build_number 是否有效
if (!build_number || build_number === 'undefined' || build_number === 'null') {
  console.warn('build_number 無效，使用預設值 99999');
  build_number = '99999';
}

// 後續處理...
```

### 方案 2: 使用 Optional Chaining 和 Nullish Coalescing

```javascript
const build_number = $('parse-version-build-number')
  .first()
  ?.json
  ?.message
  ?.content
  ?.build_number 
  ?? '99999';

// 如果 content 是字串，需要先解析
const parseNode = $('parse-version-build-number').first();
let content = parseNode?.json?.message?.content;

if (typeof content === 'string') {
  try {
    content = JSON.parse(content);
  } catch (e) {
    content = null;
  }
}

const build_number = content?.build_number ?? content?.buildNumber ?? '99999';
```

### 方案 3: 改進 OpenAI 節點的提示詞

在 `parse-version-build-number` 節點的提示詞中，明確要求 JSON 格式：

```
請從以下版本號字串中抽取資訊，並以 JSON 格式返回：
版本號: {{ $json.values[0].name }}

要求：
1. 必須返回有效的 JSON 格式
2. 必須包含以下兩個欄位：
   - version: 曆年制的版本號（例如：2025.1.0）
   - build_number: 取最前面4位數，如果沒有 build number 就使用 "99999"
3. JSON 格式範例：
   {
     "version": "2025.1.0",
     "build_number": "1234"
   }

請確保返回的 JSON 格式正確，且 build_number 欄位一定存在。
```

### 方案 4: 在 If 節點前增加驗證

在 `If-JIRA Release build num check` 節點前，增加一個驗證節點：

```javascript
// 驗證 build_number 是否存在
const parseNode = $('parse-version-build-number').first();
const content = parseNode?.json?.message?.content;

if (!content || typeof content !== 'object') {
  throw new Error('無法取得有效的 build_number');
}

if (!content.build_number && !content.buildNumber) {
  throw new Error('build_number 欄位不存在');
}

return [{
  json: {
    ...parseNode.json,
    build_number_valid: true
  }
}];
```

## 測試建議

### 測試案例 1: 正常情況
- 輸入: JIRA 版本號包含 build number
- 預期: `build_number` 正確取得

### 測試案例 2: 缺少 build number
- 輸入: JIRA 版本號不包含 build number
- 預期: `build_number` 為 "99999"

### 測試案例 3: OpenAI 返回字串格式
- 輸入: OpenAI 返回的 content 是 JSON 字串
- 預期: 正確解析字串並取得 `build_number`

### 測試案例 4: OpenAI 節點執行失敗
- 輸入: parse-version-build-number 節點執行失敗
- 預期: 拋出明確的錯誤訊息

### 測試案例 5: 結構不符合預期
- 輸入: OpenAI 返回的 JSON 結構不符合預期
- 預期: 使用預設值或拋出錯誤

## 監控建議

1. **記錄日誌**: 在 `Update Value - NewHelpCenterURL` 節點中記錄 `build_number` 的值
2. **錯誤通知**: 當 `build_number` 為 `undefined` 時，發送 Slack 通知
3. **驗證檢查**: 在更新 Remote Config 前，驗證 `build_number` 是否有效

## 結論

`build_number` 可能為 `undefined` 的主要原因：
1. **OpenAI 節點輸出結構不穩定**（最可能）
2. **節點執行失敗或無輸出**
3. **路徑存取錯誤**
4. **OpenAI 回應格式不符合要求**

**建議優先實施方案 1**，增加完整的防禦性檢查和錯誤處理，確保 workflow 的穩定性。
