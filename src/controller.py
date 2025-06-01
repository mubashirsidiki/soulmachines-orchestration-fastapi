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

from typing import Any
from fastapi import WebSocket
from models import (
    SMMessage,
    ConversationRequest,
    ConversationResponse,
)


async def handle_message(ws: WebSocket, raw: str) -> None:
    try:
        print("Raw message received:", raw)  # Debug log
        msg: SMMessage = SMMessage.model_validate_json(raw)
    except Exception as e:
        print("Unrecognized message:", raw)
        print("Error:", str(e))  # Debug log
        return

    # Only process conversation requests
    if msg.name == "conversationRequest":
        try:
            req = ConversationRequest(**msg.body)
            resp = build_response(req)
            await send_message(ws, resp)
        except Exception as e:
            print("Failed to process conversation request:", str(e))
            print("Message body:", msg.body)
    else:
        # Log other message types but don't process them
        print(f"Received {msg.name} message, skipping processing")



def build_response(req: ConversationRequest) -> ConversationResponse:
    print("Conv request:", req.model_dump())

    # Set a simple echo response
    resp = ConversationResponse(
        input={"text": req.input["text"]},
        output={"text": f"Echo: {req.input['text']}"},
        variables={},
    )

    # Handle welcome message
    if req.optionalArgs and req.optionalArgs.get("kind") == "init":
        resp.output["text"] = "Hi there!"

    # Set fallback response example (can be handled by skills in the project)
    if req.input["text"].lower().startswith("why"):
        resp.output["text"] = "I do not know how to answer that"
        resp.fallback = True

    # SM content cards example
    if req.input["text"].lower() == "show card":
        resp.output["text"] = "Here is a cat @showcards(cat)"
        resp.variables["public-cat"] = {
            "component": "image",
            "data": {
                "alt": "A cute kitten",
                "url": "https://img.freepik.com/premium-photo/little-kitten-wrapped-beige-knitted-scarf-shop-goods-cats_132375-1602.jpg?semt=ais_hybrid&w=740",
            },
        }

    return resp

async def send_message(ws: WebSocket, resp: ConversationResponse) -> None:
    wrapper = SMMessage(
        category="scene",
        kind="request",
        name="conversationResponse",
        body=resp.model_dump(mode="python"),
    )
    await ws.send_text(wrapper.model_dump_json())