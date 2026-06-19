# UNIVAC Typewriter Master Register Specification

The onboard tactical computing interface terminal processes a single 32-bit parallel register format (`DWORD`). This document details the exact allocation blocks required by the hardware wiring engineer.

## 1. Locomotion & Propulsion Bit Allocation
*   **`0x00000001` (Bit 0)**: `GEAR_1_CRAWL` — Shifts GE propulsion contactors into Series Mode (Step 1). Engages during curve approaches and station docking maneuvers.
*   **`0x00000002` (Bit 1)**: `GEAR_2_CRUISE` — Shifts GE contactors into Series-Parallel Mode (Step 2). Standard acceleration step.
*   **`0x00000004` (Bit 2)**: `GEAR_3_FAST` — Shifts GE contactors into Full Parallel Mode (Step 3). Governed maximum velocity transit line step (45 mph).
*   **`0x00000100` (Bit 8)**: `STOP_HOLD` — Actuates the pneumatic service brakes to hold the vehicle stationary at platform gates.

## 2. Climate, Communications, & Auxiliary Power Modules
*   **`0x00000001` (Bit 0 - Aux)**: `AC_DELCO_HEADLIGHT_PUMP` — Activates the auxiliary nosepiece cooling compressor mounted beneath the headlight assemblies.
*   **`0x00000002` (Bit 1 - Aux)**: `SWISSCODE_COACH_AC_ON` — Relays power to the main interior Swisscode passenger climate control decks.
*   **`0x00000004` (Bit 2 - Aux)**: `EXPRESS_WIND_MODE` — Forces high-volume cabin ventilation loops to max output.
*   **`0x00000008` (Bit 3 - Aux)**: `TURBO_FAN_MODULE` — Triggers fan-charged air turbos to clear interior cabin air during high-speed transit runs.
*   **`0x00000016` (Bit 4 - Aux)**: `GE_FIBER_CHANNEL_UP` — Powers up the high-speed tactical network backbone to handle real-time passenger data streams.
*   **`0x00000032` (Bit 5 - Aux)**: `SIP_COMMS_ACTIVE` — Enforces an open Session Initiation Protocol (SIP) VoIP channel to the dispatch central command office.

## 3. Structural Mechanics & Active Ballast Stabilization
*   **`0x00000100` (Bit 8 - Mech)**: `TRACK_ANCHOR_PULLEY` — Drives the physical track anchor pulley mechanism to secure the train.
*   **`0x00000200` (Bit 9 - Mech)**: `DISENGAGE_TRACK_COMP` — Retracts horizontal guide tires to transition to Smooth Rail Express mode.
*   **`0x00020000` (Bit 17)**: `VALVE_LEFT_MASK` / `CHEM_DISPENSE_L` — Opens left Tele-tank ballast valve to move liquid mass and level vehicle weight distribution.
*   **`0x00040000` (Bit 18)**: `VALVE_RIGHT_MASK` / `CHEM_DISPENSE_R` — Opens right Tele-tank ballast valve to move liquid mass and level vehicle weight distribution.
*   **`0x00080000` (Bit 19)**: `AUX_PUMP_MASK` — Drives central fluid-transfer pumps to balance water mass dynamically cross-beam.

## 4. Platform Signaling, Station Interlocks, & Watchdogs
*   **`0x00002000` (Bit 13)**: `HEADLIGHT_HIGH_BEAMS` — Automatically triggers the front high-beams when entering the enclosed MoPOP tunnel or during night runs.
*   **`0x00010000` (Bit 16)**: `PLATFORM_GATE_SOLENOID` — Interlocks station doors; opens platform barriers only when train velocity reaches zero.
*   **`0x00080000` (Bit 19 - Aux)**: `STATION_DOCKING_CLAMPS` — Deploys mechanical locking jaws to anchor the train to the platform frame.
*   **`0x00100000` (Bit 20)**: `DROP_DEMO_BOX` — Emergency Trip command. Instantly drops power to the Westinghouse fail-safe safety loop, venting the main air brake pipe to 0 PSI.
*   **`0x40000000` (Bit 30)**: `WATCHDOG_HEARTBEAT` — High-priority safety bit toggling states every 100 milliseconds to inhibit automatic brake dumps.
