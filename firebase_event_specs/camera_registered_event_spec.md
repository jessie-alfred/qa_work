# 事件追蹤規範：camera_registered

## 事件名稱 (Event Name)

`camera_registered`

## 目的 (Purpose)

Track a user sets up their phone as a "Camera" and successfully connects to the Alfred API server after installing the app.

## 事件屬性 (Event Properties)

| Event Property | Requirement | Data Type | Value | Description |
| --- | --- | --- | --- | --- |
| success | Mandatory | Boolean | true/false | Indicates whether the response of register device api is success |