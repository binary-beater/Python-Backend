import asyncio
async def test():
    x = 42
    await asyncio.sleep(1)

c = test()
print(c.cr_frame)