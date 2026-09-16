"""Patchright persistent context launcher: Explicit proxy and anti-detection parameters."""
from pathlib import Path

import config

LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-first-run",
    "--no-default-browser-check",
]


async def launch_account_context(p, account: str, headless: bool = None, use_extension: bool = False):
    """Launches accounts/<account> profile, returns BrowserContext. Caller must close.

    p: async_playwright() instance
    headless: None = uses config.HEADLESS
    """
    profile_dir = Path("accounts") / account
    if not profile_dir.exists():
        raise FileNotFoundError(
            f"Account profile does not exist: {profile_dir} (run python add_account.py {account} first)"
        )
    launch_headless = config.HEADLESS if headless is None else headless
    args = list(LAUNCH_ARGS)
    if use_extension:
        if not config.EXTENSION_ENABLED:
            raise RuntimeError("Dola extension is disabled (DOLA_EXTENSION_ENABLED=0)")
        extension_dir = Path(config.EXTENSION_DIR).resolve()
        if not extension_dir.exists():
            raise FileNotFoundError(f"Dola extension directory does not exist: {extension_dir}")
        # Chromium debugger extension requires headed window to intercept skill/action-bar responses
        launch_headless = False
        args.extend([
            f"--disable-extensions-except={extension_dir}",
            f"--load-extension={extension_dir}",
        ])
        if config.HEADLESS:
            args.append("--headless=new")
    kwargs = {
        "channel": "chrome",
        "headless": launch_headless,
        "args": args,
        "locale": "ja-JP",
        "timezone_id": "Asia/Tokyo",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    }
    if config.PROXY:
        kwargs["proxy"] = {"server": config.PROXY}
    return await p.chromium.launch_persistent_context(str(profile_dir), **kwargs)


def cookie_value(cookies: list, name: str) -> str:
    """Extracts cookie value from context.cookies() result."""
    return next((c["value"] for c in cookies if c["name"] == name and c["value"]), "")


async def check_login_state(account: str) -> bool:
    """Opens Dola in headless mode and checks whether session is active."""
    from patchright.async_api import async_playwright
    async with async_playwright() as p:
        context = await launch_account_context(p, account)
        try:
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto("https://www.dola.com/chat", timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # If login button is visible, session is not logged in or expired
            login_btn = await page.locator('button:has-text("ログイン"), button:has-text("Log in"), button:has-text("Sign in"), button.login-btn-header-CTKsn1').count()
            if login_btn > 0:
                return False
                
            create_btn = await page.locator('text=動画を作成, text=Create Video, text=Tạo video, text=画像を作成').count()
            return create_btn > 0
        finally:
            await context.close()

