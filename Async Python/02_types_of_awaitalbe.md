# Types of Awaitables in Python (`asyncio`)

An **awaitable** is any object that can be used with the `await` keyword.

```python
result = await some_awaitable
```

Python's `asyncio` ecosystem defines three primary awaitable types:

1. **Coroutines**
2. **Tasks**
3. **Futures**

---

# High-Level Mental Model

```text
async def function
        │
        ▼
   Coroutine
        │
create_task()
        │
        ▼
      Task
        │
        ▼
     Future
```

Think of them as:

| Type | Purpose |
|--------|---------|
| Coroutine | Defines async work |
| Task | Runs/schedules async work |
| Future | Holds a result that will be available later |

---

# 1. Coroutines

A **coroutine** is a special function that can be suspended and resumed.

Defined using:

```python
async def fetch_data():
    return "data"
```

---

## Calling a Coroutine

Calling an async function **does not execute it immediately**.

```python
async def fetch_data():
    return "data"

coro = fetch_data()

print(coro)
```

Output:

```text
<coroutine object fetch_data at 0x...>
```

At this point:

- Function body has NOT executed
- Event loop has NOT scheduled it
- No asynchronous work has started

You only have a coroutine object.

---

## Coroutine Lifecycle

```text
Created
   ↓
Awaited
   ↓
Running
   ↓
Suspended (hits await)
   ↓
Resumed
   ↓
Completed
```

Example:

```python
async def work():
    print("Start")
    await asyncio.sleep(1)
    print("End")
```

Execution flow:

```text
work() called
    ↓
Coroutine object created
    ↓
await work()
    ↓
Function starts running
    ↓
Hits await asyncio.sleep()
    ↓
Suspends
    ↓
Resumes later
    ↓
Finishes
```

---

## Awaiting a Coroutine

```python
async def fetch_data():
    return "data"

async def main():
    result = await fetch_data()
    print(result)
```

Output:

```text
data
```

---

## Important Rule: Coroutines Are Single-Use

```python
coro = fetch_data()

await coro
await coro
```

Raises:

```text
RuntimeError:
cannot reuse already awaited coroutine
```

Once completed, a coroutine cannot be restarted.

---

## Every Call Creates a New Coroutine

```python
async def hello():
    return "hello"

c1 = hello()
c2 = hello()

print(c1 is c2)
```

Output:

```text
False
```

Each call produces a fresh coroutine object.

---

# 2. Tasks

A **Task** wraps a coroutine and schedules it to run on the event loop.

Think:

```text
Coroutine
     ↓
Task
     ↓
Event Loop
```

Without a Task, a coroutine is just a description of work.

A Task makes it actively executable.

---

## Creating a Task

```python
task = asyncio.create_task(fetch_data())
```

Internally (simplified):

```python
coro = fetch_data()

task = Task(coro)

event_loop.schedule(task)
```

---

## Why Tasks Exist

Without tasks:

```python
result1 = await fetch_user()
result2 = await fetch_orders()
```

Execution:

```text
fetch_user
    ↓
complete
    ↓
fetch_orders
    ↓
complete
```

Sequential execution.

---

With tasks:

```python
task1 = asyncio.create_task(fetch_user())
task2 = asyncio.create_task(fetch_orders())

user = await task1
orders = await task2
```

Execution:

```text
fetch_user
      \
       running concurrently
      /
fetch_orders
```

---

## Example

### Sequential

```python
async def work(name):
    await asyncio.sleep(2)
    return name

async def main():
    a = await work("A")
    b = await work("B")
```

Total time:

```text
4 seconds
```

---

### Concurrent

```python
async def main():
    t1 = asyncio.create_task(work("A"))
    t2 = asyncio.create_task(work("B"))

    a = await t1
    b = await t2
```

Total time:

```text
2 seconds
```

---

# Task Lifecycle

```text
Created
   ↓
Scheduled
   ↓
Running
   ↓
Waiting
   ↓
Done
```

Possible final states:

```text
Done
Failed
Cancelled
```

---

## Task Methods

### Check Completion

```python
task.done()
```

### Check Cancellation

```python
task.cancelled()
```

### Get Exception

```python
task.exception()
```

### Get Result

```python
task.result()
```

Example:

```python
if task.done():
    print(task.result())
```

---

## Cancelling Tasks

```python
task.cancel()
```

Cancellation raises:

```python
asyncio.CancelledError
```

Example:

```python
async def worker():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("Cancelled")
```

---

# Task Inheritance

A Task is actually a specialized Future.

```python
isinstance(task, asyncio.Future)
```

Output:

```text
True
```

Inheritance:

```text
Future
   ↑
 Task
```

This relationship is crucial for understanding asyncio internals.

---

# 3. Futures

A **Future** is a container for a value that will become available later.

Think of it as:

