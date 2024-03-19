from weight_service import WeightService
import websockets
import asyncio


async def init_websocket():
    uri = "ws://192.168.1.82:4040/ws"
    websocket = await websockets.connect(uri, ping_interval=None, ping_timeout=None)
    return websocket


async def send_weight(websocket, weight):
    await websocket.send(str(weight))


async def main():
    websocket = await init_websocket()
    weight_service = WeightService()

    while True:
        sleep_time = 0.2
        await asyncio.sleep(sleep_time)
        weight = weight_service.get_weight()
        print("Weight: ", weight)
        await send_weight(websocket, weight)


if __name__ == "__main__":
    print("Hello World!")
    asyncio.run(main())
