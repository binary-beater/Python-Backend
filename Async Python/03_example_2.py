# Asynchronous code example
# but no concurrent execution of tasks, they are still executed sequentially
# it's creating two tasks, but they are not running at the same time, 
# they are still waiting for each other to finish before moving on to the next one

import asyncio
import time

async def fetch_data(param):
    print(f"Do something with {param}...")
    await asyncio.sleep(param)
    print(f"Finished processing {param}.")
    return f"Result for {param}"

async def main():
    task1 = fetch_data(1)
    task2 = fetch_data(2)
    result1 = await task1
    print("Task 1 fully completed")
    result2 = await task2
    print("Task 2 fully completed")
    return [result1, result2]

t1 = time.perf_counter()
results = asyncio.run(main())
print(results)

t2 = time.perf_counter()
print(f"Finished in {t2 - t1:.2f} seconds.")