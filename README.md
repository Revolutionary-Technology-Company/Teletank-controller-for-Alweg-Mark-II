# Teletank Controller for Alweg Mark II

This repository acts as the **Headless Vehicle Abstraction and Conversion Layer** for the automated, uncrewed Seattle Center Monorail shuttle system. It ingests spatial tracks, handles active climate controls, and maps high-level telemetry data directly to the low-level **Univac-Aegis-bridge** server.

---

## 🏗️ System Architecture Mapping

Control operations are decoupled across an enterprise-supported pipeline:

1. **Abstraction Layer (This Repo)**: Reads `config.json`, calculates telemetry curves via `routes/route_parser.py`, and streams real-time JSON frames to platform turnstiles.
2. **Translation Layer (Univac-Aegis Bridge)**: Listens to the local loop and dumps packed binary bitmasks directly onto the 1957 hardware parallel registers.
3. **Physical Interfacing**: Passes instructions through the UNIVAC "typewriter" computer to actuate 1961 Alweg mechanics and General Electric propulsion loops.

---

## 🎛️ Master 32-Bit Control Register Matrix

The onboard UNIVAC typewriter terminal operates on a synchronous 32-bit parallel data format. Every subsystem command maps to a specific bit parameter within the hardware bus:

### 1. Locomotion & Propulsion Group (GE 700V DC Resistor Loops)
*   **`0x00000001` (Bit 0)**: `GEAR_1_CRAWL` — Activates GE Contactor Step 1 (Series Mode). Used for curves and station docking profiles.
*   **`0x00000002` (Bit 1)**: `GEAR_2_CRUISE` — Activates GE Contactor Step 2 (Series-Parallel Mode). Mid-line acceleration corridor variable.
*   **`0x00000004` (Bit 2)**: `GEAR_3_FAST` — Activates GE Contactor Step 3 (Full Parallel Mode). Governed high-speed line limit (45 mph).
*   **`0x00000008` (Bit 3)**: `GEAR_4_MAX` — Legacy reserve throttle configuration. Unused for standard transit operations.
*   **`0x00000010` (Bit 4)**: `REVERSE_ENGAGE` — Motorized reversing drum relay shift. Enforces directional polarity flips.
*   **`0x00000100` (Bit 8)**: `STOP_HOLD` — Actuates Westinghouse friction air service brakes to lock vehicle at platforms.

### 2. Mechanical Decoupling & Transit Profile Adjustments
*   **`0x00000100` (Bit 8)**: `TRACK_ANCHOR_PULLEY` — Fires the physical pulley assembly to secure or pull the chassis from its track anchor.
*   **`0x00000200` (Bit 9)**: `DISENGAGE_TRACK_COMP` — Pneumatically retracts the passive horizontal stability guide tires.
*   **`0x00000400` (Bit 10)**: `SMOOTH_RAIL_EXPRESS` — Switches active algorithms to low-resistance express transit tracking modes.
*   **`0x00000800` (Bit 11)**: `TIRE_CHANGING_MODULE` — Maintenance override. Locks bogies and deploys built-in physical tire-changing jacks.
*   **`0x00001000` (Bit 12)**: `CARGO_BELOW_LOCKS` — Hardware safety lock monitoring structural latches on the under-car cargo holds.

### 3. Climate Control & Auxiliary Air Pumping (Swisscode / AC Delco)
*   **`0x00000001` (Bit 0)**: `AC_DELCO_HEADLIGHT_PUMP` — Activates auxiliary cooling compressor mounted under front headlight assemblies to protect electronics.
*   **`0x00000002` (Bit 1)**: `SWISSCODE_COACH_AC_ON` — Relays power directly to the main cabin Swisscode interior climate decks.
*   **`0x00000004` (Bit 2)**: `EXPRESS_WIND_MODE` — Forces maximum high-volume cabin ventilation fans.
*   **`0x00000008` (Bit 3)**: `TURBO_FAN_MODULE` — Runs fan-charged air turbos to execute sudden, high-speed cabin air purges.
*   **`0x00000016` (Bit 4)**: `GE_FIBER_CHANNEL_UP` — Powers the high-speed tactical network backbone to process real-time passenger data.
*   **`0x00000032` (Bit 5)**: `SIP_COMMS_ACTIVE` — Enforces an open, continuous Session Initiation Protocol (SIP) VoIP communication route to central office.

