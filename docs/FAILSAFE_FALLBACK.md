# Air-Gapped Telemechanical Fallback Specification

## 1. Functional Scope
To prevent a runaway condition or systemic failure in dense urban environments (e.g., GPS reflections within downtown Seattle urban canyons), the train contains a local, air-gapped protection loop: `local_telemechanical_fallback.py`.

## 2. Takeover Trigger Protocol
The primary automation vehicle controller must continuously transmit a network verification pulse to the `Univac-Aegis-bridge` server.

[ Primary Bridge Connected ]│├──► Network Latency > 100ms? ──► YES ──► [ Isolate Remote Sockets ]│                                                  │└──► NO (Maintain Auto Flight)                     ▼[ Polling Modbus Cab Pins ]│▼[ Execute Local Default Trip ]

The moment network latency breaches a strict **100ms execution window**, the local daemon flags a primary bridge timeout, treats the remote connection as dropped, and assumes autonomous local control.

## 3. Modbus TCP Cab-Hardware Abstraction Layer
When fallback execution is active, the daemon opens an internal, non-blocking Modbus TCP master link on port 502 to poll physical operator switches and handles from the cab panel:

*   **Discrete Input 00001 (Offset 0)**: `DI_WESTINGHOUSE_BRAKE_VALVE` — NC limit contact tracking the manual human brake handle. If pulled, it instantly sets bit 20 (`DROP_DEMO_BOX`), venting the air lines to slide the spring shoes closed on the beam.
*   **Discrete Input 00002 (Offset 1)**: `DI_MANUAL_OVERRIDE_KEY` — Cab key selector toggle. Turning this forces manual human operator dominance over all tracking variables.
*   **Input Register 30011 (Offset 10)**: `IR_THROTTLE_LEVER_POSITION` — Analog word tracking the position of the physical throttle lever. Maps integers 0-3 directly to the universal GE contactor register steps.

## 4. Route-Fenced Braking
While operating under fallback control, the system reads `routes/seattle_center_route.json` locally. If the train intercepts the coordinates for terminal docking gates (`VS_00_WESTLAKE_GATE` or `VS_06_SEATTLE_CENTER_GATE`), the code overrides the throttle, commands zero speed, and activates `STOP_HOLD` to stop the train at the platform.
