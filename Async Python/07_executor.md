# Asyncio, Threads, Processes, Executors, and Pickling

## Big Picture

Python gives us three major ways to achieve concurrency:

1. **Asyncio Coroutines**
2. **Threads**
3. **Processes**

Each solves a different problem.

| Work Type | Recommended Approach |
|------------|------------|
| Async library available | asyncio |
| Blocking I/O | ThreadPoolExecutor / asyncio.to_thread |
| CPU-bound work | ProcessPoolExecutor |

---

# 1. Pure Asyncio

## Example

```python
async def fetch_data(delay):
    await asyncio.sleep(delay)
    return delay
```

```python
task1 = asyncio.create_task(fetch_data(1))
task2 = asyncio.create_task(fetch_data(2))

r1 = await task1
r2 = await task2
```

## How it works

Only a single thread exists.

```text
Event Loop
    |
    +--> Coroutine A
    |
    +--> Coroutine B
```

When a coroutine reaches:

```python
await something
```

it voluntarily yields control back to the event loop.

The event loop then schedules another coroutine.

This is called **cooperative concurrency**.

---

# 2. Why Blocking Code Breaks Asyncio

Example:

```python
def fetch_data():
    time.sleep(5)
```

If executed directly:

```python
async def main():
    fetch_data()
```

the event loop is blocked.

```text
Event Loop
    |
    +--> time.sleep(5)
           ^
           |
           blocks everything
```

No other coroutine can run.

---

# 3. asyncio.to_thread()

Used for running blocking synchronous functions without freezing the event loop.

```python
result = await asyncio.to_thread(fetch_data, 5)
```

Conceptually:

```python
loop.run_in_executor(
    None,
    fetch_data,
    5
)
```

Internally it uses the default ThreadPoolExecutor.

---

## Execution Flow

```text
Main Thread
    |
    +--> Event Loop
            |
            +--> submit work

Worker Thread
    |
    +--> fetch_data()
            |
            +--> time.sleep(5)
```

The blocking operation happens in another thread.

The event loop remains responsive.

---

# 4. ThreadPoolExecutor

## Example

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)
```

Creates worker threads:

```text
Thread-1
Thread-2
Thread-3
Thread-4
```

And maintains a job queue.

```text
Queue
    |
    +--> Job A
    +--> Job B
    +--> Job C
```

Workers consume jobs from the queue.

---

## Good For

Blocking I/O:

```python
requests.get(...)
time.sleep(...)
file reading
database calls
```

---

## Not Good For

CPU-heavy Python code.

Because of the GIL.

---

# 5. GIL (Global Interpreter Lock)

CPython allows only one thread at a time to execute Python bytecode.

Example:

```python
def cpu_work():
    for i in range(100000000):
        pass
```

Running this in two threads:

```text
Thread A
Thread B
```

does NOT provide true parallelism.

The threads take turns holding the GIL.

---

# 6. ProcessPoolExecutor

Used for CPU-bound work.

```python
from concurrent.futures import ProcessPoolExecutor
```

Creates multiple processes:

```text
Main Process

Worker Process 1
Worker Process 2
Worker Process 3
```

Each process has:

- Its own memory
- Its own Python interpreter
- Its own GIL

---

## Why Processes Work For CPU Tasks

Threads:

```text
One GIL
```

Processes:

```text
Process A -> GIL A

Process B -> GIL B
```

Multiple CPU cores can work simultaneously.

True parallelism.

---

# 7. run_in_executor()

Bridge between asyncio and executors.

Example:

```python
loop = asyncio.get_running_loop()

future = loop.run_in_executor(
    executor,
    fetch_data,
    5
)
```

Conceptually:

```python
executor.submit(fetch_data, 5)
```

but wrapped into an awaitable asyncio Future.

---

## Important

The work starts immediately.

Example:

```python
f1 = loop.run_in_executor(executor, work1)
f2 = loop.run_in_executor(executor, work2)

print("Already running")
```

Both jobs have already started.

No create_task() needed.

---

# 8. asyncio.to_thread() vs ThreadPoolExecutor

## asyncio.to_thread()

Simple convenience API.

```python
await asyncio.to_thread(func)
```

Uses default thread pool.

No pool management required.

---

## ThreadPoolExecutor

More control.

```python
executor = ThreadPoolExecutor(
    max_workers=50
)
```

Allows:

- Custom worker count
- Shared executors
- Explicit shutdown
- Thread naming

---

# 9. await asyncio.to_thread() vs create_task()

## Direct Await

```python
await asyncio.to_thread(fetch_data, 1)
```

Execution:

```text
Submit work
Wait immediately
Return result
```

---

## create_task()

```python
task = asyncio.create_task(
    asyncio.to_thread(fetch_data, 1)
)

await task
```

For a single operation:

```text
Practically same result
```

with a tiny amount of extra overhead.

---

## Useful create_task() Example

```python
t1 = asyncio.create_task(
    asyncio.to_thread(fetch_data, 1)
)

