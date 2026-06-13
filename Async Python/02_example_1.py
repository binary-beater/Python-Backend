# synchronous code example
import time

def fetch_data(param):
    print(f"Do something with {param}...")
    time.sleep(param)
    print(f"Finished processing {param}.")
    return f"Result for {param}"

def main():
    result1 = fetch_data(1)
    print("Fetch 1 fully completed.")
    retult2 = fetch_data(2)
    print("Fetch 2 fully completed.")
    return [result1, retult2]

t1 = time.perf_counter()
results = main()
print(results)

t2 = time.perf_counter()
print(f"Finished in {t2 - t1:.2f} seconds.")