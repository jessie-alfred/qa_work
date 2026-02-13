# 事件追蹤規範：payment_experience_v2

## 事件名稱 (Event Name)

`payment_experience_v2`

## 目的 (Purpose)

Measure the performance of page when the user is attempting to upgrade to premium. It tracks the time required starting from when the user enters the premium payment page to the time the main content actually rendered (the product prices are displayed on the screen).

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| offering_fetched | Mandatory | Number |  | 開啟 paywall，向 RC SDK 取得 offering 的花費時間 (default：-1，需開啟 premium paywall 才會有值，開啟 shopify hw page 則為預設值) |
| main_content_ready | Mandatory | Number |  | 開啟 paywall，至收到 webview 回傳 main_content_ready 的 js binding 的時間 |
| url | Mandatory | String |  | 開啟 webview 的 url 資訊，只紀錄 url host and path。例：https://alfred.camera/payment/premium6_fullprice_full_14 |
| url_query | Mandatory | String |  | 只紀錄 url query string。例：version=5574&utm_source=android&utm_medium=referral&utm_campaign=action_url |
| offering_id | Mandatory | String |  | 開啟 paywall 的 offering id 資訊  (default：unknown，需開啟 premium paywall 才會有值，開啟 shopify hw page 則為預設值) |