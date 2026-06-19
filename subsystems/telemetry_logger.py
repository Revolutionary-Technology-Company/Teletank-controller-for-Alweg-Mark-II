#!/usr/bin/env python3
import sys
import time
import os

class HeadlessTelemetryLogger:
    """
    Headless terminal logger wrapping raw environmental variables 
    into visual ASCII blocks for embedded openPLC consoles.
    """
    def __init__(self):
        # Color palettes for headless ANSI scannability
        self.CLR_CYAN = '\033[96m'
        self.CLR_GREEN = '\033[92m'
        self.CLR_YELLOW = '\033[93m'
        self.CLR_RED = '\033[91m'
        self.CLR_RESET = '\033[0m'
        self.CLR_BOLD = '\033[1m'
        
        # Peak value memories
        self.peak_shock_g = 0.0
        self.max_temp_c = 0.0

    def stream_metrics_to_terminal(self, sensor_id, speed, temp, humidity, pressure, shock_g):
        """
        Wipes the terminal buffer and outputs a clean, structured visual grid
        to log uncrewed shuttle health frames continuously.
        """
        # Maintain peak-hold metrics across the simulation runtime
        if shock_g > self.peak_shock_g:
            self.peak_shock_g = shock_g
        if temp > self.max_temp_c:
            self.max_temp_c = temp

        # Generate structural alarm tags based on enterprise thresholds
        shock_status = f"{self.CLR_RED}[!! ALARM !!]{self.CLR_RESET}" if shock_g >= 4.5 else f"{self.CLR_GREEN}[NOMINAL]{self.CLR_RESET}"
        temp_status  = f"{self.CLR_RED}[OVERHEAT]{self.CLR_RESET}" if temp >= 60.0 else f"{self.CLR_GREEN}[NOMINAL]{self.CLR_RESET}"

        # Clean screen ANSI sequence (keeps terminal fixed in place without flickering)
        sys.stdout.write("\033[H\033[J")
        
        output_buffer = (
            f"╔══════════════════════════════════════════════════════════════════════════╗\n"
            f"║ {self.CLR_BOLD}{self.CLR_CYAN}REVOLUTIONARY TECHNOLOGY CO. - HEADLESS ROVER TELEMETRY BUS{self.CLR_RESET}              ║\n"
            f"╠══════════════════════════════════════════════════════════════════════════╣\n"
            f"║  TRACK ENVIRONMENT DATA                                                  ║\n"
            f"║  ─────────────────────                                                  ║\n"
            f"║  • Current Waypoint Checkpoint : {self.CLR_BOLD}{sensor_id:<32}{self.CLR_RESET}        ║\n"
            f"║  • Active Line Speed Velocity  : {self.CLR_GREEN}{speed:<3} mph{self.CLR_RESET}                                      ║\n"
            f"╠══════════════════════════════════════════════════════════════════════════╣\n"
            f"║  TELETANK ENVIRONMENTAL MATRIX                                           ║\n"
            f"║  ─────────────────────────────                                           ║\n"
            f"║  • Mechanical Shock Vector     : {self.CLR_BOLD}{shock_g:<5.2f} G{self.CLR_RESET}   {shock_status:<22}               ║\n"
            f"║  • Core Temp Sensor Output     : {self.CLR_BOLD}{temp:<5.1f} °C{self.CLR_RESET}  {temp_status:<22}               ║\n"
            f"║  • Relative Humidity Index     : {humidity:<5.1f} %   [ATMOSPHERE MONITOR]               ║\n"
            f"║  • Barometric Air Pressure    : {pressure:<6.1f} hPa [ELEVATION BARO]                 ║\n"
            f"╠══════════════════════════════════════════════════════════════════════════╣\n"
            f"║  PEAK-HOLD MISSION MEMORY RECORDS                                        ║\n"
            f"║  ────────────────────────────────                                        ║\n"
            f"║  • Max Shock Spike Encountered : {self.CLR_YELLOW}{self.peak_shock_g:<5.2f} G{self.CLR_RESET}                                      ║\n"
            f"║  • Maximum Registered Temp     : {self.CLR_YELLOW}{self.max_temp_c:<5.1f} °C{self.CLR_RESET}                                     ║\n"
            f"╚══════════════════════════════════════════════════════════════════════════╝\n"
        )
        
        sys.stdout.write(output_buffer)
        sys.stdout.flush()

if __name__ == "__main__":
    # Internal component debugging check
    logger = HeadlessTelemetryLogger()
    logger.stream_metrics_to_terminal(
        sensor_id="VS_03_DENNY_STRAIGHTAWAY",
        speed=45,
        temp=24.5,
        humidity=62.1,
        pressure=1012.4,
        shock_g=0.12
    )

