import asyncio
import sys
from patchright.async_api import async_playwright
from browser import launch_account_context

sys.stdout.reconfigure(encoding='utf-8')

async def test():
    async with async_playwright() as p:
        ctx = await launch_account_context(p, 'acc1', headless=True)
        cookies = await ctx.cookies('https://www.dola.com')
        print(f"Cookies count: {len(cookies)}")
        for c in cookies:
            print(f"  {c['name']} = {c['value'][:25]}... (domain: {c['domain']})")
        
        page = await ctx.new_page()
        await page.goto('https://www.dola.com/chat')
        await page.wait_for_timeout(4000)
        
        login_btn = await page.locator('button:has-text("ログイン"), button:has-text("Log in"), button:has-text("Sign in")').count()
        create_vid = await page.locator('text=動画を作成, text=Create Video, text=Tạo video').count()
        file_inputs = await page.locator('input[type="file"]').count()
        print(f"Login button count: {login_btn}")
        print(f"Create video button count: {create_vid}")
        print(f"File input count before click: {file_inputs}")
        
        if create_vid > 0:
            print("Clicking create video button...")
            await page.locator('text=動画を作成, text=Create Video').first.click()
            await page.wait_for_timeout(3000)
            file_inputs_after = await page.locator('input[type="file"]').count()
            print(f"File input count AFTER click: {file_inputs_after}")
            
            # Print all input elements
            all_inputs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('input, button, [contenteditable]')).map(el => ({
                    tag: el.tagName,
                    type: el.getAttribute('type'),
                    text: (el.innerText || el.textContent || '').trim().slice(0, 40),
                    outer: el.outerHTML.slice(0, 100)
                }));
            }''')
            print(f"Inputs and buttons after clicking create video ({len(all_inputs)}):")
            for inp in all_inputs:
                print(" ->", inp)
                
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(test())