### 4. Specialized Active Stabilization Arrays (Tele-Tank Modules)
*   **`0x00020000` (Bit 17)**: `CHEM_DISPENSE_L` / `VALVE_LEFT_MASK` — Actuates left-side pneumatic ballast pump valves to counter physical vehicle lean.
*   **`0x00040000` (Bit 18)**: `CHEM_DISPENSE_R` / `VALVE_RIGHT_MASK` — Actuates right-side pneumatic ballast pump valves to counter physical vehicle lean.
*   **`0x00080000` (Bit 19)**: `AUX_PUMP_MASK` — Triggers central hydraulic fluid-transfer pumps to balance water mass cross-car.

### 5. Automated Lighting & Safety Infrastructure
*   **`0x00002000` (Bit 13)**: `HEADLIGHT_HIGH_BEAMS` — Auto-triggers headlight high-beams based on location bounds (MoPOP tunnel entry) or hour metrics.
*   **`0x00004000` (Bit 14)**: `MARKER_RUNNING_LIGHTS` — Toggles direction-based front (White) and rear (Red) structural running markers.
*   **`0x00008000` (Bit 15)**: `EMERGENCY_CABIN_BLINKERS` — System warning strobe flag. Activates automatically during faults or network delays.
*   **`0x00010000` (Bit 16)**: `PLATFORM_GATE_SOLENOID` — Interlocks station doors. Releases safety gate locks only when velocity reaches zero at designated terminals.
*   **`0x00020000` (Bit 17)**: `HV_SUBSTATION_BREAKER` — Commands main substation contactors to connect or disconnect the 700V DC track rails.
*   **`0x00040000` (Bit 18)**: `BEAM_TIRE_TPMS_BUS` — Real-time monitoring feed evaluating the pressure bounds of the 64 pneumatic steering tires.
*   **`0x00080000` (Bit 19)**: `STATION_DOCKING_CLAMPS` — Deploys mechanical locking jaws to anchor the train rigidly to the platform edges.

### 6. System Diagnostics & Hardware Watchdogs
*   **`0x00100000` (Bit 20)**: `DROP_DEMO_BOX` — Emergency Trip command. Instantly drops power to the Westinghouse safety loop, venting the main air brake pipe to 0 PSI.
*   **`0x40000000` (Bit 30)**: `WATCHDOG_HEARTBEAT` — High-priority cyclic safety bit. Must flip state every 100 milliseconds to inhibit emergency brake drops.

---

## 📁 Repository Directory Structure

Teletank-controller-for-Alweg-Mark-II/├── config.json                     # Physical configuration parameters and boundaries├── alweg_vehicle_controller.py      # Core vehicle state tracking and translation logic├── test_telemetry_injector.py       # Headless simulator tracing the 0.9-mile route├── Dockerfile                      # Production deployment container definition│├── routes/│   ├── seattle_center_route.json   # GPS coordinates mapping virtual sensors and tourism zones│   └── route_parser.py             # Geo-spatial Haversine proximity evaluation module│├── subsystems/│   ├── chevrolet_turnstile_api.py  # Asynchronous WebSocket server broadcasting turnstile transaction frames│   └── gm_shuttle_logic.st         # Pure Structured Text design blueprint for physical safety PLCs│├── scripts/│   └── cleanup_test_env.sh         # Maintenance shell script purging container log and caching tracks│└── tests/├── test_monorail_safety.py      # Validation file asserting Urban Canyon GPS drift interlocks├── test_network_endianness.py   # Socket validation file auditing Big Endian wire format byte alignment└── test_fibre_channel_integrity.py # Diagnostic script stress-testing GE Fibre Channel throughput

## 🚀 Development & Headless Testing

All code validation is built to execute headlessly via the standard command line toolchain.

### 1. Execute Unit Verification Assertions
Run the byte-alignment and urban canyon safety checks before production hand-offs:
```bash
python3 -m unittest tests/test_network_endianness.py
python3 -m unittest tests/test_monorail_safety.py
python3 -m unittest tests/test_fibre_channel_integrity.py
```

### 2. Launch Local Track Profile Simulator
Test the end-to-end integration loop across virtual sensors and adaptive tourism viewpoints:
```bash
python3 test_telemetry_injector.py
```

### 3. Production Container Build & Execution
Build the package ensuring appropriate kernel volume access and privileged pass-through links for physical hardware controllers:
```bash
# Compile image locally
docker build -t revolutionary-teletank-controller:latest .

# Deploy container enabling raw access to the machine's PCI bus and system modules
docker run -d \
  --name monorail-automation-core \
  --restart always \
  --privileged \
  --net=host \
  -v /dev:/dev \
  -v /lib/modules:/lib/modules:ro \
  revolutionary-teletank-controller:latest