t2 = asyncio.create_task(
    asyncio.to_thread(fetch_data, 2)
)

r1 = await t1
r2 = await t2
```

Both thread jobs begin concurrently.

---

# 10. ProcessPoolExecutor Internals

When you do:

```python
executor.submit(
    fetch_data,
    5
)
```

The worker process cannot access your memory.

Instead:

```text
Serialize
Send
Deserialize
Execute
Serialize Result
Send Back
Deserialize
```

This process uses Pickle.

---

# 11. What Is Pickle?

Pickle is Python's serialization mechanism.

Converts Python objects into bytes.

Example:

```python
import pickle

data = {
    "name": "Alice"
}

b = pickle.dumps(data)
```

Now:

```python
type(b)
```

returns:

```python
bytes
```

---

## Unpickling

```python
obj = pickle.loads(b)
```

reconstructs the original object.

---

# 12. Why Pickle Exists

Processes do not share memory.

Example:

```text
Process A Memory
```

cannot directly access

```text
Process B Memory
```

Therefore objects must be converted into bytes and transferred.

---

# 13. Does Pickle Share Memory Addresses?

No.

Suppose:

```python
x = [1,2,3]
```

Memory:

```text
0x123456
```

in Process A means nothing in Process B.

Pickle does NOT send:

```text
Memory address
```

Instead it sends:

```text
Object data
```

required to reconstruct the object.

---

# 14. Does Pickle Serialize Function Code?

Usually NO.

Consider:

```python
def square(x):
    return x*x
```

Pickle generally stores something conceptually like:

```text
module = mymodule
function = square
```

not:

```python
def square(x):
    return x*x
```

When unpickled:

```python
import mymodule

mymodule.square
```

is located and used.

---

# 15. Why Nested Functions Fail

Example:

```python
def outer():

    def square(x):
        return x*x

    return square
```

This function exists only inside:

```python
outer()
```

Another process cannot import:

```python
mymodule.square
```

because it doesn't exist globally.

Error:

```text
Can't pickle local object
```

---

# 16. Why Lambdas Fail

Example:

```python
lambda x: x*x
```

No stable module-level name exists.

Worker process cannot import it.

Thus pickling usually fails.

---

# 17. Closures

Example:

```python
def outer():

    a = 10

    def worker(x):
        return a + x
```

The nested function captures:

```python
a = 10
```

This hidden state is called a closure.

Standard pickle does not serialize arbitrary closures.

Therefore multiprocessing often fails.

---

# 18. What Must Be Pickleable?

For ProcessPoolExecutor:

## 1. Function

```python
executor.submit(func)
```

`func` must be pickleable.

---

## 2. Arguments

```python
executor.submit(func, arg)
```

`arg` must be pickleable.

Good:

```python
list
dict
tuple
int
str
```

Bad:

```python
open file handles
sockets
thread locks
database connections
```

---

## 3. Return Value

```python
def worker():
    return something
```

`something` must be pickleable.

---

# 19. ProcessPoolExecutor Data Flow

```text
Main Process

    fetch_data
    args

        |
        v

    pickle

        |
        v

    IPC Pipe

        |
        v

Worker Process

    unpickle

        |
        v

    execute

        |
        v

    pickle(result)

        |
        v

    IPC Pipe

        |
        v

Main Process

    unpickle(result)
```

---

# 20. Why ProcessPoolExecutor Has Overhead

Every task requires:

```text
Pickle arguments
Send data
Unpickle
Execute
Pickle result
Send back
Unpickle result
```

Threads do not need this.

Threads share memory.

Processes do not.

---

# 21. Large Data Can Be Expensive

Example:

```python
huge_list = list(range(100000000))
```

Submitting:

```python
executor.submit(worker, huge_list)
```

may spend more time in:

```text
Serialization
IPC
Deserialization
```

than actual computation.

---

# 22. cloudpickle and dill

Standard pickle cannot serialize many things:

```python
nested functions
closures
lambdas
```

Libraries like:

```python
cloudpickle
dill
```

can serialize much more, including code objects and closures.

Frameworks like:

- Ray
- Dask
- Joblib

often rely on these advanced serializers.

---

# Final Mental Model

## Asyncio

```text
One Thread

Event Loop
    |
    +--> Coroutine A
    +--> Coroutine B
```

Concurrency through cooperative scheduling.

---

## ThreadPoolExecutor

```text
One Process

Thread A
Thread B
Thread C
```

Shared memory.

Good for blocking I/O.

Limited by GIL for CPU work.

---

## ProcessPoolExecutor

```text
Process A
Process B
Process C
```

Separate memory.

Separate GILs.

True parallelism.

Communication requires:

```text
Pickle
IPC
Unpickle
```

---

## Rule of Thumb

Async operation available?

→ Use asyncio

Blocking I/O?

→ Use asyncio.to_thread() / ThreadPoolExecutor

CPU-intensive Python work?

→ Use ProcessPoolExecutor