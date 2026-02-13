# 事件追蹤規範：function_behavior

## 事件名稱 (Event Name)

`function_behavior`

## 目的 (Purpose)

watch_live

## 事件屬性 (Event Properties)

| Firebase | Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- | --- |
| watch_live |  |  |  |  |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
|  | connection_time | Mandatory | Number |  |  |
|  | length | Mandatory | Number |  |  |
|  | viewer_count | Mandatory | Number |  |  |
|  | average_fps | Optional | Number |  |  |
|  | quality_by_sec | Optional | String |  |  |
|  | error_reason | Optional | String |  |  |
|  | on_vpn | Mandatory | Boolean | true/false |  |
|  | relay_url | Optional | String |  |  |
|  | by_alert | Optional | Boolean | true/false |  |
|  | alert_type | Optional | String | person_absent person_linger motion_stopped |  |
| watch_recorded_video |  |  |  |  |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
|  | placement | Mandatory | String | event_player cr_playback |  |
|  | timestamp | Optional | Number |  |  |
|  | event_source | Mandatory | String |  |  |
|  | from_eventplay | Optional | Boolean | true/false |  |
|  | event_tags | Optional | String |  |  |
|  | connection_time | Optional | Number |  |  |
|  | error_reason | Optional | String |  |  |
|  | on_vpn | Mandatory | Boolean | true/false |  |
|  | relay_url | Optional | String |  |  |
|  | by_alert | Optional | Boolean | true/false |  |
|  | alert_type | Optional | String | person_absent person_linger motion_stopped |  |
| add_a_camera |  |  |  |  |  |
|  | camera_type | Optional | String | app browser ac101 ac201 ac202 |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| click_cr_date_picker |  |  |  |  |  |
| change_playback_download_mode |  |  |  |  |  |
|  | status | Mandatory | String | entered/exited |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| click_view_in_playback |  |  |  |  |  |
| change_low_light_status |  |  |  |  |  |
|  | status | Mandatory | String | on/off/auto |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_night_vision_status |  |  |  |  |  |
|  | status | Mandatory | String | on/off/auto |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_spotlight_status |  |  |  |  |  |
|  | enabled | Optional | Boolean | true/false |  |
|  | auto_enabled | Optional | Boolean | true/false |  |
|  | brightness | Optional | String | high/low |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_resolution |  |  |  |  |  |
|  | resolution | Mandatory | String | basic standard hd fullhd supreme qhd qhd supreme |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| record_a_video |  |  |  |  |  |
|  | length | Mandatory | Number | (default：-1) |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_siren_status |  |  |  |  | 之前只有 on 會記錄 |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_zoom |  |  |  |  |  |
|  | action | Mandatory | String | double_tap pinch scale |  |
|  | placement | Mandatory | String | live event_player cr_playback |  |
|  | scale | Optional | Number (float) |  |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_voice_chat_status |  |  |  |  | 之前只有 on 會記錄 |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| click_how_to_scan |  |  |  |  |  |
| click_monitoring_target_save |  |  |  |  |  |
| click_camera_location_save |  |  |  |  |  |
| click_usage_purpose_save |  |  |  |  |  |
| usage_purpose_answered |  |  |  |  |  |
| change_continuous_autofocus_recording |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_alert_setting |  |  |  |  |  |
|  | type | Mandatory | String | event_notification event motion_stopped motion person_absent person_lingering person pet vehicle sound battery |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
| change_notification |  |  |  |  |  |
|  | type | Mandatory | String | new_products_and_deals new_features_and_updates feedback_survey |  |
|  |  |  |  |  |  |
| change_ai_frame_status |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_appearance_status |  |  |  |  |  |
|  | status | Mandatory | String | auto/light |  |
| change_camera_name |  |  |  |  |  |
|  | original_name | Mandatory | String |  |  |
|  | new_name | Mandatory | String |  |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_context_aware_settings |  |  |  |  |  |
|  | type | Mandatory | String | motion_stopped motion person_absent person_lingering person ai_frame pet vehicle |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | setting | Optional | String |  |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_continuous_recording_status |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_activity_detection_status |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_sound_detection_status |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_decibel_detection_threshold |  |  |  |  |  |
|  | threshold | Mandatory | Number | <decibel_threshold> |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| click_eventbook_turn_it_on |  |  |  |  |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| download_video |  |  |  |  |  |
|  | placement | Mandatory | String | event_group event_player cr_playback |  |
|  | source | Mandatory | String | local/cloud |  |
|  | count | Optional | Number |  |  |
|  | error_message | Optional | String | for event: - not_enough_space - viewer_offline - camera_offline - video_deleted - other for cr - not_enough_space - full_video_download_failed - download_interrupted - connection_error - cancel_by_user |  |
|  | video_duration | Optional | Number |  |  |
|  | download_duration | Optional | Number | for cr |  |
|  | download_type | Optional | String | for cr - full - partial - segments |  |
|  | candidate_type | Optional | String | for cr - relay - local - stun |  |
|  | relay_url | Optional | String | for cr |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| select_eventbook_filter |  |  |  |  |  |
|  | type | Mandatory | String | all motion person pet vehicle decibel moment |  |
|  | selected | Mandatory | Boolean |  |  |
| pull_to_refresh |  |  |  |  |  |
|  | placement | Mandatory | String | camera_list event_list |  |
| click_multiple_viewer_icon |  |  |  |  |  |
| click_hw_purchase_platform_survey_send |  |  |  |  |  |
| change_detection_zone_status |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_cr_timeline |  |  |  |  |  |
|  | action | Mandatory | String | drag zoom |  |
| change_live_toolbar |  |  |  |  |  |
|  | action | Mandatory | String | click swipe |  |
|  | type | Mandatory | String | previous next |  |
| user_message_v2 |  |  |  |  |  |
| enagement_behavior_v2 |  |  |  |  |  |
| user_message_v2 |  |  |  |  |  |
| user_message_v2 |  |  |  |  |  |
| user_message_v2 engagement_behavior_v2 |  |  |  |  |  |
| user_message_v2 engagement_behavior_v2 |  |  |  |  |  |
| user_message_v2 |  |  |  |  |  |
| user_message_v2 |  |  |  |  |  |
| click_tab_navigation |  |  |  |  | Viewer 頁面 |
|  | type | Mandatory | String | camera_list explore_list premium shop more |  |
| change_mute_status |  |  |  |  | Live 頁面 |
|  | muted | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_lens |  |  |  |  | Live 頁面 |
|  | type | Mandatory | String | front_camera rear_camera |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_camera_license |  |  |  |  | Camera Settings 頁面 |
|  | status | Mandatory | String | on/off |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_activity_detection_sensitivity |  |  |  |  | Camera Settings 頁面 |
|  | status | Mandatory | String | low/medium/high |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_viewer_priority |  |  |  |  | Camera Settings 頁面 |
|  | status | Mandatory | String | always_accept owner_first always_reject |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_video_display_settings |  |  |  |  | Camera Settings 頁面 |
|  | type | Mandatory | String | logo_watermark timestamp |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_live_connection_mode |  |  |  |  |  |
|  | status | Mandatory | String | saver auto_streaming |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_auto_power_saving_mode |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_stay_zoomed_in |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
| change_status_led |  |  |  |  |  |
|  | enabled | Mandatory | Boolean | true/false |  |
|  | camera_jid | Optional | String | <camera_jid> |  |
