"""Manual interactive login helper for Dola account setup.

Usage:
  python add_account_manual.py <account_name>
Example:
  python add_account_manual.py acc1
"""
import asyncio
import sys
from pathlib import Path
from patchright.async_api import async_playwright
from browser import LAUNCH_ARGS
import config


async def manual_login(account: str):
    profile_dir = Path("accounts") / account
    profile_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"[*] Dang mo trinh duyet de dang nhap tai khoan: [{account}]")
    print("[*] Vui long dang nhap Google / Dola tren cua so trinh duyet vua hien len.")
    print("[*] He thong se tu dong nhan dien va luu khi ban dang nhap thanh cong.")
    print("=" * 60)

    async with async_playwright() as p:
        kwargs = {
            "channel": "chrome",
            "headless": False,
            "args": LAUNCH_ARGS,
            "locale": "ja-JP",
            "timezone_id": "Asia/Tokyo",
        }
        if config.PROXY:
            kwargs["proxy"] = {"server": config.PROXY}

        context = await p.chromium.launch_persistent_context(str(profile_dir), **kwargs)
        try:
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto("https://www.dola.com/chat", timeout=60000)

            # Poll for sessionid
            logged_in = False
            for i in range(150):  # Wait up to 5 minutes
                await asyncio.sleep(2)
                cookies = await context.cookies("https://www.dola.com")
                has_session = any(c.get("name") == "sessionid" and c.get("value") for c in cookies)
                if has_session:
                    print(f"\n[OK] DA DANG NHAP THANH CONG! Sessionid da duoc luu vao: {profile_dir}")
                    logged_in = True
                    await asyncio.sleep(2)
                    break
                if i % 5 == 0 and i > 0:
                    print(f"[*] Dang doi ban dang nhap... ({i * 2}s)")

            if not logged_in:
                print("\n[!] Het thoi gian cho dang nhap (5 phut). Vui long thu lai.")
                return False
            return True
        finally:
            await context.close()


def main():
    account = sys.argv[1] if len(sys.argv) > 1 else "acc1"
    asyncio.run(manual_login(account))


if __name__ == "__main__":
    main()
