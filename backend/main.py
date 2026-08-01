from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database.database import init_db
from api.routes import router as api_router
from api.websocket import ws_manager
from utils.generator import generate_synthetic_hospital_datasets
import os

app = FastAPI(
    title="TrustFed 2.0 Backend",
    description="Enterprise Privacy-Preserving Healthcare Federated Learning Platform API",
    version="2.0.0"
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://vision-x-2-trust-fed.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

@app.on_event("startup")
def startup_event():
    init_db()
    data_dir = os.path.join(os.path.dirname(__file__), "synthetic_data")
    generate_synthetic_hospital_datasets(data_dir)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "platform": "TrustFed 2.0",
        "status": "Online",
        "privacy_shield": "Active",
        "federated_engine": "Flower Framework + Dynamic Z-Score Trust Strategy"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo ping / client heartbeats
            await websocket.send_json({"status": "connected", "echo": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    
    return {
        "status": "online",
        "message": "TrustFed Backend Running"
    }