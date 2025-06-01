# Copyright 2024 Soul Machines Ltd

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import dotenv
import uvicorn
from controller import handle_message
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Load environment variables from .env file
dotenv.load_dotenv()
PORT = int(os.getenv("FASTAPI_PORT", 8000))

# Initialize application
app = FastAPI(title="Orchestration-FastAPI")


# WebSocket Server
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("A new client connected")

    try:
        while True:
            data = await ws.receive_text()
            await handle_message(ws, data)
    except WebSocketDisconnect:
        print("Client disconnected")


# Uviorn Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)