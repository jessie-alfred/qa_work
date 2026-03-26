This document outlines a project aimed at optimizing subscription conversion rates and lifetime value through differentiated pricing and packaging strategies for various markets.

- The subscription strategy includes offering a hidden low-price plan for price-sensitive users in T1/T2 markets and a low entry price in T3 markets to encourage initial subscriptions.
- Key objectives include increasing subscription incentives, market penetration, and cost optimization, with a focus on maintaining profitability even at lower price points.
- Changes include reducing free user local storage from 7 days to 2 days for new users and introducing a 2-day cloud storage for Premium Lite users.
- The project involves implementing new entitlements, paywall designs, and appcues communication strategies to support the differentiated subscription plans.


以下是 Premium Lite 相關功能重點整理（對照 Free / Standard / Plus）：

### 1. 定價（依市場而異）
- T1：US 等 → **$3.99/月, $23.99/年**
- T2：部分中價市場 → **$2.99/月, $17.99/年**
- T3：BR/IN/TR 等 → **$0.99/月, $5.99/年**

### 2. 影像直播（Live）
- 解析度：**240p / 480p / 720p**
- 多人觀看：**最多 3 位 multi-viewers**
- 和 Standard 相同，但比 Free 多 480p / 720p、也多 multi-viewers

### 3. 偵測功能（Detection）
- **有：**
  - Motion Detection & Alert
  - Person / Sound / Pet / Vehicle Detection & Alert
- **沒有：**
  - Context Awareness Detection（這個只有 Plus 有）

### 4. 錄影與雲端儲存（Recording）
- 錄影類型：**Event 錄影**
- **Cloud storage：2 天**
  - 解析度：錄影最高 **720p**
- Playback：
  - 可回放時長：最多 **8 小時**
  - Playback 解析度：**720p**

（對照）
- Free：Local 2 天、最高 240p、Playback 240p
- Standard：Cloud 14 天、720p、Playback 8 小時
- Plus：Cloud 30 天、720p、Playback 無上限

### 5. 錄影瀏覽權限（Recording View Access）
- Event playback：**YES**
- 連續錄影 Continuous Recording：**NO**（需升級 Standard 以上）

### 6. Camera 數量限制
- Premium Lite：**最多 2 台相機**
- Free：最多 2 台
- Standard：最多 4 台
- Plus：不限台數

### 7. 相關技術設定（跟功能體驗直接相關）
- Premium Lite 會有新 entitlement：
  - `event:storage:2d` → 給 2 天 Cloud event storage
  - `cr:playback` → 控制 CR Playback 是否解鎖
- 若沒有 `cr:playback` entitlement，就會看到 **CR Playback paywall 遮罩**，並透過 Appcues 走 upsell 流程
- CR Playback 遮罩 CTA 使用 `viewer_tier_upgrade_unlock`（Unlock），文案會引導升級到更高階方案
