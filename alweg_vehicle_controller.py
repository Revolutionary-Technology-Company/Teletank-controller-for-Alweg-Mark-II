import json
import socket
import struct
import time
import math

# Universal Low-Level Teletank Bitmasks matching your C++ Univac core
class TeletankBits:
    GEAR_1_CRAWL       = 0x00000001 # Maps to Alweg GE Resistor Step 1 (Series)
    GEAR_2_CRUISE      = 0x00000002 # Maps to Alweg GE Resistor Step 2 (Series-Parallel)
    GEAR_3_FAST        = 0x00000004 # Maps to Alweg GE Resistor Step 3 (Full Parallel)
    STOP_HOLD          = 0x00000100 # Maps to Westinghouse service brakes application
    VALVE_LEFT_MASK    = 0x00020000 # Actuate Left Tele-Tank fluid pump
    VALVE_RIGHT_MASK   = 0x00040000 # Actuate Right Tele-Tank fluid pump
    WATCHDOG_HEARTBEAT = 0x40000000 # Multi-generational 100ms safety ping
    DROP_DEMO_BOX      = 0x00100000 # Emergency Trip (Dump Westinghouse Brake Pipe)

class AlwegMarkIIAutomation:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        # Target loop connectivity parameters
        self.bridge_ip = "127.0.0.1"
        self.bridge_port = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # High-speed UDP link
        
        # Local tracking variables
        self.heartbeat_toggle = False

    def convert_and_transmit(self, current_velocity, chassis_roll, current_gps_drift):
        command_mask = 0x00000000
        self.heartbeat_toggle = not self.heartbeat_toggle
        
        # 1. Map Velocity straight to the Universal Teletank Gear Steps
        if current_velocity == 0:
            command_mask |= TeletankBits.STOP_HOLD
        elif current_velocity <= 15:
            command_mask |= TeletankBits.GEAR_1_CRAWL
        elif current_velocity <= 30:
            command_mask |= TeletankBits.GEAR_2_CRUISE
        else:
            command_mask |= TeletankBits.GEAR_3_FAST

        # 2. Map Chrysler Gyro Analog Roll Volts directly to Telemechanical Gas Solenoids
        if chassis_roll > 3.0:
            command_mask |= TeletankBits.VALVE_LEFT_MASK # Counter-balance the lean
        elif chassis_roll < -3.0:
            command_mask |= TeletankBits.VALVE_RIGHT_MASK

        # 3. Handle Samsara Structural Integrity Metrics
        max_drift = self.config["kinematic_safety_limits"]["samsara_dual_gateway_sync"]["max_spatial_drift_feet"]
        if current_gps_drift > max_drift:
            # Spatial uncoupling detected: Trigger universal Saaper "Bomb Drop" / Emergency Stop
            command_mask |= TeletankBits.DROP_DEMO_BOX

        # 4. Inject Watchdog Token
        if self.heartbeat_toggle:
            command_mask |= TeletankBits.WATCHDOG_HEARTBEAT

        # 5. Pack into raw C-struct format (Big-Endian 32-bit unsigned int)
        payload = struct.pack(">I", command_mask)
        
        # 6. Fire packet over network loop to the Univac Bridge Server
        self.sock.sendto(payload, (self.bridge_ip, self.bridge_port))

if __name__ == "__main__":
    controller = AlwegMarkIIAutomation()
    print("🚀 Alweg Monorail Teletank Format Converter Core Operational.")
    
    # Simulating continuous 100ms hardware processing cycles
    while True:
        # Example variables gathered from physical sensors and Samsara telemetry hooks
        controller.convert_and_transmit(current_velocity=25, chassis_roll=4.2, current_gps_drift=1.5)
        time.sleep(0.1)
