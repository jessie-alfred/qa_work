# 事件追蹤規範：user_message_v2

## 事件名稱 (Event Name)

`user_message_v2`

## 目的 (Purpose)

Track all non-error UI elements displayed to users.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| message_id | Mandatory | String | e.g. <string_id>/<topic_id> | The primary unique identifier for a message, which can be a string_id or a topic_id.  It is used to uniquely identify a message and to link related events.  For example, user_message_v2 and engagement_behavior_v2 can be associated with the same message_id to establish a connection between the two events. |
| camera_resource_id | Optional | String |  | The resource ID of the camera device |