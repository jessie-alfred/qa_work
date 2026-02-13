# 事件追蹤規範：ad_behavior

## 事件名稱 (Event Name)

`ad_behavior`

## 目的 (Purpose)

Tracks all ad-related operations from ad request to user interaction.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| action | Mandatory | String |  |  |
|  |  |  | presentable |  |
|  |  |  | suppressed |  |
|  |  |  | requested |  |
|  |  |  | request_failed |  |
|  |  |  | shown |  |
|  |  |  | clicked |  |
| placement | Mandatory | String | camera_list live event_list event_player | 原本叫 ad_unit，會拆成 page 跟 ad_format |
| ad_format | Mandatory | String | banner native_banner native interstitial |  |
| ad_mediation | Mandatory | String | admob | 原本叫 mediation |
| ad_source | Optional | String | admob facebook pubnative applovin inmobi pangle mintegral unknown | 原本叫 source |
| suppresed_reason | Optional | String | new_hw_user appcues_experience_started ctr_bonus rateus_dialog sd_sdcard_error_push freq | 目前僅當 action 為 suppressed 時會帶上 |
| error_message | Optional | String | <error_message_from_sdk> | 目前僅當 action 為 request_failed 時會帶上 |