# 事件追蹤規範：camera_settings_v2

## 事件名稱 (Event Name)

`camera_settings_v2`

## 目的 (Purpose)

Track camera configurations with snapshots at the moment. Triggered when 1) the Camera finishes registering with backend or 2) every 12 hours while remaining online.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| activity_detection | Mandatory | Boolean | true/false | Whether the activity detection is enabled |
| activity_detection_sensitivity | Mandatory | String | low/medium/high | The sensitivity level of the activity detection |
| motion_detection | Mandatory | Boolean | true/false | Whether the motion detection is enabled |
| person_detection | Mandatory | Boolean | true/false | Whether the person detection is enabled |
| pet_detection | Mandatory | Boolean | true/false | Whether the pet detection is enabled |
| vehicle_detection | Mandatory | Boolean | true/false | Whether the vehicle detection is enabled |
| sound_detection | Mandatory | Boolean | true/false | Whether the sound detection is enabled |
| decibel_detection_threshold | Mandatory | Number |  | The threshold of the decibel detection |
| activity_detection_schedule | Mandatory | Boolean | true/false | Whether the activity detection schedule is enabled |
| person_linger | Mandatory | Boolean | true/false | Whether the person linger of the context aware is enabled |
| person_absent | Mandatory | Boolean | true/false | Whether the person absent of the context aware is enabled |
| motion_stop | Mandatory | Boolean | true/false | Whether the motion stop of the context aware is enabled |
| detection_zone | Mandatory | Boolean | true/false | Whether the detection zone is enabled |
| continuous_recording | Mandatory | Boolean | true/false | Whether the continuous recording is enabled |
| ai_frame | Mandatory | Boolean | true/false | Whether the ai frame of the person detection is enabled |
| low_light | Mandatory | Boolean | true/false | Whether the low-light is enabled |
| auto_low_light | Mandatory | Boolean | true/false | Whether the auto low-light is enabled |
| zoomed_in | Mandatory | Boolean | true/false | Whether the camera is currently zoomed-in |
| zoom_in_lock | Mandatory | Boolean | true/false | Whether the zoom-in lock is enabled |