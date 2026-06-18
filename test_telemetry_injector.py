#!/usr/bin/env python3
import time
import sys
from alweg_vehicle_controller import AlwegMarkIIAutomation

def run_headless_simulation():
    print("------------------------------------------------------------")
    print("⚡ HEADLESS SIMULATION INITIALIZED: Alweg Mark II Teletank Core")
    print("------------------------------------------------------------")
    
    try:
        # Initialize the converter from our train repo config.json
        controller = AlwegMarkIIAutomation()
    except Exception as e:
        print(f"❌ Initialization Failed: Could not read config.json. Error: {e}")
        sys.exit(1)

    # Simulation timeline modeling track points from Westlake to Seattle Center
    timeline = [
        {"desc": "Station Docked: Westlake Terminal", "velocity": 0,  "roll": 0.0,  "drift": 0.5, "dur": 3},
        {"desc": "Departing Station: Accelerating",    "velocity": 12, "roll": 1.1,  "drift": 0.8, "dur": 3},
        {"desc": "WP-01: Intercepting S-Curve Bends", "velocity": 14, "roll": 5.4,  "drift": 1.1, "dur": 5},
        {"desc": "WP-02: 5th Ave Straightaway Max",   "velocity": 45, "roll": -0.2, "drift": 1.2, "dur": 6},
        {"desc": "High Wind Shear Event Detected",     "velocity": 38, "roll": -4.8, "drift": 1.4, "dur": 4},
        {"desc": "Samsara GPS Urban Canyon Glitch",   "velocity": 30, "roll": 0.0,  "drift": 9.5, "dur": 2}, # Should trigger emergency stop
        {"desc": "Approaching WP-03: Seattle Center",  "velocity": 10, "roll": 0.5,  "drift": 0.6, "dur": 4}
    ]

    for step in timeline:
        print(f"\n▶️ Current Stage: {step['desc']}")
        print(f"  [Sensors] Speed: {step['velocity']}mph | Roll: {step['roll']}° | GPS Spatial Drift: {step['drift']}ft")
        
        # Loop for the duration of this specific track event at 100ms intervals
        cycles = int(step['dur'] * 10)
        for _ in range(cycles):
            controller.convert_and_transmit(
                current_velocity=step['velocity'],
                chassis_roll=step['roll'],
                current_gps_drift=step['drift']
            )
            time.sleep(0.1)
            
    print("\n🏁 Headless track profile simulation complete.")

if __name__ == "__main__":
    run_headless_simulation()
