#!/usr/bin/env python3
"""JWT 解碼工具：解析 JWT token 的 header 與 payload（僅解碼，不驗證簽章）。"""

import base64
import json
import sys
from typing import Optional


def base64url_decode(data: str) -> bytes:
    """Base64url 解碼（JWT 使用 - 和 _ 取代 + 和 /，且常省略 padding）。"""
    # 還原為標準 base64 字元
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def decode_jwt(token: str) -> tuple[dict, dict]:
    """
    解碼 JWT token，回傳 (header, payload)。
    不驗證簽章，僅解析內容。
    """
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise ValueError(f"無效的 JWT 格式，應為 3 段，實際為 {len(parts)} 段")

    header_b64, payload_b64, _signature_b64 = parts

    header = json.loads(base64url_decode(header_b64).decode("utf-8"))
    payload = json.loads(base64url_decode(payload_b64).decode("utf-8"))

    return header, payload


def format_timestamp(ts: Optional[int]) -> str:
    """將 Unix timestamp 轉成可讀字串。"""
    if ts is None:
        return "—"
    from datetime import datetime, timezone
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, OSError):
        return str(ts)


def main():
    default_token = (
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhbGZyZWQubGFicyIsImlhdCI6MTc3MDk1NzU2MywiZXhwIjoxNzcwOTU4MTYzLCJlbWFpbCI6ImFsZnJlZHExN2xpbkBnbWFpbC5jb20iLCJqaWQiOiJhbGZyZWRxMTdsaW5AZ21haWwuY29tL2l2dXUxMmlQaG9uZTEyXzU2NDczRTkyQzU0OTQiLCJyZWdpb24iOiJ0dyIsImxvZ2luVHlwZSI6Imdvb2dsZS5jb20iLCJ1bmlxdWVfaWQiOiJkZXY0NGJmNmMxMmRhOGMxMWJjIiwiY291bnRyeSI6IlRXIiwicmVnX2RhdGVfdHMiOjE3NzA2MzM0MTg4Mzd9.jg59niRBoKkM2v--kWzhT4f0T0TsIEs68DKaSXtydDU"
    )

    token = sys.argv[1] if len(sys.argv) > 1 else default_token

    try:
        header, payload = decode_jwt(token)
    except Exception as e:
        print(f"解碼失敗：{e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("JWT Header")
    print("=" * 60)
    print(json.dumps(header, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("JWT Payload")
    print("=" * 60)
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    # 常用欄位摘要
    print("\n" + "=" * 60)
    print("常用欄位摘要")
    print("=" * 60)
    print(f"  iss (簽發者):     {payload.get('iss', '—')}")
    print(f"  iat (簽發時間):   {format_timestamp(payload.get('iat'))}")
    print(f"  exp (過期時間):   {format_timestamp(payload.get('exp'))}")
    print(f"  email:            {payload.get('email', '—')}")
    print(f"  region:           {payload.get('region', '—')}")
    print(f"  country:          {payload.get('country', '—')}")
    print(f"  loginType:        {payload.get('loginType', '—')}")
    print(f"  unique_id:        {payload.get('unique_id', '—')}")
    reg_ts = payload.get("reg_date_ts")
    if reg_ts is not None and isinstance(reg_ts, int) and reg_ts > 1e12:
        reg_ts = reg_ts // 1000  # 毫秒轉秒
    print(f"  reg_date_ts:      {format_timestamp(reg_ts)}")


if __name__ == "__main__":
    main()
