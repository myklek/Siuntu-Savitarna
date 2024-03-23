from weight_service import WeightService
import websockets
import asyncio


WEIGHT_CHANGE_THRESHOLD = 0.2
STABLE_READINGS_REQUIRED = 5
async def init_websocket():
    # uri = "ws://192.168.1.122:4040/ws"
    uri = "ws://192.168.1.82:4040/ws"
    websocket = await websockets.connect(uri, ping_interval=None, ping_timeout=None)
    return websocket


async def send_weight(websocket, weight):
    await websocket.send(str(weight))


async def main():
    websocket = await init_websocket()
    weight_service = WeightService()

    last_weight = weight_service.get_weight()
    stable_readings = 0

    while True:
        sleep_time = 0.1
        await asyncio.sleep(sleep_time)
        weight = weight_service.get_weight()
        print("Weight: ", weight)
        if abs(weight - last_weight) < WEIGHT_CHANGE_THRESHOLD:
            stable_readings += 1
        else:
            stable_readings = 0

            # If the weight has been stable for the required number of readings, send it
        if stable_readings >= STABLE_READINGS_REQUIRED:
            print("Weight has stabilized. Sending weight...")
            await send_weight(websocket, weight)
            stable_readings = 0

        last_weight = weight


if __name__ == "__main__":
    print("Hello World!")
    asyncio.run(main())
