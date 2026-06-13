# Understanding `asyncio`: Coroutines, Tasks, and `await`

## Example Code

```python
import asyncio

async def fetch_data(param):
    print(f"Do something with {param}...")
    await asyncio.sleep(param)
    print(f"Finished processing {param}.")
    return f"Result for {param}"

async def main():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))

    result1 = await task1
    result2 = await task2

    return [result1, result2]

asyncio.run(main())
```

---

## What `asyncio.run()` Does

```python
asyncio.run(main())
```

1. Creates an event loop.
2. Schedules `main()` to run.
3. Runs the loop until `main()` completes.
4. Closes the event loop.

---

## Coroutine vs Task

### Coroutine Object

```python
coro = fetch_data(1)
```

This only creates a coroutine object.

* No code inside `fetch_data()` runs.
* It is not scheduled in the event loop.
* It is just a description of work to be done later.

Think of it as a recipe.

---

### Task

```python
task = asyncio.create_task(fetch_data(1))
```

This:

1. Wraps the coroutine in a Task.
2. Registers it with the event loop.
3. Schedules it to run as soon as possible.

Think of it as a scheduled job.

---

## What `await` Does

### Awaiting a Coroutine

```python
coro = fetch_data(1)
result = await coro
```

When awaiting a raw coroutine:

* `await` starts executing the coroutine.
* The event loop drives it until completion.
* If it suspends (e.g. on `asyncio.sleep()`), the loop can run other tasks.
* The awaiting coroutine resumes when the coroutine finishes.

So for a coroutine object:

```text
await coroutine
```

means:

```text
Start it and wait for it to finish.
```

---

### Awaiting a Task

```python
task = asyncio.create_task(fetch_data(1))
result = await task
```

The task is already scheduled and may already be running.

So:

```text
await task
```

means:

```text
Wait for this already-running task to finish.
```

---

## Why Does `task2` Run Even Before `await task2`?

Consider:

```python
task1 = asyncio.create_task(fetch_data(1))
task2 = asyncio.create_task(fetch_data(2))

result1 = await task1
result2 = await task2
```

When `create_task()` is called:

```python
task2 = asyncio.create_task(fetch_data(2))
```

`task2` is immediately scheduled.

Later, when:

```python
await task1
```

causes `main()` to suspend, the event loop looks for other runnable tasks and finds `task2`.

Therefore `task2` can run even though:

```python
await task2
```

has not been reached yet.

---

## How Concurrency Happens

Timeline:

```text
main starts
│
├─ create task1
├─ create task2
│
├─ await task1
│   │
│   ├─ task1 runs
│   ├─ task1 sleeps
│   │
│   ├─ task2 runs
│   ├─ task2 sleeps
│   │
│   └─ event loop switches between them
│
├─ task1 completes
├─ main resumes
│
├─ await task2
│
└─ task2 completes
```

This cooperative switching is what provides concurrency.

---

## If You Don't Want a Coroutine to Start Yet

Do not create a task.

Instead:

```python
coro = fetch_data(1)
```

Nothing runs.

Later:

```python
await coro
```

or

```python
task = asyncio.create_task(coro)
```

will start execution.

---

## If You Already Created a Task

```python
task = asyncio.create_task(fetch_data(1))
```

The task is already scheduled.

If you no longer want it:

```python
task.cancel()
```

The event loop will raise `CancelledError` inside the coroutine at its next suspension point.

---

## Mental Model

### Coroutine Object

```text
Recipe
Not running
Not scheduled
```

```python
coro = fetch_data(1)
```

---

### Task

```text
Scheduled job
Managed by event loop
May already be running
```

```python
task = asyncio.create_task(fetch_data(1))
```

---

### Await

For a coroutine:

```text
Start it and wait.
```

For a task:

```text
Wait for it.
```

---

## Key Takeaway

```python
fetch_data(1)
```

Creates a coroutine object only.

```python
await fetch_data(1)
```

Starts the coroutine and waits for it to finish.

```python
asyncio.create_task(fetch_data(1))
```

Schedules the coroutine to run independently in the background.

```python
await task
```

Does not start the task—it merely waits for the already-scheduled task to complete.
