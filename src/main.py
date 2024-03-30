from fastapi import FastAPI, WebSocket
from threading import Thread, Event

from starlette.websockets import WebSocketDisconnect, WebSocketState

from weight_service import WeightService
from camera_service import CameraService
import asyncio

app = FastAPI()
weight_service = WeightService()
camera_service = CameraService()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"status": "connected"})

    stop_weight_event = Event()
    stop_dimensions_event = Event()
    weight_thread = None
    dimensions_thread = None

    def get_stable_weight(stop_event):
        for weight_data in weight_service.get_stable_weight(stop_event):
            asyncio.run(websocket.send_json(weight_data))

    def get_object_dimensions_thread(stop_event):
        for dimensions in camera_service.get_object_dimensions(stop_event):
            asyncio.run(websocket.send_json(dimensions))

    async def read_messages():
        nonlocal weight_thread
        nonlocal dimensions_thread
        while True:
            message_data = await websocket.receive_text()
            print(message_data)
            if message_data == "stopWeightReading":
                stop_weight_event.set()
                if weight_thread is not None:
                    weight_thread.join()  # Ensure the thread has finished
                weight_thread = None
            elif message_data == "getStableWeight":
                if weight_thread is None or not weight_thread.is_alive():
                    stop_weight_event.clear()
                    weight_thread = Thread(target=get_stable_weight, args=(stop_weight_event,))
                    weight_thread.start()
            elif message_data == "stopObjectDimensionsReading":  # Handle new message type
                stop_dimensions_event.set()
                if dimensions_thread is not None:
                    dimensions_thread.join()  # Ensure the thread has finished
                dimensions_thread = None
            elif message_data == "getObjectDimensions":
                if dimensions_thread is None or not dimensions_thread.is_alive():
                    stop_dimensions_event.clear()
                    dimensions_thread = Thread(target=get_object_dimensions_thread, args=(stop_dimensions_event,))
                    dimensions_thread.start()

    try:
        await asyncio.create_task(read_messages())
    except WebSocketDisconnect:
        # Handle the WebSocket disconnect
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
