(* =======================================================================
   REVOLUTIONARY TECHNOLOGY COMPANY - TELETANK HARDWARE COIL REGISTERS
   Target System: Alweg Mark II Integration Profile via Univac-Aegis Bridge
   ======================================================================= *)

PROGRAM Teletank_Hardware_Actuation
VAR
    // Input bitmask received from the Python conversion socket (Port 5005)
    dwTeletankBitmask : DWORD; 
    
    // Physical Output Terminal Mappings (To be wired by the Hardware Engineer)
    out_bGE_Step1_Series           AT %QX0.0 : BOOL; // 1961 GE Contactor 1
    out_bGE_Step2_SeriesParallel   AT %QX0.1 : BOOL; // 1961 GE Contactor 2
    out_bGE_Step3_FullParallel     AT %QX0.2 : BOOL; // 1961 GE Contactor 3
    out_bWestinghouse_Brake_Hold   AT %QX0.3 : BOOL; // Friction Air Brake Valve
    out_bTeleTank_Pump_Left        AT %QX0.4 : BOOL; // Left Ballast HPU
    out_bTeleTank_Pump_Right       AT %QX0.5 : BOOL; // Right Ballast HPU
    out_bWestinghouse_Triple_Dump  AT %QX0.6 : BOOL; // Emergency Vent Solenoid
END_VAR

// --- HARDWARE ACTUATION PARSING LOOP ---

// Propulsion Mapping (Bits 0, 1, 2)
out_bGE_Step1_Series         := (dwTeletankBitmask AND 16#00000001) <> 0;
out_bGE_Step2_SeriesParallel := (dwTeletankBitmask AND 16#00000002) <> 0;
out_bGE_Step3_FullParallel   := (dwTeletankBitmask AND 16#00000004) <> 0;

// Braking Matrix Mapping (Bit 8)
out_bWestinghouse_Brake_Hold := (dwTeletankBitmask AND 16#00000100) <> 0;

// Active Ballast Tele-Tank Mapping (Bits 17, 18)
out_bTeleTank_Pump_Left      := (dwTeletankBitmask AND 16#00020000) <> 0;
out_bTeleTank_Pump_Right     := (dwTeletankBitmask AND 16#00040000) <> 0;

// High-Speed Safety Interlock / Urban Canyon Glitch Drop (Bit 20)
// Normally closed fail-safe logic: If true, keep the dump valve powered (safe).
// If bit is tripped, force a drop to 0, instantly venting the brake pipe.
IF (dwTeletankBitmask AND 16#00100000) <> 0 THEN
    out_bWestinghouse_Triple_Dump := FALSE; // Drop power to vent air
ELSE
    out_bWestinghouse_Triple_Dump := TRUE;  // Keep powered (normal operation)
END_IF

END_PROGRAM

