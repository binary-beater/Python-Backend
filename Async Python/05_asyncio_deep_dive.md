# Asyncio Deep Dive: Coroutines, Tasks, Futures, and the Event Loop

## Mental Model in One Sentence

> A **Task** is a scheduler-managed **Future** that drives a **Coroutine** forward. The coroutine stores its execution state, while the Task stores scheduling state and the eventual result.

---

# 1. The Main Actors

## Coroutine

A coroutine is an async function that has been called but not necessarily executed.

```python
async def fetch():
    await asyncio.sleep(1)
    return "hello"

coro = fetch()
```

Think of a coroutine as a **paused function**.

### Stores

* Function code
* Execution frame
* Local variables
* Instruction pointer (where to resume)
* Current state

Conceptually:

```text
Coroutine
├── Code
├── Frame
│   ├── locals
│   ├── stack
│   └── instruction pointer
└── State
```

---

## Task

A Task wraps a coroutine and is managed by the event loop.

```python
task = asyncio.create_task(fetch())
```

Think of a Task as:

> "A scheduler entry that knows how to run and monitor a coroutine."

### Stores

* Reference to coroutine
* Current state
* Result
* Exception
* Callbacks
* What it's currently waiting for

Conceptually:

```text
Task
├── Coroutine
├── State
├── Result
├── Exception
├── Callbacks
└── Waiting For
```

---

## Future

A Future is simply:

> "A placeholder for a value that will exist later."

Example:

```python
future = Future()

future.set_result("hello")
```

Conceptually:

```text
Future
├── done?
├── result?
└── callbacks
```

---

# 2. Relationship Between Them

```text
Task
 │
 ▼
Coroutine
 │
 ▼
await Future
```

A Task runs a Coroutine.

A Coroutine awaits Futures.

When a Future completes, the Task resumes the Coroutine.

---

# 3. What Happens During await?

Example:

```python
async def fetch():
    x = 10

    await asyncio.sleep(1)

    return x + 5
```

Execution reaches:

```python
await asyncio.sleep(1)
```

Coroutine pauses.

Stored state:

```text
Coroutine Frame
├── x = 10
├── instruction pointer
└── execution stack
```

Nothing is lost.

This is similar to a game save file.

---

# 4. How Resumption Works

Imagine:

```python
async def fetch():
    print("A")
    await asyncio.sleep(1)
    print("B")
```

Conceptually:

```text
1. print("A")
2. await sleep
3. print("B")
4. return
```

After suspension:

```text
Current Position = 3
```

When resumed:

```text
Continue from Position = 3
```

Execution does NOT restart.

---

# 5. Task Lifecycle

```text
PENDING
   │
   ▼
RUNNING
   │
   ▼
FINISHED
```

or

```text
PENDING
   │
   ▼
RUNNING
   │
   ▼
EXCEPTION
```

or

```text
PENDING
   │
   ▼
RUNNING
   │
   ▼
CANCELLED
```

---

# 6. Where Is the Result Stored?

Example:

```python
task = asyncio.create_task(fetch())

await task
```

After completion:

```text
Task
├── state = FINISHED
├── result = "hello"
└── exception = None
```

The result is cached inside the Task.

---

# 7. Why Can We Await the Same Task Multiple Times?

```python
task = asyncio.create_task(fetch())

await task
await task
await task
```

The coroutine executes only once.

After completion:

```text
Task
├── FINISHED
└── result = "hello"
```

Subsequent awaits simply return the stored result.

Conceptually:

```python
if task.done():
    return task.result()
```

---

# 8. Event Loop Scheduling

## Important

Asyncio is NOT preemptive.

The event loop cannot interrupt a running task.

A task runs until it:

* hits await
* returns
* raises an exception

Example:

```python
async def bad():
    while True:
        pass
```

This blocks the entire event loop.

---

# 9. Cooperative Multitasking

Asyncio uses cooperative scheduling.

A task voluntarily gives up control:

```python
await something
```

or

```python
await asyncio.sleep(0)
```

Think:

```text
Task A:
"Here's the CPU, someone else can run."
```

---

# 10. OS Threads vs Asyncio Tasks

## OS Threads

```text
Thread A running

(timer interrupt)

Thread B running
```

The OS can forcibly switch.

### Scheduling Type

Preemptive

---

## Asyncio Tasks

```text
Task A running
Task B ready

Task A continues

Task A reaches await

Task B runs
```

The event loop cannot interrupt.

### Scheduling Type

Cooperative

---

# 11. Is Asyncio FIFO?

Not strictly.

The practical rule is:

> Tasks run when they become ready.

Ready tasks are generally queued in order, but correctness should never depend on FIFO scheduling.

Think:

```text
Ready Queue
─────────────
Task A
Task B
Task C
─────────────
```

Usually processed in insertion order.

But asyncio only guarantees readiness-based scheduling.

---

# 12. How Sleep Works Internally

```python
await asyncio.sleep(1)
```

Conceptually:

```python
future = Future()

start_timer(
    1,
    lambda: future.set_result(None)
)

await future
```

So:

```text
sleep
 │
 ▼
Future
```

Sleep is basically a timer-backed Future.

---

# 13. Why Tasks Need Futures

Suppose:

```python
await future
```

The coroutine tells the Task:

```text
I can't continue yet.
Wake me when this Future completes.
```

Task records:

```text
Task
├── waiting_for = future
└── state = PENDING
```

Task then registers:

```python
future.add_done_callback(wake_task)
```

---

# 14. Future Completion Flow

```text
Future
   │
   ▼
Result Available
   │
   ▼
Callback Fires
   │
   ▼
Task Becomes Ready
   │
   ▼
Coroutine Resumes
```

---

# 15. Why Task Is a Subclass of Future

A Future represents:

```text
A value that will exist later
```

A Task also represents:

```text
The result of a coroutine that will exist later
```

Both provide:

```python
done()
result()
exception()
```

Therefore conceptually:

```python
class Task(Future):
    ...
```

---

# 16. Complete Execution Flow

Example:

```python
task = asyncio.create_task(fetch())

await task
```

Internally:

```text
Task Created
      │
      ▼
Coroutine Starts
      │
      ▼
await sleep()
      │
      ▼
Future Created
      │
      ▼
Task Suspended
      │
      ▼
Timer Expires
      │
      ▼
Future Completed
      │
      ▼
Task Woken Up
      │
      ▼
Coroutine Resumed
      │
      ▼
Coroutine Returns
      │
      ▼
Task Stores Result
      │
      ▼
await task Receives Result
```

---

# Ultimate Comparison Table

| Concept    | Think Of It As            | Stores                              |
| ---------- | ------------------------- | ----------------------------------- |
| Coroutine  | Paused function           | Frame, locals, instruction pointer  |
| Task       | Manager/scheduler         | State, result, exception, callbacks |
| Future     | Promise of a future value | Result, done status, callbacks      |
| Event Loop | Scheduler                 | Ready queue and I/O monitoring      |
| await      | Voluntary yield           | Suspends coroutine                  |
| sleep()    | Timer-backed Future       | Completes after timer expires       |

---

# One Final Mental Picture

```text
Event Loop
    │
    ▼
 Task
    │
    ▼
 Coroutine
    │
    ▼
 await Future
    │
    ▼
 External Event
 (timer/socket/file/etc.)
```

When the external event finishes:

```text
External Event
      │
      ▼
 Future Completes
      │
      ▼
 Task Wakes Up
      │
      ▼
 Coroutine Continues
      │
      ▼
 Result Stored In Task
      │
      ▼
 Awaiters Receive Result
```

This is the core architecture of asyncio.
