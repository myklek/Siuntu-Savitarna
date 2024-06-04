from fastapi import FastAPI, WebSocket
from threading import Thread, Event
import cv2

from starlette.websockets import WebSocketDisconnect, WebSocketState

from weight_service import WeightService
from measuring_service import MeasuringService
from qr_detection_service import QRDetectionService
from distance_service import DistanceService
import asyncio

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MJPG'))

app = FastAPI()
weight_service = WeightService()
distance_service = DistanceService()
qr_detection_service = QRDetectionService(cam)
measuring_service = MeasuringService(cam)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"status": "connected"})

    stop_weight_event = Event()
    stop_dimensions_event = Event()
    stop_qr_detection_event = Event()
    stop_distance_event = Event()
    weight_thread = None
    qr_detection_thread = None
    dimensions_thread = None
    distance_thread = None

    def run_weight(stop_event):
        for weight_data in weight_service.get_stable_weight(stop_event):
            asyncio.run(websocket.send_json(weight_data))

    def run_object_dimensions(stop_event):
        for dimensions in measuring_service.get_object_dimensions(stop_event):
            asyncio.run(websocket.send_json(dimensions))

    def run_qr_detection(stop_event):
        for qr_data in qr_detection_service.get_qr_code_data(stop_event):
            asyncio.run(websocket.send_json(qr_data))

    def run_distance(stop_event):
        for distance_data in distance_service.get_stable_distance(stop_event):
            asyncio.run(websocket.send_json(distance_data))

    async def read_messages():
        # nonlocal weight_thread
        # nonlocal dimensions_thread

        def stop_distance_reading():
            nonlocal distance_thread
            stop_distance_event.set()
            if distance_thread is not None:
                distance_thread.join()
            distance_thread = None

        def get_distance():
            nonlocal distance_thread
            if distance_thread is None or not distance_thread.is_alive():
                stop_distance_event.clear()
                distance_thread = Thread(target=run_distance, args=(stop_distance_event,))
                distance_thread.start()

        def stop_weight_reading():
            nonlocal weight_thread
            stop_weight_event.set()
            if weight_thread is not None:
                weight_thread.join()
            weight_thread = None

        def get_weight():
            nonlocal weight_thread
            if weight_thread is None or not weight_thread.is_alive():
                stop_weight_event.clear()
                weight_thread = Thread(target=run_weight, args=(stop_weight_event,))
                weight_thread.start()

        def stop_object_dimensions_reading():
            nonlocal dimensions_thread
            stop_dimensions_event.set()
            if dimensions_thread is not None:
                dimensions_thread.join()
            dimensions_thread = None
            measuring_service.close()

        def get_object_dimensions():
            nonlocal dimensions_thread
            if dimensions_thread is None or not dimensions_thread.is_alive():
                stop_dimensions_event.clear()
                dimensions_thread = Thread(target=run_object_dimensions, args=(stop_dimensions_event,))
                dimensions_thread.start()

        def stop_qr_detection_reading():
            nonlocal qr_detection_thread
            stop_qr_detection_event.set()
            if qr_detection_thread is not None:
                qr_detection_thread.join()
            qr_detection_thread = None
            qr_detection_service.close()

        def get_qr_code_data():
            nonlocal qr_detection_thread
            if qr_detection_thread is None or not qr_detection_thread.is_alive():
                stop_qr_detection_event.clear()
                qr_detection_thread = Thread(target=run_qr_detection, args=(stop_qr_detection_event,))
                qr_detection_thread.start()

        actions = {
            "stopWeightReading": stop_weight_reading,
            "getWeight": get_weight,
            "stopObjectDimensionsReading": stop_object_dimensions_reading,
            "getObjectDimensions": get_object_dimensions,
            "stopQRDetectionReading": stop_qr_detection_reading,
            "getQRCodeData": get_qr_code_data,
            "stopDistanceReading": stop_distance_reading,
            "getDistance": get_distance
        }
        while True:
            message_data = await websocket.receive_text()
            print('Message recieved: ' + message_data)
            action = actions.get(message_data)
            if action:
                action()

    try:
        await asyncio.create_task(read_messages())
    except WebSocketDisconnect:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
