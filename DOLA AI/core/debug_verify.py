
import asyncio
from browser_pool import BrowserPool
import config

async def main():
    pool = BrowserPool(max_concurrency=config.MAX_CONCURRENCY)
    try:
        ok = await pool.verify_account('acc1')
        print('OK:', ok)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())

