from time import time
import httpx
import asyncio


async def send_async_request(client, url: str):
    resp = await client.get(url)
    return resp


async def main():
    tasks = []

    t0 = time()
    async with httpx.AsyncClient() as client:
        url = "http://127.0.0.1:8000"
        try:
            for i in range(3000):
                tasks.append(asyncio.create_task(send_async_request(client, url)))  # type: ignore

            responses = await asyncio.gather(*tasks)
            if all([res.status_code == 200 for res in responses]):
                print("All requests were successfull")
            else:
                print("Some requests were not successfull.")
                print(responses)
        except Exception as e:
            print("Exception:", e)
            print(f"Sent {i} requests.")  # type: ignore
    print("Time:", time() - t0)


if __name__ == "__main__":
    asyncio.run(main())
