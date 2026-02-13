# 事件追蹤規範：event_play_experience_v2

## 事件名稱 (Event Name)

`event_play_experience_v2`

## 目的 (Purpose)

Measure the performance when the user is attempting to cloud-stored events from the event book. It tracks the time required to perform a successful playback starting from the time when the user clicks on a specific event to the time the playback actually started (the first content is displayed on the screen)

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| camera_platform | Mandatory | String | android/ios/embedded/web | From API - v2(event.platform) - DVR(event.cam.platform) - notification(params.os) |
| size | Mandatory | Number |  | The size (in bytes) of the event to be played.  From API - v2(event.vsize) - DVR(event.footages[0].size) - notification(params.vsize) |
| resolution | Mandatory | Number | e.g. 240, 480, 720, 1080 | Always 抓短邊 |
| vcodec | Mandatory | String | h264/hevc | Retrieve the codec name locally when playing the event. |
| storage_provider | Mandatory | String | s3/r2/local | From API - v2(s3) - DVR(event.footages[0].provider) - notification(params.storage_provider) |
| storage_region | Mandatory | String |  | provider-specific region string or bucket name, null when provider is local.  From API - v2(event.bucket) - DVR(event.footages[0].bucket) - notification(params.bucket)  notification 身上原本有 region，不要用它，他是 user region |
| network_type | Mandatory | String | wifi/cellular/vpn |  |
| cached | Android Only | Boolean | true/false | Android 這邊都是先存在播，因此一定都是會 true，但是去 get CDN 這邊會算上 cache ，這邊可以用這個來標示 |
| pre_buffer | iOS Only | Number |  | Indicates the media duration the caller prefers the player to buffer from the network ahead of the playhead to guard against playback disruption. |