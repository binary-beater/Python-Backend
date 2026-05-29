# Python Coroutines vs Normal Functions

## 1. Normal (Synchronous) Functions

A normal Python function is defined using `def`.

```python
def main():
    print("Hello")
```

When you call it:

```python
main()
```

Python immediately:

1. Enters the function
2. Executes all statements
3. Returns the result

So execution happens directly.

---

## 2. Async Functions

An async function is defined using `async def`.

```python
async def main():
    print("Hello")
```

Calling it:

```python
main()
```

does **NOT** execute the function body immediately.

Instead, Python creates a **coroutine object**.

---

# What is a Coroutine Object?

A coroutine object is:

> A paused, runnable representation of an async function.

Think of it like:

* a task description
* a suspended computation
* work waiting to be executed

Example:

```python
coro = main()
print(coro)
```

Output:

```python
<coroutine object main at 0x...>
```

At this point:

* `print("Hello")` has NOT run
* the function body has NOT started
* Python only created the coroutine object

---

# Why Async Functions Behave Differently

Async functions may contain:

```python
await something()
```

Example:

```python
await asyncio.sleep(1)
```

When Python sees `await`, it must:

1. Pause the current coroutine
2. Let other coroutines run
3. Resume later when ready

This requires a scheduler.

That scheduler is the **event loop**.

---

# What the Event Loop Does

The event loop:

* runs coroutines
* pauses/resumes them
* handles timers
* manages async I/O
* switches between tasks

Without an event loop:

* `await` cannot work
* coroutines cannot progress
* async code never executes

---

# Why `asyncio.run(main())` Works

```python
asyncio.run(main())
```

does this internally:

1. Creates an event loop
2. Schedules `main()` on it
3. Runs until completion
4. Cleans up resources

So this:

```python
asyncio.run(main())
```

means:

> "Execute this coroutine using an event loop."

---

# Synchronous vs Async Execution

## Synchronous

```python
def main():
    print("Hello")

main()
```

Flow:

```text
call function
→ execute immediately
→ return
```

---

## Async

```python
async def main():
    print("Hello")

main()
```

Flow:

```text
call async function
→ create coroutine object
→ no execution yet
```

Then:

```python
asyncio.run(main())
```

Flow:

```text
create event loop
→ run coroutine
→ execute function body
→ complete
```

---

# Important Mental Model

## Normal Function

```python
result = main()
```

means:

> "Run this function now."

---

## Async Function

```python
coro = main()
```

means:

> "Create a coroutine that can be run later."

And:

```python
asyncio.run(coro)
```

means:

> "Actually execute it."

---

# Simple Analogy

## Normal Function

Like pressing a microwave button:

```text
Press button → starts immediately
```

---

## Coroutine

Like preparing a cooking recipe card:

```text
Create recipe → nothing cooks yet
Need a chef (event loop) to execute it
```

---

# Key Takeaways

* `def` functions execute immediately when called
* `async def` functions return coroutine objects
* Coroutine objects do not run by themselves
* The event loop executes coroutines
* `asyncio.run()` creates and manages the event loop
* `await` only works inside a running event loop
