import asyncio
import time

async def fetch_data(param):
    await asyncio.sleep(param)
    return f"Result of {param}"

async def main():
    # Create tasks manually
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result1 = await task1
    result2 = await task2
    print(f"Task 1 and 2 awaited results: {[result1, result2]}")

    # Gather coroutines
    coroutines = [fetch_data(i) for i in range(1, 3)]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    print(f"Gathered results: {results}")

    # Gather Tasks
    tasks = [asyncio.create_task(fetch_data(i)) for i in range(1, 3)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(f"Gathered task results: {results}")

    # Task Group
    async with asyncio.TaskGroup() as tg:
        results = [tg.create_task(fetch_data(i)) for i in range(1, 3)]
        # all tasks in the group will be awaited automatically when exiting the context
    print(f"Task group results: {[result.result() for result in results]}")

t1 = time.perf_counter()

results = asyncio.run(main())

t2 = time.perf_counter()
print(f"Execution time: {t2 - t1:.2f} seconds")