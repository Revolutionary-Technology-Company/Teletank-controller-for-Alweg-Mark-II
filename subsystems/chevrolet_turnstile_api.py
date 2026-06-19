#!/usr/bin/env python3
import asyncio
import websockets
import json
import logging
from datetime import datetime

# Configure clean headless console logging output
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] 🎫 CHEVROLET_TURNSTILE_API: %(message)s',
    datefmt='%H:%M:%S'
)

class ChevroletTurnstileServer:
    def __init__(self, host="0.0.0.0", port=8081):
        self.host = host
        self.port = port
        self.connected_platforms = set() # Thread-safe tracking registry for gates

    async def register_connection(self, websocket):
        """Register newly connected turnstile or platform display nodes."""
        self.connected_platforms.add(websocket)
        logging.info(f"New validation terminal connected from {websocket.remote_address}")
        try:
            # Keep connection alive; look for unexpected client disconnects
            await websocket.wait_closed()
        finally:
            self.connected_platforms.remove(websocket)
            logging.info(f"Terminal connection dropped: {websocket.remote_address}")

    async def broadcast_gate_validation(self, sensor_id, state_string):
        """Serializes verification packet and pushes it to all connected hubs."""
        if not self.connected_platforms:
            return

        # Explicit JSON payload structure mapped to your platform requirements
        payload = {
            "turnstile_transaction_frame": {
                "system_timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "gate_node_id": "CHEVROLET_TURNSTILE_NETWORK_HUB",
                "intercept_state": state_string,
                "virtual_sensor_id": sensor_id,
                "command_logic": {
                    "allow_passenger_ingress": True if state_string == "TRAIN_REACHED_PLATFORM" else False,
                    "orca_card_terminal_state": "ACTIVE_VALIDATION_ENABLED" if state_string == "TRAIN_REACHED_PLATFORM" else "STANDBY_HOLD",
                    "platform_safety_doors": "OPEN_COMMAND_FIRED" if state_string == "TRAIN_REACHED_PLATFORM" else "CLOSE_COMMAND_LOCK"
                },
                "hardware_verification_token": "0xABC123FF99"
            }
        }

        message_string = json.dumps(payload)
        
        # Broadcast concurrently across the connected set using copy to avoid modification errors
        logging.info(f"Broadcasting token for checkpoint {sensor_id} to {len(self.connected_platforms)} active terminals.")
        websockets_to_alert = self.connected_platforms.copy()
        
        for ws in websockets_to_alert:
            try:
                await ws.send(message_string)
            except websockets.exceptions.ConnectionClosed:
                pass

    def start_server_loop(self, loop):
        """Initializes non-blocking execution inside the main thread."""
        start_server = websockets.serve(self.register_connection, self.host, self.port)
        loop.run_until_complete(start_server)
        logging.info(f"Headless WebSocket Network Core listening on ws://{self.host}:{self.port}")

