# 事件追蹤規範：error_message_v2

## 事件名稱 (Event Name)

`error_message_v2`

## 目的 (Purpose)

Track all error UI elements displayed to users.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| message_id | Mandatory | String | e.g. <string_id>/<topic_id> | The primary unique identifier for a message, which can be a string_id or a topic_id.  It is used to uniquely identify a message and to link related events.  For example, user_message_v2 and engagement_behavior_v2 can be associated with the same message_id to establish a connection between the two events. |
| camera_resource_id | Optional | String |  | The resource ID of the camera device |
| error_code | Optional | Number | e.g. 1008, 1010, 1012, 1017, 1020, 3001, 3002, 3004, 3006, 4001, 4002, 5001, 5010, 5016, 5019, 5020, 5021, 6005, 6006, 6008, 7001, 7004, 7006, 7007, 7008, 7009, 7010, 7011, 7012, 7013, 7015, 9001, 9002, 9005, 9007 | The error code of the event |
| error_message | Optional | String |  | The error messgage of the event |