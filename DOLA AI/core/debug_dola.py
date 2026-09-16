import asyncio
import sys
from patchright.async_api import async_playwright
from browser import launch_account_context

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        context = await launch_account_context(p, 'acc1', headless=True, use_extension=False)
        page = await context.new_page()
        await page.goto('https://www.dola.com/chat', timeout=60000)
        await page.wait_for_timeout(6000)
        
        print('Page title:', await page.title())
        print('Page URL:', page.url)
        
        elements = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('*')).filter(el => {
                const tag = el.tagName.toLowerCase();
                return tag === 'input' || tag === 'button' || tag === 'textarea' || el.getAttribute('role') === 'button';
            }).map(el => ({
                tag: el.tagName,
                type: el.getAttribute('type'),
                id: el.id,
                text: (el.innerText || el.textContent || el.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ').slice(0, 80),
                outer: el.outerHTML.slice(0, 150)
            }));
        }''')
        
        print(f"Found {len(elements)} interactive elements:")
        for el in elements:
            print(" ->", el)
            
        await page.screenshot(path='dola_chat_debug.png')
        print("Screenshot saved to dola_chat_debug.png")
        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
