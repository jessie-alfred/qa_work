# 事件追蹤規範：purchase_behavior_v2

## 事件名稱 (Event Name)

`purchase_behavior_v2`

## 目的 (Purpose)

Track all the user behaviors around purchase-related activities.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| action | Mandatory | String |  |  |
|  |  |  | landed | The user has entered the paywall. |
|  |  |  | started | The user has initiated the native payment process. |
|  |  |  | exited | The user has left the paywall. |
|  |  |  | completed | The native payment has been completed successfully. |
| success | Mandatory | Boolean | true/false | Indicates whether the action associated with the event was successful. |
| paywall_type | Mandatory | String | webview/shopify/revenuecat | The type of the paywall |
| placement_id | Optional | String | <placement_id> | The ID of a specific location used to launch the payment page. (Placement ID List) |
| url | Optional | String |  | The URL used in WebView-based paywall |
| offering_id | Optional | String |  | The ID of the offering represents a specific set of products that are presented to a user on the RC paywall. |
| product_id | Optional | String |  | The actual product ID based on the offering ID |
| subscription_cycle | Optional | String | p1m/p6m/p1y | Same as subscription_cycle |
| price | Optional | Number |  | The price of currently selected product |
| currency | Optional | String |  | The currency used by current paywall |
| error_code | Optional | Number | <rc_error_code> | The error code for the event |
| error_message | Optional | String | rapid_click/product_not_found/<xxx> | The error message for the event |