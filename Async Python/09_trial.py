import asyncio

async def fetch_data(param):
    print("Fetching data...")
    await asyncio.sleep(param)  # Simulate a network delay
    print("Data fetched!")
    return {"data": "Sample data"}

async def main():
    print("Starting main function...")
    task1 = asyncio.create_task(fetch_data(2))

    await asyncio.sleep(2)

asyncio.run(main())

# A coroutine object by itself does not execute when it is created. 
# It must either be awaited or scheduled on the event loop. 
# When asyncio.create_task() is used, the coroutine is wrapped 
# in a Task and immediately scheduled to run by the event loop. 
# This means the task can execute concurrently with other coroutines 
# even if it is never explicitly awaited. However, while a task does 
# not need to be awaited to start running, awaiting it is still useful
#  for retrieving its result, handling exceptions, and ensuring it 
# completes before the program exits. If the event loop stops before 
# the task finishes, any unfinished tasks may be cancelled.