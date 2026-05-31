import asyncio
import time

def sync_function(test_param: str) -> str:
    print("This is a synchronous function.")
    time.sleep(0.1)
    return f"Sync Result: {test_param}"

async def async_function(test_param: str) -> str:
    print("This is an asynchronous function.")
    await asyncio.sleep(0.1)
    return f"Async Result: {test_param}"


async def main():
    # sync_result = sync_function("Hello")
    # print(sync_result)

    loop = asyncio.get_running_loop()
    future = loop.create_future() # a promise-like object that will eventually hold a result or an exception
    print(f"Empty Future: {future}")

    future.set_result("Future Result: Test")
    future_result = await future
    print(future_result)

if __name__ == "__main__":
    asyncio.run(main())