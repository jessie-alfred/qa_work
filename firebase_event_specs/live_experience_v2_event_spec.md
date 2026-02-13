# 事件追蹤規範：live_experience_v2

## 事件名稱 (Event Name)

`live_experience_v2`

## 目的 (Purpose)

Measure the user experience when connecting to a camera’s live view. It tracks the time required starting from when the user enters the Live screen to the time when the first video frame is received.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| call_ready | Mandatory | Number |  | Viewer Call 給 Camera 的 timestamp (default：-1, from 為 cr_playback 且支援 merge connection 的話 default：0) |
| call_accepted | Mandatory | Number |  | Viewer 端確認 Camera 端接受 call 的 timestamp (default：-1, from 為 cr_playback 且支援 merge connection 的話 default：0) |
| video_channel_ready | Mandatory | Number |  | video channel 建立好的 timestamp (default：-1, from 為 cr_playback 且支援 merge connection 的話 default：0) |
| first_video_frame | Mandatory | Number |  | 第一張可以 render 出來的 video frame 的 timestamp (default：-1) |
| first_audio | Mandatory | Number |  | 第一個 audio 來的 timestamp， Live 前就已經被手動關閉 audio 則記 -2 (default：-1, from 為 cr_playback 且支援 merge connection 的話 default：-3) |
| network_type | Mandatory | String | <viewer_network_type>/<camera_network_type> e.g. 5G/4G | available types:  - 5G - 4G - non-4G - wifi - unknown |
| candidate | Mandatory | String |  | audioCandidateStart/videoCandidateStart,audioCandidateEnd/videoCandidateEnd,audioCandidateChanged/videoCandidateChanged start：連線建立當下 <audio>/<video> 的 candidate type（local/stun/relay/unknown） end：事件記錄當下 <audio>/<video> 的 candidate type（local/stun/relay/unknown） changed：連線過程中，最後一次切換 <audio>/<video> candidate type 的 timestamp，timestamp 是指與“進入 Live 畫面"的時間差，沒有切換 candidate type 就記 -1（{timestamp}/-1） |
| camera_pipeline | Mandatory | String | ios/android1/android2/android3/web/embedded | 相機端是什麼平台 |
| camera_jid | Mandatory | String | <camera_resource_id> | camera jid 裡 resource id 的部分，也就是去除 email 的部分 |
| camera_os_ver | Mandatory | String | <OS type> <OS version> (e.g. iOS 10.3.3) | available types: - iOS  - android - embedded - Web Camera: browser name and its version  (default：empty string) |
| camera_app_ver | Mandatory | String | <version name>/<build number> (e.g. 4.4.4/2164) | 相機端 app 版本 (default：-2) |
| resolution | Mandatory | Number |  | 解析度寬度或高度取較小者 (default：0) |
| from | Mandatory | String | camera_list/background/push/context_aware_push/relay_reconnect/cr_playback/payment_page/bounding_box_setting/deeplink | live 是從哪邊發起 |
| ip_stack | Mandatory | String | <viewer’s IP stack>/<camera’s IP stack> e.g. ipv4v6/ipv4 | available types: - ipv4v6 - ipv4 - ipv6 - unknown |
| signaling_protocol | Mandatory | String |  | rtc_signaling 的 capability 版本 (default：0) |
|  |  |  | 0.0 | Legacy XMPP based protocol |
|  |  |  | 1.0 | RTC Signaling |
|  |  |  | 2.0 | Data Channel Only |
|  |  |  | 3.0 | Initial Resolution |
| multi_viewer_user | Optional | String | <allViewersNum>,<trustCircleNum> e.g. 1,0 | multiple viewer 的數量 |
| turn | Optional | String | e.g. global.turn.twilio.com, turn.cloudflare.com | Turn Server URL |
| error_reason | Optional | String |  | live 的結束是出自於哪個 error back - when user press the exit button to leave live stream  background - when the App goes to the background  busy - when reaching the maximum number of multiple viewers  cr_playback - when launching the CR Playback  camera_exit - XMPP disconnection due to reasons other than following SessionDisconnectReason.ACCESS_DENIED  SessionDisconnectReason.CAMERA_DISABLED  SessionDisconnectReason.CAMERA_OCCUPIED  SessionDisconnectReason.CAMERA_NO_FRAME  SessionDisconnectReason.SESSION_BUSY  SessionDisconnectReason.SESSION_REPLACED   camera_offline - when XMPP disconnected on the camera side  connect_timeout first video frame not received within 30 seconds  when receiving any of the following peer connection errors PeerConnectionClient.ErrorCode.PEER_CONNECTION_STATE_FAILED  PeerConnectionClient.ErrorCode.P2P_CONNECT_TIMEOUT  PeerConnectionClient.ErrorCode.SDP_ERROR    disabled - when the camera preview is disabled on the camera side  relay_finish Amplitude only - when usage of the relay server exceeds 3 minutes  live_auto_streaming_mode_interruption_leave Amplitude only - when the live saving mode timeout occurs  live_auto_streaming_mode_interruption_upgrade Amplitude only - when the user taps the upgrade button of live saving mode dialog  no_frame - first video frame not received within 3 seconds on the camera side   no_permission - when the viewer is not authorized to access  occupied - when failed to open the camera on the camera side  push_notification - while in live stream, tap on a push notification from another camera to enter its live stream  replaced - when the viewer session is replaced by another viewer  rtc_error - when peer connection errors due to reasons other than following PeerConnectionClient.ErrorCode.PEER_CONNECTION_STATE_FAILED  PeerConnectionClient.ErrorCode.P2P_CONNECT_TIMEOUT  PeerConnectionClient.ErrorCode.SDP_ERROR   unknown - this error is not supposed to happen  viewer_offline - when XMPP disconnected on the viewer side |
| hw_decoder | Android Only | String |  | viewer 端所使用的 decoder 類型 (default：-1) |
|  |  |  | -1.0 | unknown |
|  |  |  | 0.0 | software |
|  |  |  | 1.0 | hardware |
| local_network_permission | iOS 14+ Only | String |  | 是否同意 local connection 的權限 |
|  |  |  | -1.0 | not determined |
|  |  |  | 0.0 | denied |
|  |  |  | 1.0 | allowed |