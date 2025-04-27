#!/usr/bin/env python3
"""
Register Prometheus/Epimethius with Hermes Service Registry

This script registers the Prometheus/Epimethius planning system with the Hermes service registry,
allowing other components to discover and use its capabilities.

Usage:
    python register_with_hermes.py [options]

Environment Variables:
    HERMES_URL: URL of the Hermes API (default: http://localhost:8001/api)
    PROMETHEUS_PORT: Port for the Prometheus API (default: 8006)
    STARTUP_INSTRUCTIONS_FILE: Path to JSON file with startup instructions

Options:
    --hermes-url: URL of the Hermes API (overrides HERMES_URL env var)
    --instructions-file: Path to startup instructions JSON file
    --port: Port for the Prometheus API (overrides PROMETHEUS_PORT env var)
    --help: Show this help message
"""

import os
import sys
import asyncio
import signal
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prometheus.registration")

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()

# Add parent directories to path
component_dir = str(script_dir)
tekton_dir = os.path.abspath(os.path.join(component_dir, ".."))
tekton_core_dir = os.path.join(tekton_dir, "tekton-core")

# Add to Python path
sys.path.insert(0, component_dir)
sys.path.insert(0, tekton_dir)
sys.path.insert(0, tekton_core_dir)

# Check if we're in a virtual environment
in_venv = sys.prefix != sys.base_prefix
if not in_venv:
    venv_dir = os.path.join(component_dir, "venv")
    if os.path.exists(venv_dir):
        logger.warning(f"Not running in the Prometheus virtual environment.")
        logger.warning(f"Consider activating it with: source {venv_dir}/bin/activate")

# Import registration utilities
try:
    # Try to import from tekton-core first (preferred)
    from tekton.utils.hermes_registration import (
        HermesRegistrationClient,
        register_component,
        load_startup_instructions
    )
    REGISTRATION_UTILS_AVAILABLE = True
    logger.info("Successfully imported Tekton registration utilities")
except ImportError:
    logger.warning("Could not import Tekton registration utilities.")
    logger.warning("Falling back to direct Hermes client import.")
    REGISTRATION_UTILS_AVAILABLE = False

    # Try to import from Hermes directly
    try:
        hermes_dir = os.environ.get("HERMES_DIR")
        if not hermes_dir or not os.path.exists(hermes_dir):
            potential_hermes_dir = os.path.normpath(os.path.join(script_dir, "../Hermes"))
            if os.path.exists(potential_hermes_dir):
                hermes_dir = potential_hermes_dir
                sys.path.insert(0, hermes_dir)
                
        # Import from hermes directly
        from hermes.core.service_discovery import ServiceRegistry
        logger.info(f"Successfully imported Hermes modules from {hermes_dir}")
    except ImportError as e:
        logger.error(f"Error importing Hermes modules: {e}")
        logger.error(f"Make sure Hermes is properly installed and accessible")
        sys.exit(1)

# Import Prometheus/Epimethius specific modules
try:
    from prometheus.core.planning_engine import PlanningEngine
    from prometheus.utils.hermes_helper import (
        register_with_hermes,
        prometheus_capabilities,
        epimethius_capabilities
    )
    logger.info("Successfully imported Prometheus/Epimethius modules")
except ImportError as e:
    logger.error(f"Error importing Prometheus/Epimethius modules: {e}")
    logger.error(f"Make sure Prometheus/Epimethius is properly installed and accessible")
    sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Register Prometheus/Epimethius with Hermes Service Registry"
    )
    parser.add_argument(
        "--hermes-url",
        help="URL of the Hermes API",
        default=os.environ.get("HERMES_URL", "http://localhost:8001/api")
    )
    parser.add_argument(
        "--instructions-file",
        help="Path to startup instructions JSON file",
        default=os.environ.get("STARTUP_INSTRUCTIONS_FILE")
    )
    parser.add_argument(
        "--port",
        help="Port for the Prometheus API",
        default=os.environ.get("PROMETHEUS_PORT", "8006")
    )
    
    return parser.parse_args()


