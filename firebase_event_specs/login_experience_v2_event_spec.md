# 事件追蹤規範：login_experience_v2

## 事件名稱 (Event Name)

`login_experience_v2`

## 目的 (Purpose)

Measure the performance when the user re-signs in to the service (within previously obtained signin session). It tracks the time required starting from the app is launched to the time when the client successfully retrieved the API token and connected to the XMPP server after authentication.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| start_timestamp | Mandatory | Number |  | 本事件開始紀錄的 timestamp |
| get_kv_token_completed | Mandatory | Number |  | 拿到 kv token 的 timestamp (default：-1) |
| xmpp_signin_completed | Mandatory | Number |  | xmpp sign-in 成功的 timestamp (default：-1) |
| network_type | Mandatory | String | 5G/4G/non-4G/wifi/unknown |  |
| ip_stack | Mandatory | String | ipv4v6/ipv4/ipv6/unknown |  |
| xmpp_type | Mandatory | String | unknown/alfred |  |
| login_type | Mandatory | String | anonymous/email/google/apple/qr |  |
| timeout | Mandatory | String |  |  |
|  |  |  | 0.0 | 未超過十秒 |
|  |  |  | 1.0 | 超過十秒 |
| role | Mandatory | String | viewer/camera | 登入使用的角色 |
| tls_type | Optional | String | direct_tls/starttls | XMPP 連線的方法 |
| from | Mandatory | String | camera_list playback push context_aware_push event_play camera live (iOS only) sdcard (iOS only) event (iOS only) | Login 的進入點 |
| xmpp_region | Mandatory | String |  | xmpp 所在的 region |
| report_entry | Mandatory | String | signin_provider_error xmpp_connected xmpp_disconnected camera_timeout viewer_timeout kvtoken_failure (iOS only) | 上報的時機 |
| error | Optional | String | <error_type>,<error_message> | error_type: - signin_provider - xmpp  error_message of signin_provider: - account_null - provider_unknown - email_unverified - firebase_invalid_credential - firebase_user_collision - firebase_sign_in - sign_in_cancelled - timeout - firebase_link_collision - firebase_link_credential - firebase_link_credential_null - firebase_link_web_cancelled - google_play_unavailable - unknown - firebase_id_token - firebase_user_not_found - kv_token_failure - sign_in_required  error_message of xmpp (from SignalingChannel.DisconnectReason enum name with lowercase): - server_unreachable - host_unknown - unauthorized - tls_failed - connect_timeout - conflict - rejected_by_server - server_shutdown - logout - ping_timeout - none |