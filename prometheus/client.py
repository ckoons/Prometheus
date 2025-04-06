"""
Prometheus Client - Client for interacting with the Prometheus planning component.

This module provides a client for interacting with Prometheus's planning capabilities
through the standardized Tekton component client interface.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union

# Try to import from tekton-core first
try:
    from tekton.utils.component_client import (
        ComponentClient,
        ComponentError,
        ComponentNotFoundError,
        CapabilityNotFoundError,
        CapabilityInvocationError,
        ComponentUnavailableError,
        SecurityContext,
        RetryPolicy,
    )
except ImportError:
    # If tekton-core is not available, use a minimal implementation
    from .utils.component_client import (
        ComponentClient,
        ComponentError,
        ComponentNotFoundError,
        CapabilityNotFoundError,
        CapabilityInvocationError,
        ComponentUnavailableError,
        SecurityContext,
        RetryPolicy,
    )

# Configure logger
logger = logging.getLogger(__name__)


class PrometheusClient(ComponentClient):
    """Client for the Prometheus planning component."""
    
    def __init__(
        self,
        component_id: str = "prometheus.planning",
        hermes_url: Optional[str] = None,
        security_context: Optional[SecurityContext] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize the Prometheus client.
        
        Args:
            component_id: ID of the Prometheus component to connect to (default: "prometheus.planning")
            hermes_url: URL of the Hermes API
            security_context: Security context for authentication/authorization
            retry_policy: Policy for retrying capability invocations
        """
        super().__init__(
            component_id=component_id,
            hermes_url=hermes_url,
            security_context=security_context,
            retry_policy=retry_policy
        )
    
    async def create_plan(
        self,
        objective: str,
        context: Optional[Dict[str, Any]] = None,
        complexity_threshold: float = 0.7,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Create a plan for the given objective.
        
        Args:
            objective: The objective to plan for
            context: Optional additional context for planning
            complexity_threshold: Threshold for using latent reasoning
            max_iterations: Maximum reasoning iterations for complex plans
            
        Returns:
            Dictionary with the plan and reasoning details
            
        Raises:
            CapabilityInvocationError: If the plan creation fails
            ComponentUnavailableError: If the Prometheus component is unavailable
        """
        parameters = {
            "objective": objective,
            "complexity_threshold": complexity_threshold,
            "max_iterations": max_iterations
        }
        
        if context:
            parameters["context"] = context
            
        result = await self.invoke_capability("create_plan", parameters)
        
        if not isinstance(result, dict) or "plan" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Prometheus",
                result
            )
            
        return result
    
    async def assess_complexity(
        self,
        objective: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Assess the complexity of a planning objective.
        
        Args:
            objective: The objective to assess
            context: Optional additional context for assessment
            
        Returns:
            Complexity score between 0 and 1
            
        Raises:
            CapabilityInvocationError: If the complexity assessment fails
            ComponentUnavailableError: If the Prometheus component is unavailable
        """
        parameters = {"objective": objective}
        
        if context:
            parameters["context"] = context
            
        result = await self.invoke_capability("assess_complexity", parameters)
        
        if not isinstance(result, dict) or "complexity_score" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Prometheus",
                result
            )
            
        return result["complexity_score"]
    
    async def perform_latent_reasoning(
        self,
        input_content: str,
        max_iterations: int = 3,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform iterative reasoning in latent space.
        
        Args:
            input_content: The input content to reason about
            max_iterations: Maximum number of reasoning iterations
            namespace: Optional namespace for the reasoning session
            
        Returns:
            Dictionary with reasoning results
            
        Raises:
            CapabilityInvocationError: If the latent reasoning fails
            ComponentUnavailableError: If the Prometheus component is unavailable
        """
        parameters = {
            "input_content": input_content,
            "max_iterations": max_iterations
        }
        
        if namespace:
            parameters["namespace"] = namespace
            
        result = await self.invoke_capability("latent_reasoning", parameters)
        
        if not isinstance(result, dict) or "result" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Prometheus",
                result
            )
            
        return result


async def get_prometheus_client(
    component_id: str = "prometheus.planning",
    hermes_url: Optional[str] = None,
    security_context: Optional[SecurityContext] = None,
    retry_policy: Optional[RetryPolicy] = None
) -> PrometheusClient:
    """
    Create a client for the Prometheus planning component.
    
    Args:
        component_id: ID of the Prometheus component to connect to (default: "prometheus.planning")
        hermes_url: URL of the Hermes API
        security_context: Security context for authentication/authorization
        retry_policy: Policy for retrying capability invocations
        
    Returns:
        PrometheusClient instance
        
    Raises:
        ComponentNotFoundError: If the Prometheus component is not found
        ComponentUnavailableError: If the Hermes API is unavailable
    """
    # Try to import from tekton-core first
    try:
        from tekton.utils.component_client import discover_component
    except ImportError:
        # If tekton-core is not available, use a minimal implementation
        from .utils.component_client import discover_component
    
    # Check if the component exists
    await discover_component(component_id, hermes_url)
    
    # Create the client
    return PrometheusClient(
        component_id=component_id,
        hermes_url=hermes_url,
        security_context=security_context,
        retry_policy=retry_policy
    )