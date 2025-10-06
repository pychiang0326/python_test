import asyncio
import random

async def fetch_data(api):
    print(f"Fetching data from {api}...")
    await asyncio.sleep(random.randint(1, 3))  # Simulate network delay
    return f"Data from {api}"

async def main():
    apis = ['API 1', 'API 2', 'API 3']
    # Create a list of tasks (which are Futures)
    futures = [asyncio.create_task(fetch_data(api)) for api in apis]
    # Wait for all futures to complete and gather their results
    results = await asyncio.gather(*futures)
    print(results)

asyncio.run(main())
