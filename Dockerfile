#!/usr/bin/env python3
import json
import struct
import time
import socket
import logging
from pyModbusTCP.client import ModbusClient  # Standard Python Modbus TCP Master Library
from routes.route_parser import MonorailRouteParser

# Re-defining the Universal Teletank Bitmasks locally to keep the script 100% self-contained
class TeletankBits:
    GEAR_1_CRAWL       = 0x00000001 # Maps to Alweg GE Resistor Step 1 (Series)
    GEAR_2_CRUISE      = 0x00000002 # Maps to Alweg GE Resistor Step 2 (Series-Parallel)
    GEAR_3_FAST        = 0x00000004 # Maps to Alweg GE Resistor Step 3 (Full Parallel)
    STOP_HOLD          = 0x00000100 # Maps to Westinghouse service brakes application
    VALVE_LEFT_MASK    = 0x00020000 # Actuate Left Tele-Tank fluid pump
    VALVE_RIGHT_MASK   = 0x00040000 # Actuate Right Tele-Tank fluid pump
    WATCHDOG_HEARTBEAT = 0x40000000 # Multi-generational 100ms safety ping
    DROP_DEMO_BOX      = 0x00100000 # Emergency Trip (Dump Westinghouse Brake Pipe)

logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] 🚨 LOCAL_TELEMECHANICAL_FALLBACK: %(message)s',
    datefmt='%H:%M:%S'
)

