# Use a hardened Linux runtime container designed for embedded industrial systems
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install low-level network utility tools and loop builders
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    g++ \
    kmod \
    pciutils \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/revolutionary_technology

# Copy configuration and tracking binaries directly into app space
COPY config.json .
COPY alweg_vehicle_controller.py .
COPY routes/ ./routes/
COPY subsystems/ ./subsystems/
COPY scripts/ ./scripts/

EXPOSE 5005 8081

# HARDWARE DEPLOYMENT ROUTINE:
# To allow the container to interface with the physical GE Fibre Channel hardware,
# your lawyer must run this container using the --privileged flag.
# This script ensures the kernel modules are initialized before launching the train application.
RUN echo '#!/bin/bash\n\
echo "⚙️ Initializing low-level industrial hardware drivers..."\n\
# Probe host system for Fibre Channel card nodes (e.g., fc_transport/scsi)\n\
modprobe qla2xxx 2>/dev/null || echo "⚠️ Host driver mismatch; relying on pass-through PCI mapping."\n\
\n\
echo "🚀 Booting Alweg Monorail Automation Application..."\n\
exec python3 alweg_vehicle_controller.py\n\
' > /opt/revolutionary_technology/entrypoint.sh && chmod +x /opt/revolutionary_technology/entrypoint.sh

ENTRYPOINT ["/opt/revolutionary_technology/entrypoint.sh"]

# Use a lightweight, hardened Linux base image for industrial runtime stability
FROM python:3.11-slim-bookworm

# Establish strict non-interactive frontend variables for headless installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies required for compiling network components
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set up the enterprise directories inside the controller workspace
WORKDIR /opt/revolutionary_technology

# Copy the configuration boundaries profile directly into the application space
COPY config.json .
COPY alweg_vehicle_controller.py .
COPY test_telemetry_injector.py .

# Inform the hardware platform that our UDP communication pipeline uses port 5005
EXPOSE 5005

# Execute the simulation harness inside the headless container by default
CMD ["python3", "test_telemetry_injector.py"]
# Run the Endianness test, then the Urban test, and fire the cleanup script automatically
CMD python3 -m unittest tests/test_network_endianness.py && \
    python3 -m unittest tests/test_monorail_safety.py && \
    chmod +x ./scripts/cleanup_test_env.sh && ./scripts/cleanup_test_env.sh

