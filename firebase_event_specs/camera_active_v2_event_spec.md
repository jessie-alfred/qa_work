# 事件追蹤規範：camera_active_v2

## 事件名稱 (Event Name)

`camera_active_v2`

## 目的 (Purpose)

Track the liveness of a Camera with snapshots of configurations at the moment. Triggered when 1) the Camera finishes registering with backend or 2) every 12 hours while remaining online.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| report_type | Mandatory | String | launch/routine | The app launch type |
| launch_reason | Android Only | String | user/crash/wake/anr/deadlock/update/gl_error/service_relaunch/camera_disabled | The reason or trigger that caused the app to launch |
| xmpp_online | Mandatory | Boolean | true/false | Whether the XMPP is connected |
| xmpp_region | Mandatory | String | <xmpp_region> | Current XMPP region |
| background | Android Only | Boolean | true/false | Whether the camera is running in background |
| screen_on | Android Only | Boolean | true/false | Whether the screen of the device is on |
| camera_pipeline | Android Only | String | version_1/version_2/version_3 | The camera pipeline type |
| battery_optimization | Android Only | Boolean | true/false | Whether the battery optimization is enabled |
| guided_access | iOS Only | Boolean | true/false | Whether the guided access is enabled |
| network_type | Mandatory | String | 5g/4g/wifi/others(已連線但非上述)/unknown(斷線) | The internet connectivity used by the device |