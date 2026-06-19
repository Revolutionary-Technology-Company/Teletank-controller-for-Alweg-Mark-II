#!/usr/bin/env python3
import json
import struct
import time
import socket
import logging
from routes.route_parser import MonorailRouteParser
from alweg_vehicle_controller import TeletankBits

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

        # Output Socket (Direct hardware map register route fallback)
        self.hardware_ip = "127.0.0.1"
        self.hardware_port = 5006 # Secondary local hardware listener port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

    def read_physical_cab_hardware(self):
        """
        Headless Hardware Abstraction Layer (HAL).
        In production, your lawyer maps these to raw PLC analog/digital input registers.
        Returns: throttle_lever (-1 to 3), brake_valve_pulled (bool), override_key (bool)
        """
        # MOCK SENSOR READS: Simulating standard human operator defaults
        throttle_lever = 2        # Physical handle position (Step 2: Series-Parallel)
        brake_valve_pulled = False # Physical Westinghouse air valve handle state
        override_key = False       # Physical manual override panel switch
        
        return throttle_lever, brake_valve_pulled, override_key

    def execute_default_transit_cycle(self, current_lat, current_lon, speed_mph, gps_drift):
        """Processes the 100ms air-gapped transit loop using native assets."""
        # 1. Gather human input telemetry and master keys from the cab consoles
        cab_throttle, cab_brake, cab_manual_key = self.read_physical_cab_hardware()
        
        # Check if the human operator threw the master override key to force manual handling
        if cab_manual_key and not self.local_override_active:
            logging.warning("🕹️ MANUAL KEY DETECTED. Overriding automated tracking modules.")
            self.local_override_active = True
        elif not cab_manual_key and self.local_override_active:
            self.local_override_active = False

        # 2. Intercept spatial location via the polygon checker module
        active_sensor, _ = self.route_engine.evaluate_full_spatial_matrix(current_lat, current_lon)
        
        # 3. Compile local fallback register bitmask based on human parameters or route logic
        fallback_mask = 0x00000000
        self.heartbeat_toggle = not self.heartbeat_toggle
        
        # Add local system heartbeat token
        if self.heartbeat_toggle:
            fallback_mask |= TeletankBits.WATCHDOG_HEARTBEAT

        # LOGIC SEPARATION GATES:
        if self.local_override_active or not self.is_bridge_connected:
            # --- LOCAL AUTONOMOUS MODE IS ACTIVE ---
            
            # Evaluate spatial track boundaries to enforce terminal stopping
            if active_sensor in ["VS_00_WESTLAKE_GATE", "VS_06_SEATTLE_CENTER_GATE"]:
                logging.info(f"📍 Station Boundary hit at {active_sensor}. Overriding throttle; applying service brakes.")
                fallback_mask |= TeletankBits.STOP_HOLD # Apply Westinghouse brakes
            
            elif cab_brake or gps_drift > 8.0:
                # Direct hardware trip: Human brake pull or critical chassis drift error
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
            except socket.error:
                pass
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

