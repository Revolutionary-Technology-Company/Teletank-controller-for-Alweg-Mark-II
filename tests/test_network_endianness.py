#!/usr/bin/env python3
import unittest
import socket
import struct
import threading
import time
from alweg_vehicle_controller import AlwegMarkIIAutomation, TeletankBits

class TestNetworkEndianness(unittest.TestCase):
    def setUp(self):
        self.test_ip = "127.0.0.1"
        self.test_port = 5005
        
        # Open a headless receiver socket on the test thread to mimic the C++ Bridge
        self.receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_sock.bind((self.test_ip, self.test_port))
        self.receiver_sock.settimeout(1.0)
        
        # Buffer to catch raw wire data
        self.received_bytes = None
        self.socket_ready = threading.Event()
        
        # Spin up background listener thread
        self.listener_thread = threading.Thread(target=self._listen_loop)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        self.socket_ready.wait() # Wait for socket to bind

    def _listen_loop(self):
        self.socket_ready.set()
        try:
            data, _ = self.receiver_sock.recvfrom(1024)
            self.received_bytes = data
        except socket.timeout:
            pass

    def tearDown(self):
        self.receiver_sock.close()
        self.listener_thread.join(timeout=1.0)

    def test_byte_order_serialization(self):
        print("\n🧪 RUNNING HEADLESS TEST: Binary Byte-Order Endianness Validation")
        
        # Initialize the actual vehicle controller core
        automation = AlwegMarkIIAutomation()
        
        # Force a distinct state: Trigger Gear 3 / Full Parallel
        # Expected Mask: 0x00000004 (or with heartbeat flag)
        automation.convert_and_transmit(current_velocity=45, chassis_roll=0.0, current_gps_drift=0.0)
        
        # Give the local loop a fraction of a second to route the UDP packet
        time.sleep(0.1)
        
        # Validate that bytes were successfully intercepted
        self.assertIsNotNone(self.received_bytes, "Failure: No network packet arrived on port 5005.")
        
        # Inspect raw wire array. Big Endian format demands the most significant byte comes first.
        # For a clean GEAR_3 flag (0x00000004), the bytes MUST read: [0x00, 0x00, 0x00, 0x04]
        # (Note: If heartbeat toggled, bit 30 will be high, but index 3 remains 0x04 or 0x44)
        raw_byte_list = list(self.received_bytes)
        print(f"  Raw Network Bytes Transmitted: {raw_byte_list}")
        
        # Explicit bitmask validation using manual native shifts to verify wire layout
        unpacked_big_endian = struct.unpack(">I", self.received_bytes)[0]
        unpacked_little_endian = struct.unpack("<I", self.received_bytes)[0]
        
        print(f"  Unpacked as Big Endian (Target PLC Layout): {hex(unpacked_big_endian)}")
        print(f"  Unpacked as Little Endian (Swapped Error):   {hex(unpacked_little_endian)}")
        
        # Verify the Gear 3 bit is residing inside the correct structural register slice
        is_gear_3_active = (unpacked_big_endian & TeletankBits.GEAR_3_FAST) != 0
        self.assertTrue(is_gear_3_active, "Failure: Endianness is swapped! The PLC register will misread the speed command.")
        print("✅ SUCCESS: Wire byte-order matches the big-endian target hardware profile exactly.")

if __name__ == "__main__":
    unittest.main()

