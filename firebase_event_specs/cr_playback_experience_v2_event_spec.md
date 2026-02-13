# 事件追蹤規範：cr_playback_experience_v2

## 事件名稱 (Event Name)

`cr_playback_experience_v2`

## 目的 (Purpose)

Measure the performance when the user is attempting to play continuous recording videos from the camera. It tracks the time required to perform a successful playback starting from the time when the user enters the CR playback page to to the time when the player is ready to play.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| camera_app_ver | Mandatory | String | <version name>/<build number> (e.g. 4.4.4/2164) | 相機端 app 版本 (default：-2) |
| camera_jid | Mandatory | String | <camera_resource_id> | camera jid 裡 resource id 的部分，也就是去除 email 的部分 |
| camera_os_ver | Mandatory | String | <OS type> <OS version> (e.g. iOS 10.3.3) | available types: - iOS  - android - embedded - Web Camera: browser name and its version  (default：empty string) |
| candidate | Mandatory | String |  | start,end,changed start：連線建立當下 <audio>/<video> 的 candidate type（local/stun/relay/unknown） end：事件記錄當下 <audio>/<video> 的 candidate type（local/stun/relay/unknown） changed：連線過程中，最後一次切換 <audio>/<video> candidate type 的 timestamp，timestamp 是指與“進入 Live 畫面"的時間差，沒有切換 candidate type 就記 -1（{timestamp}/-1） |
| data_channel_accepted | Mandatory | Number |  | 相機接到請求的 timestamp (default：-1, 若 data channel 已先在 live 建立成功的話 default：0) |
| data_channel_connected | Mandatory | Number |  | 連線完成的 timestamp (default：-1, 若 data channel 已先在 live 建立成功的話 default：0) |
| data_channel_requested | Mandatory | Number |  | 發送請求的 timestamp (default：-1, 若 data channel 已先在 live 建立成功的話 default：0) |
| entry | Mandatory | String | eventbook/context_aware_push/push/deeplink/camera_list/live |  |
| first_data_received | Mandatory | Number |  | 接收到事件列表的 timestamp (default：-1) |
| ip_stack | Mandatory | String | <viewer’s IP stack>/<camera’s IP stack> e.g. ipv4v6/ipv4 | available types: - ipv4v6 - ipv4 - ipv6 - unknown |
| network_type | Mandatory | String | <viewer_network_type>/<camera_network_type> e.g. 5G/4G | available types:  - 5G - 4G - non-4G - wifi - unknown |
| playback_id | Mandatory | String |  | 記錄當次進入播放器的 timestamp，目的是和 continuous_recording_playback_memo_1 串起來 |
| stop_reason | Mandatory | String | timeout |  |
|  |  |  | leave |  |
|  |  |  | playback_started |  |
|  |  |  | not_found |  |
|  |  |  | camera_offline |  |
|  |  |  | connect_timeout |  |
|  |  |  | background |  |
|  |  |  | push_notification |  |
|  |  |  | player_error | Android Only |
| video_count | Mandatory | Number |  | 事件數量 (default：0) |
| error_code | Optional | Number |  | The error code for the event |
| error_message | Optional | String |  | The error message for the event |