async def register_prometheus_epimethius(
    hermes_url: Optional[str] = None,
    instructions_file: Optional[str] = None,
    port: Optional[str] = None
) -> bool:
    """
    Register Prometheus/Epimethius with Hermes service registry.
    
    Args:
        hermes_url: URL of the Hermes API
        instructions_file: Path to JSON file with startup instructions
        port: Port for the Prometheus API
        
    Returns:
        True if registration was successful
    """
    # Check for startup instructions file
    if instructions_file and os.path.isfile(instructions_file):
        logger.info(f"Loading startup instructions from {instructions_file}")
        instructions = load_startup_instructions(instructions_file)
        # Extract relevant information from instructions
    else:
        instructions = {}
    
    # Define component information
    component_id = instructions.get("component_id", "prometheus.planning")
    component_name = instructions.get("name", "Prometheus/Epimethius Planning System")
    component_type = instructions.get("type", "planning_system")
    
    # Define capabilities
    prometheus_caps = await prometheus_capabilities()
    epimethius_caps = await epimethius_capabilities()
    capabilities = prometheus_caps + epimethius_caps
    
    # Define dependencies
    dependencies = instructions.get("dependencies", [
        "telos.requirements",
        "rhetor-prompt",
        "engram.memory"
    ])
    
    # If port is not provided, use a default or from instructions
    if not port:
        port = instructions.get("port", "8006")
    
    # Define endpoint
    endpoint = f"http://localhost:{port}/api"
    
    # Define additional metadata
    metadata = {
        "description": "Planning, retrospective analysis, and improvement for Tekton",
        "ui_available": True,
        "cli_available": True,
        "telos_integration": True,
        "rhetor_integration": True,
        "engram_integration": True,
        "single_port_architecture": True,
        "port": port
    }
    if instructions.get("metadata"):
        metadata.update(instructions["metadata"])
    
    try:
        # Initialize the planning engine
        engine = PlanningEngine()
        await engine.initialize()
        
        # Register the component
        client = None
        if REGISTRATION_UTILS_AVAILABLE:
            client = await register_component(
                component_id=component_id,
                component_name=component_name,
                component_type=component_type,
                component_version="0.1.0",
                capabilities=capabilities,
                hermes_url=hermes_url,
                dependencies=dependencies,
                endpoint=endpoint,
                additional_metadata=metadata
            )
            
            if client:
                logger.info(f"Successfully registered {component_name} with Hermes")
                
                # Set up signal handlers
                loop = asyncio.get_event_loop()
                
                stop_event = asyncio.Event()
                
                def handle_signal(sig):
                    logger.info(f"Received signal {sig.name}, shutting down")
                    asyncio.create_task(shutdown(client, engine, stop_event))
                
                for sig in (signal.SIGINT, signal.SIGTERM):
                    loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
                
                logger.info("Registration active. Press Ctrl+C to unregister and exit...")
                try:
                    await stop_event.wait()
                except Exception as e:
                    logger.error(f"Error during registration: {e}")
                    await shutdown(client, engine, stop_event)
                
                return True
            else:
                logger.error(f"Failed to register {component_name} with Hermes")
                await engine.close()
                return False
        else:
            # Use the helper function
            success = await register_with_hermes(
                component_id=component_id,
                component_name=component_name,
                component_type=component_type,
                capabilities=capabilities,
                endpoint=endpoint,
                description=f"Prometheus/Epimethius Planning System for Tekton",
                dependencies=dependencies,
                hermes_url=hermes_url,
                additional_metadata=metadata
            )
            
            if success:
                logger.info(f"Successfully registered {component_name} with Hermes")
                
                # Keep the registration active until interrupted
                try:
                    while True:
                        await asyncio.sleep(60)
                        logger.info(f"{component_name} registration still active...")
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received, shutting down...")
                finally:
                    # Cleanup
                    await engine.close()
                    logger.info("Shutdown complete")
                
                return True
            else:
                logger.error(f"Failed to register {component_name} with Hermes")
                await engine.close()
                return False
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return False


async def shutdown(client, engine, stop_event):
    """
    Perform graceful shutdown.
    
    Args:
        client: HermesRegistrationClient instance
        engine: Planning engine instance
        stop_event: Asyncio event to signal shutdown
    """
    logger.info("Shutting down Prometheus/Epimethius...")
    
    # Stop the planning engine
    await engine.close()
    logger.info("Planning Engine stopped")
    
    # Unregister from Hermes
    if client:
        await client.close()
        logger.info("Unregistered from Hermes")
    
    # Signal to stop the main loop
    stop_event.set()
    logger.info("Shutdown complete")


async def main():
    """Main entry point."""
    args = parse_arguments()
    
    logger.info("Registering Prometheus/Epimethius with Hermes service registry...")
    
    success = await register_prometheus_epimethius(
        hermes_url=args.hermes_url,
        instructions_file=args.instructions_file,
        port=args.port
    )
    
    if success:
        logger.info("Prometheus/Epimethius registration process complete")
    else:
        logger.error("Failed to register Prometheus/Epimethius with Hermes")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())