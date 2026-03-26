---
name: 已產出測試案例清單
description: 各 CAMERA ticket / 功能已產出的測案檔案，供迴歸參考與避免重工
type: project
---

## 已完成測試案例

| 功能 / Ticket | 測案檔案 | 測項數 | 核心功能範圍 | 產出日期 |
|------|------|------|------|------|
| Premium Lite | `test_case/PremiumLite_TestCase.md` | 57 | Entitlement (event:storage:2d / cr:playback)、CR Playback Paywall (Appcues)、Membership 轉換、定價 T1/T2/T3 | 2026-03-26 |
| CAMERA-6186 | `test_case/done/CAMERA-6186_TestCase.md` | - | - | - |
| CAMERA-6225 | `test_case/done/CAMERA-6225_Firebase_Core_Events_TestCase.md` | - | Firebase Core Events | - |
| CAMERA-6350 | `test_case/done/CAMERA-6350 Cloud Storage Cost Tracking.md` | - | Cloud Storage 費用追蹤 | - |
| CAMERA-6423 | `test_case/done/CAMERA-6423_TestCase.md` | - | - | - |
| CAMERA-6504 | `test_case/done/CAMERA-6504_TestCase.md` | - | - | - |

## 使用說明

- 產生新測案前，先查此清單確認是否有重疊功能可作為回歸基準
- 更新舊功能測案時，在此更新對應欄位的測項數與日期
