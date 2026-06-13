# asyncio: Coroutine vs Task vs gather() vs TaskGroup

## Core Concepts

### Coroutine

Calling an async function does **not** start execution.

```python
coro = fetch_data(1)
```

- Returns a coroutine object.
- Not scheduled.
- Not running.
- Event loop doesn't know about it yet.

Think:

> A recipe waiting to be cooked.

---

### Task

A Task wraps a coroutine and schedules it immediately.

```python
task = asyncio.create_task(fetch_data(1))
```

- Scheduled on the event loop.
- Starts running as soon as the loop gets control.
- Can run independently.

Think:

> A chef actively cooking the recipe.

---

## Manual Task Creation

```python
task1 = asyncio.create_task(fetch_data(1))
task2 = asyncio.create_task(fetch_data(2))

result1 = await task1
result2 = await task2
```

### What Happens?

1. `task1` starts running.
2. `task2` starts running.
3. Both execute concurrently.
4. `await task1` waits only if task1 isn't finished.
5. `await task2` waits only if task2 isn't finished.

### Use When

- Need individual task references.
- Need cancellation.
- Need status inspection.
- Need background execution.

---

## gather() with Coroutines

```python
results = await asyncio.gather(
    fetch_data(1),
    fetch_data(2)
)
```

### What Happens?

`gather()` automatically converts coroutines into tasks.

Internally similar to:

```python
task1 = asyncio.create_task(fetch_data(1))
task2 = asyncio.create_task(fetch_data(2))

await task1
await task2
```

### Use When

- Running multiple independent async operations.
- Need results collected in order.

---

## gather() with Tasks

```python
task1 = asyncio.create_task(fetch_data(1))
task2 = asyncio.create_task(fetch_data(2))

results = await asyncio.gather(task1, task2)
```

### Difference

Tasks are already running.

`gather()` simply waits for them.

### Use When

Tasks were started earlier and you want to wait for all of them later.

---

# Error Handling

## 1. Individual Tasks

```python
t1 = asyncio.create_task(good())
t2 = asyncio.create_task(bad())

try:
    await t2
except Exception:
    pass

await t1
```

### Behavior

```text
bad fails
good continues
```

Failure of one task does not affect others.

---

## 2. gather() (default)

```python
await asyncio.gather(
    good(),
    bad()
)
```

### Behavior

```text
bad fails
gather raises exception
good may continue running
```

Important:

- Exception propagates immediately.
- Other tasks are NOT automatically cancelled.

---

## 3. gather(return_exceptions=True)

```python
results = await asyncio.gather(
    good(),
    bad(),
    return_exceptions=True
)
```

### Result

```python
[
    "good result",
    ValueError("boom")
]
```

### Behavior

```text
bad fails
good continues
all tasks complete
exceptions become results
```

### Use When

You want all tasks to finish regardless of failures.

Examples:

- Multiple API calls
- Batch processing
- Scraping many URLs

---

## 4. TaskGroup

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(good())
    tg.create_task(bad())
```

### Behavior

```text
bad fails
good is cancelled
ExceptionGroup raised
```

### What Happens?

1. One task raises exception.
2. TaskGroup cancels remaining tasks.
3. Waits for cancellations.
4. Raises ExceptionGroup.

---

# Visual Comparison

## Individual Tasks

```text
bad ----X
good -------->
```

Other tasks continue.

---

## gather()

```text
bad ----X
good -------->

gather raises exception
```

Other tasks may continue.

---

## gather(return_exceptions=True)

```text
bad ----X
good -------->

results:
[Exception, Success]
```

Everything completes.

---

## TaskGroup

```text
bad ----X
good ----CANCELLED

ExceptionGroup
```

Failure cancels siblings.

---

# Result Handling

## gather()

Returns results directly.

```python
results = await asyncio.gather(...)
```

---

## TaskGroup

Does not aggregate results.

Keep references yourself.

```python
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch_data(1))
    t2 = tg.create_task(fetch_data(2))

print(t1.result())
print(t2.result())
```

---

# When To Use What?

## create_task()

Use when:

- Starting work immediately.
- Awaiting later.
- Managing individual tasks.

```python
download_task = asyncio.create_task(download())
```

---

## gather()

Use when:

- Tasks are independent.
- Need all results collected.

```python
results = await asyncio.gather(
    fetch_users(),
    fetch_orders(),
    fetch_products()
)
```

---

## gather(return_exceptions=True)

Use when:

- Some tasks may fail.
- Want successes and failures together.

```python
results = await asyncio.gather(
    *tasks,
    return_exceptions=True
)
```

---

## TaskGroup

Use when:

- Tasks belong to one logical operation.
- Failure in one should stop all.

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(charge_card())
    tg.create_task(update_inventory())
    tg.create_task(send_email())
```

If one fails, the rest are cancelled.

---

# Quick Mental Model

| Feature | Coroutine | Task | gather | TaskGroup |
|----------|-----------|--------|---------|-----------|
| Starts immediately | ❌ | ✅ | ✅ | ✅ |
| Runs concurrently | ❌ | ✅ | ✅ | ✅ |
| Returns results | ❌ | Via await | ✅ | Via task.result() |
| Auto-cancels siblings on failure | ❌ | ❌ | ❌ | ✅ |
| Structured concurrency | ❌ | ❌ | ❌ | ✅ |
| Best use case | Definition of work | Background work | Independent parallel tasks | Related tasks that must succeed/fail together |

---

# Modern Recommendation

- Use `TaskGroup` for related subtasks that form a single operation.
- Use `gather(return_exceptions=True)` when collecting results from independent tasks where some failures are acceptable.
- Use `create_task()` when work should start immediately and be awaited later.