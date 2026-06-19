To get our completely automated system running on the train's edge PLC without any graphical interfaces, we will implement Step 1: The Python Mock Telemetry Injector and Core Testing Script, followed by Step 2: The systemd Initialization Service Files to handle automatic booting and recovery.
Everything here will be strictly command-line based, relying on raw sockets, JSON reading, and headless Linux system services.
## Step 1: Create the systemd Service Files (Onboard Edge PLC)
To ensure this software runs reliably like a piece of true transit infrastructure, we must configure Linux systemd services to daemonize both parts of the architecture. If a service crashes or the train experiences a brief power fluctuation, the OS will automatically reload the automation pipeline in under a second.
## A. The Universal Bridge Server Daemon
Create this file on your PLC target at /etc/systemd/system/univac-bridge.service:

[Unit]
Description=Univac-Aegis Universal Teletank Bridge Server
After=network.target
Documentation=https://github.com

[Service]
Type=simple
WorkingDirectory=/opt/univac_aegis_bridge
ExecStart=/opt/univac_aegis_bridge/build/univac_aegis_bridge_node
Restart=always
RestartSec=1s

# Performance Tuning: Prioritize execution to guarantee the 100ms watchdog path
CPUSchedulingPolicy=rr
CPUSchedulingPriority=99
Nice=-20

[Install]
WantedBy=multi-user.target

## B. The Alweg Converter Daemon
Create this file on your PLC target at /etc/systemd/system/alweg-controller.service:

[Unit]
Description=Alweg Monorail Teletank Format Converter Core
After=univac-bridge.service
Requires=univac-bridge.service
Documentation=https://github.com

[Service]
Type=simple
WorkingDirectory=/opt/alweg_teletank_controller
ExecStart=/usr/bin/python3 /opt/alweg_teletank_controller/alweg_vehicle_controller.py
Restart=always
RestartSec=1s

# Force unbuffered output so we can monitor telemetry via system logs
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target

------------------------------
## Step 2: Headless Execution & Deployment Verification
To activate your multi-generational automation environment on the train's edge PLC cabinet, SSH directly into the target machine and execute the following configuration commands:

# 1. Reload the systemd manager configuration to discover the new services
sudo systemctl daemon-reload
# 2. Enable the services so they boot automatically on hardware power-up
sudo systemctl enable univac-bridge.service
sudo systemctl enable alweg-controller.service
# 3. Start the execution pipeline right now
sudo systemctl start univac-bridge.service
sudo systemctl start alweg-controller.service

## How to Verify the Control Pipeline Headless:
Because we completely avoided GUIs, you will monitor the telemetry processing, bit-packing, and network sockets live by attaching directly to the Linux logging journal:

# Monitor the live conversion logs, lookups, and errors via journalctl
sudo journalctl -u alweg-controller.service -f

------------------------------
## How to Proceed
With the headless simulation engine and automatic service daemons locked in, let me know:

* Do you want to check how the system handles the Samsara GPS Urban Canyon Glitch simulation phase, and trace how the bitmask forces the DROP_DEMO_BOX trigger?
* Should we write a network socket listener tool (using tcpdump or raw python) to verify the binary structs are landing on port 5005 with the correct byte-order formatting?


