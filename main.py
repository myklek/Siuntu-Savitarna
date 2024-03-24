from fastapi import FastAPI, WebSocket

from weight_service import WeightService

app = FastAPI()
weight_service = WeightService()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"status": "connected"})
    while True:
        data = await websocket.receive_text()
        if data == "getStableWeight":
            temp_weights = weight_service.get_stable_weight()
            for weight in temp_weights:
                await websocket.send_json({"weight": weight})
            await websocket.send_json({"stableWeight": weight})
        else:
            await websocket.send_text(f"Message text was: {data}")
