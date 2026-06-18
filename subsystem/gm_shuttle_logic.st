(* =======================================================================
   GM INTERLOCK SHUTTLE SEQUENCING MACHINE
   ======================================================================= *)
CASE iShuttleState OF
    0: (* Train Docked at Terminal Platform *)
       out_bPropulsion_Enable := FALSE;
       out_bStation_Doors_Open := TRUE;
       
       // Move to transit once platform countdown wraps and turnstiles clear
       IF bPlatform_Clearance_Signaled THEN
           out_bStation_Doors_Open := FALSE;
           iShuttleState := 1; (* Transition to Departure *)
       END_IF;

    1: (* Mid-Line Kinematic Transit *)
       out_bPropulsion_Enable := TRUE;
       
       // Handle curve speed clamping via virtual sensor intersections
       IF bVirtual_Sensor_Stewart_Active OR bVirtual_Sensor_MoPOP_Active THEN
           out_bGE_Motors_High_Speed := FALSE;
           out_bGE_Motors_Low_Speed  := TRUE; (* Drop to Series mode *)
       ELSE
           out_bGE_Motors_High_Speed := TRUE;  (* High speed parallel mode *)
       END_IF;

       // Approach terminal docking checkpoint
       IF bVirtual_Sensor_Terminal_Approach_Active THEN
           iShuttleState := 2; (* Transition to Braking Approach *)
       END_IF;

    2: (* Coordinated Docking Brake Loop *)
       out_bGE_Motors_High_Speed := FALSE;
       out_bGE_Motors_Low_Speed  := FALSE;
       out_bDynamic_Braking_Active := TRUE; (* Reverse motor polarization *)
       
       IF bTrain_Velocity_Zero THEN
           iShuttleState := 0; (* Reset back to platform docking state *)
       END_IF;
END_CASE;
