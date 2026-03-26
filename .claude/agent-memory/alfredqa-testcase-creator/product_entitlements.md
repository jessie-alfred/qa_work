---
name: Alfred 訂閱方案 Entitlement 與功能對照
description: Premium Lite / Standard / Plus 各 tier 的 entitlement key、功能邊界、CR Playback，供測項產生時快速比對
type: project
---

## Tier 功能對照表

| 功能 | Free | Premium Lite | Standard | Plus |
|------|------|------|------|------|
| 直播解析度 | 240p | 240p / 480p / 720p | 240p / 480p / 720p | 240p / 480p / 720p / 1080p |
| Multi-viewer 人數 | 1 | 3 | 3 | 3 |
| 相機數量 | 2 | 2 | 4 | 無限 |
| Event Cloud Storage | ✗（Local 2天 新用戶 / 7天 舊用戶） | 2 天 Cloud | 14 天 Cloud | 30 天 Cloud |
| Playback 解析度 | 240p | 720p | 720p | 720p |
| Motion / Person / Sound / Pet / Vehicle Detection | Motion only | ✅ | ✅ | ✅ |
| Context Awareness Detection | ✗ | ✗ | ✗ | ✅ |
| CR Playback 播放 | ✗ (顯示遮罩)| ✗（顯示遮罩） | ✅ | ✅ |

## 關鍵 Entitlement Keys

| Key | 說明 | 適用 Tier |
|-----|------|------|
| `event:storage:2d` | 2 天 Cloud Event Storage | Premium Lite |
| `event:storage:14d` | 14 天 Cloud Event Storage | Standard |
| `event:storage:30d` | 30 天 Cloud Event Storage | Plus |
| `cr:playback` | CR Playback 解鎖 | Standard / Plus |
| `cr:duration:unlimited` | 連續錄影時長無上限 | Plus |
