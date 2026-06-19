### Industrial PLC Modbus TCP Signal Map Specification

Your physical wires from the driver cab panel terminals must map directly to these 
Modbus server allocations on the train's local sub-net network:

1. Westinghouse Mechanical Air Brake Valve Handle:
   - Hardware Connection: Normally Closed (NC) physical limit switch on brake valve.
   - Modbus Data Type: Discrete Input (Read-Only Coil)
   - Modbus Modnet Address: 00001 (Offset 0)
   - Software State: 1 = Brake Handle Pulled (Trip Condition); 0 = Normal Run.

2. Master Manual Override Panel Key Switch:
   - Hardware Connection: Mechanical key selector toggle on central dash array.
   - Modbus Data Type: Discrete Input (Read-Only Coil)
   - Modbus Modnet Address: 00002 (Offset 1)
   - Software State: 1 = Enforce Manual Driver Dominance; 0 = Automated Shuttle Operations.

3. General Electric Master Controller Throttle Handle:
   - Hardware Connection: Linear cam contact or rotary encoder tracking handle steps.
   - Modbus Data Type: Input Register (Read-Only 16-Bit Word)
   - Modbus Modnet Address: 30011 (Offset 10)
   - Software State Integer Range: 
     - 0 = Neutral Coast
     - 1 = Series Crawl Speed
     - 2 = Series-Parallel Intermediate Acceleration
     - 3 = Full Parallel Express Transit Line Speed

