#!/bin/bash
#
# Run script for Prometheus component in Tekton
#

# Determine the Tekton root directory (parent of this component)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEKTON_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Source common utilities
source "${TEKTON_ROOT}/scripts/lib/tekton-utils.sh" || { echo "Failed to source common utilities"; exit 1; }
source "${TEKTON_ROOT}/scripts/lib/tekton-config.sh" || { echo "Failed to source config utilities"; exit 1; }
source "${TEKTON_ROOT}/scripts/lib/tekton-ports.sh" || { echo "Failed to source port utilities"; exit 1; }
source "${TEKTON_ROOT}/scripts/lib/tekton-process.sh" || { echo "Failed to source process utilities"; exit 1; }

# Load component configuration
PROMETHEUS_CONFIG="${TEKTON_ROOT}/config/components/prometheus.yaml"

# Set up environment variables
PROMETHEUS_PORT=$(get_port "prometheus" 8005)
export PROMETHEUS_PORT

# Check if Prometheus is already running
if check_port_in_use $PROMETHEUS_PORT; then
    echo "Prometheus is already running on port $PROMETHEUS_PORT"
    exit 0
fi

echo "Starting Prometheus on port $PROMETHEUS_PORT..."

# Run the Prometheus API server
cd "${SCRIPT_DIR}" || { echo "Failed to change to Prometheus directory"; exit 1; }

# Create a virtual environment if it doesn't exist
VENV_DIR="venv"
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "${VENV_DIR}" || { echo "Failed to create virtual environment"; exit 1; }
    source "${VENV_DIR}/bin/activate" || { echo "Failed to activate virtual environment"; exit 1; }
    pip install -e . || { echo "Failed to install Prometheus"; exit 1; }
    pip install -e "${TEKTON_ROOT}/tekton-llm-client" || { echo "Failed to install tekton-llm-client"; exit 1; }
else
    source "${VENV_DIR}/bin/activate" || { echo "Failed to activate virtual environment"; exit 1; }
fi

# Run the server
python -m prometheus.api.app --port $PROMETHEUS_PORT &
PROMETHEUS_PID=$!
echo "Prometheus running with PID $PROMETHEUS_PID"

# Register with Hermes using tekton-register
${TEKTON_ROOT}/scripts/tekton-register register --component prometheus --config ${PROMETHEUS_CONFIG} &
REGISTER_PID=$!

# Trap signals for graceful shutdown
trap "${TEKTON_ROOT}/scripts/tekton-register unregister --component prometheus; kill $PROMETHEUS_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Wait for the server to start
wait_for_port $PROMETHEUS_PORT 30 || { 
    echo "Failed to start Prometheus within timeout"; 
    kill $PROMETHEUS_PID 2>/dev/null;
    ${TEKTON_ROOT}/scripts/tekton-register unregister --component prometheus;
    exit 1; 
}

echo "Prometheus is running at http://localhost:$PROMETHEUS_PORT"

# Keep the script running until interrupted
wait $PROMETHEUS_PID