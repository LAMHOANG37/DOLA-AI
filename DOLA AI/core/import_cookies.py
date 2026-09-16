"""Import Dola cookies from cookies.txt directly into account profiles.

Supported formats from tool Stand / MMO / DevTools:
1. Semicolon string: msToken=...; sessionid=...; s_v_web_id=...
2. Pipe / Colon delimited: email|pass|totp|msToken=...; sessionid=...
3. JSON Array: [{"name": "sessionid", "value": "..."}, ...]
"""
import asyncio
import json
import re
from pathlib import Path
from patchright.async_api import async_playwright
from browser import LAUNCH_ARGS
import config


def parse_cookie_input(raw: str) -> list[dict]:
    raw = raw.strip()
    if not raw:
        return []

    # 1. Try parsing JSON array
    if raw.startswith("[") and raw.endswith("]"):
        try:
            items = json.loads(raw)
            cookies = []
            for it in items:
                name = it.get("name") or it.get("key")
                val = it.get("value") or it.get("val")
                domain = it.get("domain", ".dola.com")
                path = it.get("path", "/")
                if name and val:
                    cookies.append({
                        "name": str(name),
                        "value": str(val),
                        "domain": str(domain) if "dola.com" in str(domain) else ".dola.com",
                        "path": str(path),
                    })
            if cookies:
                return cookies
        except Exception:
            pass

    # 2. If line contains pipes '|' or '----' from MMO tools (e.g. mail|pass|cookie or uid|pass|cookie)
    cookie_str = raw
    if "|" in raw:
        parts = raw.split("|")
        # find the part that looks like cookie
        for p in parts:
            if "sessionid=" in p or "msToken=" in p or "s_v_web_id=" in p:
                cookie_str = p
                break
    elif "----" in raw:
        parts = raw.split("----")
        for p in parts:
            if "sessionid=" in p or "msToken=" in p or "s_v_web_id=" in p:
                cookie_str = p
                break

    # 3. Standard key=value; pairs
    cookies = []
    # Strip common header prefixes if user pasted them
    cookie_str = re.sub(r"(?i)^cookie:\s*", "", cookie_str).strip()
    
    items = cookie_str.split(";")
    for item in items:
        item = item.strip()
        if not item or "=" not in item:
            continue
        k, v = item.split("=", 1)
        k = k.strip()
        v = v.strip()
        cookies.append({
            "name": k,
            "value": v,
            "domain": ".dola.com",
            "path": "/",
        })
    return cookies


async def import_single_account(account: str, raw_line: str):
    profile_dir = Path("accounts") / account
    profile_dir.mkdir(parents=True, exist_ok=True)
    cookies = parse_cookie_input(raw_line)
    if not cookies:
        print(f"[!] Khong the doc cookie cho [{account}]")
        return False

    has_sess_in_input = any(c["name"] == "sessionid" for c in cookies)
    if not has_sess_in_input:
        print(f"[!] Canh bao: [{account}] thieu cookie 'sessionid'")
        return False

    # Nhân đôi cookies cho cả .dola.com và www.dola.com để đảm bảo Playwright nhận 100%
    expanded_cookies = []
    for c in cookies:
        c1 = c.copy()
        c1["domain"] = ".dola.com"
        c2 = c.copy()
        c2["domain"] = "www.dola.com"
        expanded_cookies.extend([c1, c2])

    async with async_playwright() as p:
        kwargs = {
            "channel": "chrome",
            "headless": True,
            "args": LAUNCH_ARGS,
            "locale": "ja-JP",
            "timezone_id": "Asia/Tokyo",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }
        if config.PROXY:
            kwargs["proxy"] = {"server": config.PROXY}

        context = await p.chromium.launch_persistent_context(str(profile_dir), **kwargs)
        try:
            await context.add_cookies(expanded_cookies)
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto("https://www.dola.com/chat", timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Kiểm tra xem có nút login không
            login_btn = await page.locator('button:has-text("ログイン"), button:has-text("Log in"), button:has-text("Sign in")').count()
            create_vid_btn = await page.locator('text=動画を作成, text=Create Video, text=Tạo video').count()

            saved_cookies = await context.cookies("https://www.dola.com")
            has_session = any(c["name"] == "sessionid" and c["value"] for c in saved_cookies)

            if has_session and login_btn == 0:
                print(f"[OK] Da import thanh cong [{account}] -> {profile_dir} (Trang thai: Active)")
                return True
            else:
                print(f"[!] [{account}] Cookie khong hop le hoac bi server Dola tu choi (chua dang nhap).")
                return False
        finally:
            await context.close()



async def main():
    cookie_file = Path("cookies.txt")
    if not cookie_file.exists():
        print("[!] File 'cookies.txt' khong ton tai.")
        print("[*] Vui long tao file 'cookies.txt' va dan cookie tu tool Stand vao do.")
        return

    content = cookie_file.read_text(encoding="utf-8").strip()
    if not content:
        print("[!] File 'cookies.txt' dang trong.")
        return

    # Check if the entire file is a single JSON array of accounts
    lines = []
    if content.startswith("[{") and "sessionid" in content:
        # Single JSON or array
        lines = [content]
    else:
        lines = [line.strip() for line in content.splitlines()
                 if line.strip() and not line.strip().startswith("#")]

    print(f"[*] Tim thay {len(lines)} dong cookie trong cookies.txt. Bat dau import...")
    success_count = 0
    for idx, line in enumerate(lines, start=1):
        acc_name = f"acc{idx}"
        ok = await import_single_account(acc_name, line)
        if ok:
            success_count += 1

    print(f"\n[V] Hoan tat! Import thanh cong {success_count}/{len(lines)} tai khoan.")


if __name__ == "__main__":
    asyncio.run(main())
