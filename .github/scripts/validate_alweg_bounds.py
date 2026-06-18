import json
import os
import sys

def validate_config():
    config_path = "config.json"
    
    if not os.path.exists(config_path):
        print(f"❌ CRITICAL ERROR: {config_path} missing from repository root.")
        sys.exit(1)
        
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ SYNTAX ERROR: config.json is not valid JSON. Details: {e}")
        sys.exit(1)

    print("Checking enterprise Alweg kinematic boundaries...")
    errors = 0

    # 1. Structural Limits Verification
    limits = data.get("kinematic_safety_limits", {})
    watchdog = limits.get("high_speed_watchdog_ms", {})
    max_latency = watchdog.get("max_latency_allowed", 999.0)
    
    if max_latency > 100.0:
        print(f"❌ SAFETY VIOLATION: Watchdog latency limit ({max_latency}ms) exceeds the critical 100ms maximum threshold.")
        errors += 1
        
    spatial = limits.get("samsara_dual_gateway_sync", {})
    max_drift = spatial.get("max_spatial_drift_feet", 0.0)
    if max_drift > 10.0 or max_drift < 2.0:
        print(f"❌ STRUCTURAL VIOLATION: Spatial gateway drift tolerance ({max_drift}ft) is out of bounds for a rigid 122ft chassis.")
        errors += 1

    # 2. Braking Matrix Verification
    braking = data.get("pneumatic_braking_mapping", {})
    psi_range = braking.get("service_brake_range_psi", {})
    min_psi = psi_range.get("min_application", 0.0)
    max_psi = psi_range.get("full_application", 0.0)
    
    if min_psi > 90.0 or max_psi < 50.0:
        print(f"❌ PNEUMATIC ERROR: Westinghouse brake pipe pressure range ({min_psi} -> {max_psi} PSI) violates physical hardware limits.")
        errors += 1

    # 3. Final Evaluation
    if errors > 0:
        print(f"💥 VALIDATION FAILED: {errors} critical safety violations detected. Pull request rejected.")
        sys.exit(1)
        
    print("🚀 SUCCESS: config.json passed all deterministic safety constraints.")
    sys.exit(0)

if __name__ == "__main__":
    validate_config()

