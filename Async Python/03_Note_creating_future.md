# Difference Between `asyncio.Future()` and `loop.create_future()`

You'll commonly see both of these:

```python
future = asyncio.Future()
```

and

```python
loop = asyncio.get_running_loop()
future = loop.create_future()
```

They both create a Future object, but there are important differences.

---

# Short Answer

For modern asyncio code:

```python
loop.create_future()
```

is the preferred approach.

Reason:

- Ensures the Future is bound to the correct event loop
- Allows custom event loops to provide optimized Future implementations
- More flexible and framework-friendly

---

# 1. `asyncio.Future()`

```python
future = asyncio.Future()
```

Creates a Future directly.

Internally (simplified):

```python
future = Future()
```

The Future must be associated with an event loop.

In modern Python, it uses the currently running loop.

Example:

```python
async def main():
    future = asyncio.Future()
```

This works because an event loop is already running.

---

## Problem

Imagine an alternative event loop implementation:

```python
uvloop
```

A framework may want to provide its own optimized Future type.

When you write:

```python
asyncio.Future()
```

you're explicitly asking for asyncio's Future implementation.

That bypasses the loop's ability to customize future creation.

---

# 2. `loop.create_future()`

```python
loop = asyncio.get_running_loop()

future = loop.create_future()
```

Instead of constructing a Future directly, you're asking:

> "Event loop, please create a Future for me."

---

## Why This Matters

Different event loops can override future creation.

Conceptually:

```python
class CustomLoop:
    def create_future(self):
        return FastFuture()
```

Then:

```python
future = loop.create_future()
```

returns:

```python
FastFuture()
```

instead of:

```python
asyncio.Future()
```

This gives event loop implementations freedom to optimize.

---

# CPython Default Loop

With the standard asyncio event loop:

```python
future1 = asyncio.Future()

loop = asyncio.get_running_loop()
future2 = loop.create_future()
```

Both are effectively:

```python
<class '_asyncio.Future'>
```

So in everyday code they appear identical.

Example:

```python
print(type(future1))
print(type(future2))
```

Output:

```text
<class '_asyncio.Future'>
<class '_asyncio.Future'>
```

---

# Why the Documentation Recommends `create_future()`

The asyncio docs explicitly recommend:

```python
loop.create_future()
```

because it allows alternative event loops to inject specialized Future implementations.

Think of it like:

```python
# Less flexible
obj = ConcreteClass()

# More flexible
obj = factory.create()
```

`create_future()` is the factory pattern.

---

# Historical Context

Older asyncio versions required explicit loop management:

```python
loop = asyncio.get_event_loop()

future = asyncio.Future(loop=loop)
```

The loop parameter has since been removed from most APIs.

Modern style:

```python
loop = asyncio.get_running_loop()
future = loop.create_future()
```

---

# When Should You Use Each?

## Application Code

Most of the time:

```python
await coroutine()
```

or

```python
asyncio.create_task()
```

You rarely create Futures yourself.

If you do:

```python
loop.create_future()
```

is preferred.

---

## Library / Framework Code

Definitely prefer:

```python
loop.create_future()
```

because:

- Works with custom loops
- More future-proof
- Recommended by asyncio docs

---

# Example

Producer-consumer coordination:

```python
import asyncio

async def producer(future):
    await asyncio.sleep(1)
    future.set_result("done")

async def main():
    loop = asyncio.get_running_loop()

    future = loop.create_future()

    asyncio.create_task(producer(future))

    result = await future

    print(result)

asyncio.run(main())
```

Output:

```text
done
```

---

# Mental Model

### `asyncio.Future()`

```text
Create a Future directly
```

Like:

```python
car = Toyota()
```

---

### `loop.create_future()`

```text
Ask the event loop to create a Future
```

Like:

```python
car = factory.create_car()
```

The factory decides which implementation to return.

---

# Recommendation

Use:

```python
loop = asyncio.get_running_loop()
future = loop.create_future()
```

when you need to manually create a Future.

Avoid:

```python
future = asyncio.Future()
```

unless you have a specific reason to instantiate the concrete Future class directly.

For most asyncio application code, you won't need either—Tasks and coroutines are usually sufficient.