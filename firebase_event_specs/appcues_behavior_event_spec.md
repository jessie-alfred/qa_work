# 事件追蹤規範：appcues_behavior

## 事件名稱 (Event Name)

`appcues_behavior`

## 目的 (Purpose)

(未填)

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| action | Mandatory | String |  |  |
|  |  |  | experience_started |  |
|  |  |  | experience_finished |  |
|  |  |  | identify | Amplitude 一起拿掉 |
|  |  |  | show |  |
|  |  |  | event |  |
| exp_id | Optional | String |  |  |
| event_name | Optional | String |  | For action = event |
| finish_reason | Optional | String | completed/dismissed |  |