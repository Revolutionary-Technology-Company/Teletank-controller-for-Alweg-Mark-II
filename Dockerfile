# =======================================================================
# REVOLUTIONARY TECHNOLOGY COMPANY - ENTERPRISE AUTOMATION CORE
# Target Platform: WAGO PFC / openPLC / Embedded Industrial Linux
# Subsystem: Multimedia Pass-Through & Hardware Mapping
# =======================================================================

# Use a hardened Linux base image for industrial runtime stability
FROM python:3.11-slim-bookworm

# Establish strict non-interactive frontend variables for headless installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies, utilities, and hardware audio drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    g++ \
    kmod \
    pciutils \
    libgomp1 \
    alsa-utils \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the standard Modbus TCP protocol master package via pip
RUN pip install --no-cache-dir pyModbusTCP==0.2.1

# Set up the enterprise directories inside the controller workspace
WORKDIR /opt/revolutionary_technology

# Copy configuration boundaries and core scripts directly into application space
COPY config.json .
COPY alweg_vehicle_controller.py .
COPY test_telemetry_injector.py .
COPY routes/ ./routes/
COPY subsystems/ ./subsystems/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Inform the hardware platform that our communication pipelines use these designated ports
EXPOSE 5005 8081 502

# HARDWARE DEPLOYMENT ROUTINE GENERATOR:
# Probes host system modules, maps Fibre Channel, validates network integrity, 
# and runs parallel fallback daemons before launching the main vehicle logic.
RUN echo '#!/bin/bash\n\
echo "⚙️ Initializing low-level industrial hardware drivers..."\n\
modprobe qla2xxx 2>/dev/null || echo "⚠️ Host driver mismatch; relying on pass-through PCI mapping."\n\
\n\
echo "📊 Executing Automated Fibre Channel Network Integrity Diagnostics..."\n\
python3 -m unittest tests/test_fibre_channel_integrity.py\n\
\n\
if [ $? -eq 0 ]; then\n\
    echo "✅ DIAGNOSTICS PASSED: Hardware backbone stable. Booting Multi-Generational Automation Stack..."\n\
    \n\
    # Spin up the local telemechanical fallback loop concurrently on a background core\n\
    python3 subsystems/local_telemechanical_fallback.py &\n\
    \n\
    # Execute the primary train vehicle controller as the main container thread\n\
    exec python3 alweg_vehicle_controller.py\n\
else\n\
    echo "💥 CRITICAL DIAGNOSTIC ERROR: Fibre Channel degradation detected. Automation inhibited for safety."\n\
    exit 1\n\
fi\n\
' > /opt/revolutionary_technology/entrypoint.sh && chmod +x /opt/revolutionary_technology/entrypoint.sh

# Run system verification suites automatically during image validation phases
RUN python3 -m unittest tests/test_network_endianness.py && \
    python3 -m unittest tests/test_monorail_safety.py && \
    chmod +x ./scripts/cleanup_test_env.sh && ./scripts/cleanup_test_env.sh

# Set the operational entrypoint script
ENTRYPOINT ["/opt/revolutionary_technology/entrypoint.sh"]