class LocalTelemechanicalFallback:
    def __init__(self, config_path="config.json"):
        # Load local route polygons and constraints
        self.route_engine = MonorailRouteParser()
        self.watchdog_timeout_ms = 100.0
        self.last_bridge_heartbeat = time.perf_counter()
        
        # State tracking flags
        self.is_bridge_connected = True
        self.local_override_active = False
        self.heartbeat_toggle = False

        # --- INDUSTRIAL MODBUS TCP COUPLER CONFIGURATION ---
        # 127.0.0.1 is used for local loop testing. 
        # For the train, your hardware engineer updates this to the target PLC IP (e.g., 192.168.1.50)
        self.plc_ip = "127.0.0.1"
        self.plc_port = 502  # Standard, universal Modbus TCP port
        self.modbus_client = ModbusClient(host=self.plc_ip, port=self.plc_port, auto_open=True, timeout=0.05)

        # Output Socket Configuration (Direct backup hardware map register route)
        self.hardware_ip = "127.0.0.1"
        self.hardware_port = 5006 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def read_physical_cab_hardware(self):
        """
        Headless Industrial Hardware Abstraction Layer (HAL).
        Directly polls physical PLC I/O channels over Modbus TCP registers.
        """
        # --- DEFINED STANDARD REGISTER BOUNDS FOR HARDWARE ENGINEER ---
        # Discrete Inputs (%IX / Read-Only Contact Switches)
        DI_WESTINGHOUSE_BRAKE_VALVE = 0   # Address 00001: True if human operator pulls emergency handle
        DI_MANUAL_OVERRIDE_KEY      = 1   # Address 00002: True if physical key switch turned in cab
        
        # Input Registers (%IW / Read-Only Analog-to-Digital Values)
        IR_THROTTLE_LEVER_POSITION  = 10  # Address 30011: Raw integer step value from physical handle

        # Default safe configuration values if network loop drops completely
        throttle_lever = 0        # 0 = Coast/Neutral
        brake_valve_pulled = True # Default to True (Brakes applied) for safety if PLC falls off link
        override_key = False

        # Execute non-blocking hardware polling cycle over Modbus TCP
        try:
            if self.modbus_client.open():
                # 1. Poll the Discrete Input discrete bit array (Count of 2 coils starting at address 0)
                discrete_inputs = self.modbus_client.read_discrete_inputs(0, 2)
                if discrete_inputs and len(discrete_inputs) >= 2:
                    brake_valve_pulled = discrete_inputs[DI_WESTINGHOUSE_BRAKE_VALVE]
                    override_key = discrete_inputs[DI_MANUAL_OVERRIDE_KEY]

                # 2. Poll the Input Register analog integer block (Count of 1 word starting at address 10)
                input_registers = self.modbus_client.read_input_registers(IR_THROTTLE_LEVER_POSITION, 1)
                if input_registers and len(input_registers) >= 1:
                    raw_throttle = input_registers[0]
                    # Boundary sanitization loop: clamp to standard 1961 GE resistor steps (0 to 3)
                    throttle_lever = max(0, min(raw_throttle, 3))
            else:
                # Hardware Link Fault Warning
                logging.warning("⚠️ Modbus TCP physical PLC link offline. Enforcing safe mechanical default profiles.")
        except Exception as e:
            logging.error(f"Error encountered during Modbus parsing cycle: {e}")
            
        return throttle_lever, brake_valve_pulled, override_key

    def verify_bridge_liveness(self, heartbeat_bit_active):
        """Monitors incoming bridge telemetry pulses to track connection state."""
        current_time = time.perf_counter()
        
        if heartbeat_bit_active:
            self.last_bridge_heartbeat = current_time
            if not self.is_bridge_connected:
                logging.info("🔗 Connection re-established with primary Univac-Aegis Bridge.")
                self.is_bridge_connected = True
        else:
            # Check if elapsed time breaches our strict 100ms enterprise safety window
            elapsed_ms = (current_time - self.last_bridge_heartbeat) * 1000.0
            if elapsed_ms > self.watchdog_timeout_ms and self.is_bridge_connected:
                logging.warning(f"💥 PRIMARY BRIDGE DISCONNECTED ({elapsed_ms:.1f}ms lag). Assuming local telemechanical control.")
                self.is_bridge_connected = False

    def execute_default_transit_cycle(self, current_lat, current_lon, speed_mph, gps_drift):
        """Processes the 100ms air-gapped transit loop using native assets."""
        # 1. Gather human input telemetry and master keys from the cab consoles via Modbus
        cab_throttle, cab_brake, cab_manual_key = self.read_physical_cab_hardware()
        
        # Check if the human operator threw the master override key to force manual handling
        if cab_manual_key and not self.local_override_active:
            logging.warning("🕹️ MANUAL KEY DETECTED. Overriding automated tracking modules.")
            self.local_override_active = True
        elif not cab_manual_key and self.local_override_active:
            self.local_override_active = False

        # 2. Intercept spatial location via the polygon checker module
        spatial_data = self.route_engine.evaluate_full_spatial_matrix(current_lat, current_lon)
        active_sensor = spatial_data.get("active_sensor")
        
        # 3. Compile local fallback register bitmask based on human parameters or route logic
        fallback_mask = 0x00000000
        self.heartbeat_toggle = not self.heartbeat_toggle
        
        # Add local system heartbeat token
        if self.heartbeat_toggle:
            fallback_mask |= TeletankBits.WATCHDOG_HEARTBEAT

        # LOGIC SEPARATION GATES:
        if self.local_override_active or not self.is_bridge_connected:
            # --- LOCAL AUTONOMOUS / BACKUP MODE IS ACTIVE ---
            
            # Evaluate spatial track boundaries to enforce terminal stopping
            if active_sensor in ["VS_00_WESTLAKE_GATE", "VS_06_SEATTLE_CENTER_GATE"]:
                logging.info(f"📍 Station Boundary hit at {active_sensor}. Overriding throttle; applying service brakes.")
                fallback_mask |= TeletankBits.STOP_HOLD # Apply Westinghouse brakes
            
            elif cab_brake or gps_drift > 8.0:
                # Direct hardware trip: Human brake pull or critical chassis drift error
                logging.critical("💥 CRITICAL FAULT INGESTED: Dropping emergency safety loops.")
                fallback_mask |= TeletankBits.DROP_DEMO_BOX # Emergency dump valve drop
                
            else:
                # Map physical throttle lever steps straight to universal GE contactor registers
                if cab_throttle == 1:   fallback_mask |= TeletankBits.GEAR_1_CRAWL
                elif cab_throttle == 2: fallback_mask |= TeletankBits.GEAR_2_CRUISE
                elif cab_throttle == 3: fallback_mask |= TeletankBits.GEAR_3_FAST
                else:                   fallback_mask |= TeletankBits.STOP_HOLD
                
            # Pack and fire binary packet directly to local backup PLC hardware channels
            payload = struct.pack(">I", fallback_mask)
            try:
                self.sock.sendto(payload, (self.hardware_ip, self.hardware_port))
            except socket.error as e:
                logging.error(f"Failed to transmit data payload to local hardware port: {e}")
        else:
            # Primary bridge is connected and active; log telemetry updates quietly
            pass

if __name__ == "__main__":
    fallback_node = LocalTelemechanicalFallback()
    print("🚀 Local Telemechanical Fallback Module Configured and Active.")
    
    # Simulating a live network disconnect event during transit
    # Cycles 0-2: Bridge is alive. Cycle 3+: Bridge drops, local takeover occurs.
    for cycle in range(6):
        bridge_pulse = True if cycle < 3 else False
        fallback_node.verify_bridge_liveness(heartbeat_bit_active=bridge_pulse)
        
        # Process track execution at Denny Way straightaway coordinates
        fallback_node.execute_default_transit_cycle(
            current_lat=47.61589, 
            current_lon=-122.34142, 
            speed_mph=25, 
            gps_drift=0.5
        )
        time.sleep(0.1)
