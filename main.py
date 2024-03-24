from fastapi import FastAPI, WebSocket
from threading import Thread, Event

from starlette.websockets import WebSocketDisconnect, WebSocketState

from weight_service import WeightService
import asyncio

app = FastAPI()
weight_service = WeightService()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"status": "connected"})

    stop_event = Event()
    t = None

    def get_stable_weight(stop_event):
        for weight_data in weight_service.get_stable_weight(stop_event):
            asyncio.run(websocket.send_json(weight_data))

    async def read_messages():
        nonlocal t
        while True:
            message_data = await websocket.receive_text()
            print(message_data)
            if message_data == "stopWeightReading":
                stop_event.set()
                if t is not None:
                    t.join()  # Ensure the thread has finished
                t = None
            elif message_data == "getStableWeight":
                if t is None or not t.is_alive():
                    stop_event.clear()
                    t = Thread(target=get_stable_weight, args=(stop_event,))
                    t.start()

    try:
        await asyncio.create_task(read_messages())
    except WebSocketDisconnect:
        # Handle the WebSocket disconnect
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
