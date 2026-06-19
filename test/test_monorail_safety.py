import unittest
import struct
from alweg_vehicle_controller import AlwegMarkIIAutomation, TeletankBits

class TestMonorailSafetyLogic(unittest.TestCase):
    def setUp(self):
        # Instantiate your converter module using the repository config.json
        self.automation = AlwegMarkIIAutomation()
        
        # Override the socket connection with a mock to run completely headless
        class MockSocket:
            def __init__(self): self.last_payload = None
            def sendto(self, payload, address): self.last_payload = payload
            
        self.automation.sock = MockSocket()

    def test_samsara_gps_urban_canyon_fault(self):
        print("\n🧪 RUNNING HEADLESS TEST: Samsara Urban Canyon GPS Fault Interception")
        
        # 1. Execute a run with severe GPS spatial drift (e.g., 9.5 feet, exceeding config bounds)
        self.automation.convert_and_transmit(current_velocity=30, chassis_roll=0.0, current_gps_drift=9.5)
        
        # 2. Unpack the transmitted binary payload sent to port 5005
        sent_bytes = self.automation.sock.last_payload
        unpacked_mask = struct.unpack(">I", sent_bytes)[0]
        
        print(f"  Received Bitmask Payload: {bin(unpacked_mask)}")
        
        # 3. Assert that the software correctly applied the DROP_DEMO_BOX emergency stop bit
        # checking that the safety dump bit is active
        has_emergency_tripped = (unpacked_mask & TeletankBits.DROP_DEMO_BOX) != 0
        print(f"  Emergency Trip Bit Active? {has_emergency_tripped}")
        
        self.assertTrue(has_emergency_tripped, "Failure: Software failed to trip the brake valve mask during a high GPS drift event!")
        print("✅ SUCCESS: Software safety interlock dropped the binary loop flawlessly.")

if __name__ == "__main__":
    unittest.main()
