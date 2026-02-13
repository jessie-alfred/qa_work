# 事件追蹤規範：camera_statistics_v2

## 事件名稱 (Event Name)

`camera_statistics_v2`

## 目的 (Purpose)

Track camera statistics with snapshots of storage usage and cloud storage cost metrics at the moment. Triggered when 1) the Camera finishes registering with backend or 2) every 12 hours while remaining online.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| internal_free_mb | Mandatory | Number |  | The free capacity of internal storage in MB |
| cr_size_mb | Mandatory | Number |  | The storage size of the current CR videos in MB |
| cr_total_time_minutes | Mandatory | Number |  | The total duration of the current CR videos in minutes |
| event_size_mb | Mandatory | Number |  | The storage size of the current Event videos in MB |
| period_snapshot_count | Mandatory | Number |  | Total snapshots uploaded since previous report |
| period_snapshot_size_kb | Mandatory | Number |  | Total sizes in KB for all snapshots uploaded since previous report |
| period_video_count | Mandatory | Number |  | Number of videos uploaded since the last report |
| period_video_duration_sec | Mandatory | Number |  | Total duration of videos uploaded since the last report, in seconds |
| period_video_size_kb | Mandatory | Number |  | Total size of videos uploaded since the last report, in kilobytes (KB) |