"""
Prometheus/Epimethius API Application

This module defines the FastAPI application for the Prometheus/Epimethius Planning System.
It implements the Single Port Architecture pattern with path-based routing.
"""

import os
import sys
import asyncio
from typing import Dict, Optional
from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown

# Set up logging
logger = setup_component_logging("prometheus")

# Import endpoint routers
from .endpoints import planning, tasks, timelines, resources
from .endpoints import retrospective, history, improvement
from .endpoints import tracking, llm_integration
from .fastmcp_endpoints import mcp_router, fastmcp_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI application lifespan events.
    
    Args:
        app: FastAPI application
    """
    # Startup: Initialize components
    logger.info("Starting Prometheus/Epimethius API...")
    
    # Get port configuration
    config = get_component_config()
    port = config.prometheus.port if hasattr(config, 'prometheus') else int(os.environ.get("PROMETHEUS_PORT"))
    
    # Register with Hermes
    hermes_registration = HermesRegistration()
    heartbeat_task = None
    
    try:
        await hermes_registration.register_component(
            component_name="prometheus",
            port=port,
            version="0.1.0",
            capabilities=[
                "strategic_planning",
                "goal_management",
                "retrospective_analysis",
                "timeline_tracking",
                "resource_optimization"
            ],
            metadata={
                "description": "Strategic planning and goal management",
                "category": "planning"
            }
        )
        
        # Start heartbeat task
        if hermes_registration.is_registered:
            heartbeat_task = asyncio.create_task(heartbeat_loop(hermes_registration, "prometheus"))
        
        # Initialize FastMCP server
        try:
            await fastmcp_server.startup()
            logger.info("FastMCP server initialized successfully")
        except Exception as e:
            logger.warning(f"FastMCP server initialization failed: {e}")
        
        # Initialize engines (will be implemented in future PRs)
        logger.info("Initialization complete")
        
        # Store registration for access in endpoints
        app.state.hermes_registration = hermes_registration
        
        yield
    finally:
        # Cleanup: Shutdown components
        logger.info("Shutting down Prometheus/Epimethius API...")
        
        # Cancel heartbeat task
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Deregister from Hermes
        if hermes_registration.is_registered:
            await hermes_registration.deregister("prometheus")
        
        # Shutdown FastMCP server
        try:
            await fastmcp_server.shutdown()
            logger.info("FastMCP server shut down successfully")
        except Exception as e:
            logger.warning(f"FastMCP server shutdown failed: {e}")
        
        # Give sockets time to close on macOS
        await asyncio.sleep(0.5)
        
        # Cleanup resources (will be implemented in future PRs)
        logger.info("Cleanup complete")


def create_app() -> FastAPI:
    """
    Create the FastAPI application.
    
    Returns:
        FastAPI application
    """
    # Get port configuration
    config = get_component_config()
    port = config.prometheus.port if hasattr(config, 'prometheus') else int(os.environ.get("PROMETHEUS_PORT"))
    
    # Create the FastAPI application
    app = FastAPI(
        title="Prometheus/Epimethius Planning System API",
        description="API for the Prometheus/Epimethius Planning System",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (customize as needed)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
    
    # Add error handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(exc) if os.environ.get("DEBUG", "false").lower() == "true" else None
            }
        )
    
    # WebSocket events
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                # Process WebSocket data (will be implemented in future PRs)
                await websocket.send_json({"status": "received", "data": data})
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
    
    # Root router
    @app.get("/")
    async def root():
        return {
            "name": "Prometheus/Epimethius Planning System API",
            "version": "0.1.0",
            "status": "online",
            "docs_url": f"http://localhost:{port}/docs"
        }
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint following Tekton standards"""
        return {
            "status": "healthy",
            "component": "prometheus",
            "version": "0.1.0",
            "port": port,
            "message": "Prometheus is running normally"
        }
    
    # Mount Prometheus (forward planning) API routes
    prometheus_router = APIRouter(prefix="/api", tags=["prometheus"])
    prometheus_router.include_router(planning.router)
    prometheus_router.include_router(tasks.router)
    prometheus_router.include_router(timelines.router)
    prometheus_router.include_router(resources.router)
    app.include_router(prometheus_router)
    
    # Mount Epimethius (retrospective analysis) API routes
    epimethius_router = APIRouter(prefix="/api", tags=["epimethius"])
    epimethius_router.include_router(retrospective.router)
    epimethius_router.include_router(history.router)
    epimethius_router.include_router(improvement.router)
    app.include_router(epimethius_router)
    
    # Mount shared API routes
    shared_router = APIRouter(prefix="/api", tags=["shared"])
    shared_router.include_router(tracking.router)
    shared_router.include_router(llm_integration.router)
    app.include_router(shared_router)
    
    # Mount MCP API routes
    app.include_router(mcp_router)
    
    return app


# Create the application instance
app = create_app()


# Run the application if this module is executed directly
if __name__ == "__main__":
    from shared.utils.socket_server import run_component_server
    
    run_component_server(
        component_name="prometheus",
        app_module="prometheus.api.app",
        default_port=int(os.environ.get("PROMETHEUS_PORT")),
        reload=False
    )