```text
Result not available yet
           ↓
      Future object
           ↓
Result arrives later
```

---

## JavaScript Comparison

JavaScript:

```javascript
const promise = fetch(url);
```

Python:

```python
future = asyncio.Future()
```

Conceptually:

```text
Promise ≈ Future
```

---

## Creating a Future

```python
future = asyncio.Future()
```

Initially:

```python
future.done()
```

Output:

```text
False
```

No result exists yet.

---

## Completing a Future

```python
future.set_result("Hello")
```

Now:

```python
future.done()
```

Output:

```text
True
```

Retrieve result:

```python
future.result()
```

Output:

```text
Hello
```

---

## Awaiting a Future

```python
future = asyncio.Future()

async def producer():
    await asyncio.sleep(1)
    future.set_result("Done")

asyncio.create_task(producer())

result = await future

print(result)
```

Output:

```text
Done
```

Flow:

```text
await future
      ↓
suspend coroutine
      ↓
future completed
      ↓
resume coroutine
```

---

# Why Futures Exist

Imagine:

```text
Producer
    ↓
creates result later

Consumer
    ↓
needs result eventually
```

A Future acts as the bridge.

```text
Producer
    ↓
 Future
    ↓
Consumer
```

---

# Internal Usage of Futures

Most asyncio APIs rely on Futures internally.

Example:

```python
await asyncio.sleep(5)
```

Simplified implementation:

```python
future = Future()

# timer callback later
future.set_result(None)

await future
```

The coroutine waits until the Future completes.

---

# Why Developers Rarely Use Futures Directly

Most application code uses:

```python
await coroutine()
```

or

```python
asyncio.create_task()
```

instead of:

```python
asyncio.Future()
```

because asyncio creates Futures internally.

---

## Application Developers Usually Use

```python
async def
await
create_task()
gather()
TaskGroup
```

---

## Library/Framework Authors May Use

```python
Future()
set_result()
set_exception()
```

especially when integrating:

- callbacks
- sockets
- transports
- protocols
- event-driven APIs

---

# Relationship Between Coroutines, Tasks, and Futures

## Hierarchy

```text
Awaitable
│
├── Coroutine
│
└── Future
      │
      └── Task
```

---

## Execution Flow

```python
task = asyncio.create_task(fetch())
```

Under the hood:

```text
fetch()
   ↓
Coroutine Object
   ↓
Wrapped in Task
   ↓
Scheduled by Event Loop
   ↓
Runs until await
   ↓
Waits on Future
   ↓
Future completes
   ↓
Task resumes
   ↓
Returns result
```

---

# Complete Example

```python
import asyncio

async def fetch():
    print("start")

    await asyncio.sleep(2)

    print("end")

    return 42

async def main():
    task = asyncio.create_task(fetch())

    print("doing other work")

    result = await task

    print(result)

asyncio.run(main())
```

Execution:

```text
main starts
    ↓
task created
    ↓
fetch scheduled
    ↓
main continues
    ↓
fetch starts
    ↓
sleep creates future
    ↓
task pauses
    ↓
future completes
    ↓
task resumes
    ↓
returns 42
    ↓
await task gets result
```

Output:

```text
doing other work
start
end
42
```

---

# Modern Asyncio APIs

## asyncio.gather()

Run multiple awaitables concurrently.

```python
results = await asyncio.gather(
    fetch_user(),
    fetch_orders(),
    fetch_products(),
)
```

Returns:

```python
[
    user,
    orders,
    products
]
```

---

## asyncio.TaskGroup (Python 3.11+)

Preferred structured concurrency API.

```python
async with asyncio.TaskGroup() as tg:
    user_task = tg.create_task(fetch_user())
    order_task = tg.create_task(fetch_orders())
```

Benefits:

- Automatic cleanup
- Better exception handling
- Structured concurrency
- Recommended over manual task management

---

# JavaScript Comparison

| JavaScript | Python |
|------------|---------|
| async function | async def |
| Promise | Future |
| await | await |
| Promise.all() | asyncio.gather() |
| Promise.then() | Future callbacks |
| Event Loop | Event Loop |
| setTimeout | asyncio.sleep |

---

# Key Takeaways

### Coroutine

```text
Defines async work
```

Example:

```python
async def fetch():
    ...
```

---

### Task

```text
Schedules and runs async work
```

Example:

```python
task = asyncio.create_task(fetch())
```

---

### Future

```text
Represents a result that will exist later
```

Example:

```python
future = asyncio.Future()
```

---

# Final Mental Model

```text
async def
    ↓
Coroutine
    ↓
create_task()
    ↓
Task
    ↓
awaits
    ↓
Future
    ↓
completed by
    ↓
Event Loop
```

Or even simpler:

```text
Coroutine = What to do
Task      = Running it
Future    = Result arrives later
EventLoop = Coordinator
```