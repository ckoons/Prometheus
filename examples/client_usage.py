#!/usr/bin/env python3
"""
Example Usage of the Prometheus Client

This script demonstrates how to use the PrometheusClient to interact with the 
Prometheus planning component.
"""

import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prometheus_example")

# Try to import from the prometheus package
try:
    from prometheus.client import PrometheusClient, get_prometheus_client
except ImportError:
    import sys
    import os
    
    # Add the parent directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # Try importing again
    from prometheus.client import PrometheusClient, get_prometheus_client


async def create_plan_example():
    """Example of using the Prometheus client for plan creation."""
    logger.info("=== Plan Creation Example ===")
    
    # Create a Prometheus client
    client = await get_prometheus_client()
    
    try:
        # Simple planning example
        simple_objective = "Create a landing page for the product."
        simple_context = {"deadline": "2 weeks", "team_size": 2}
        
        logger.info(f"Creating plan for simple objective: {simple_objective}")
        simple_plan = await client.create_plan(simple_objective, simple_context)
        
        # Log key information from the plan
        logger.info(f"Used latent reasoning: {simple_plan.get('used_latent_reasoning', False)}")
        logger.info(f"Complexity score: {simple_plan.get('complexity_score', 0.0)}")
        logger.info(f"Iterations: {simple_plan.get('iterations', 1)}")
        
        # Complex planning example
        complex_objective = (
            "Develop a distributed microservice architecture that integrates with legacy systems, "
            "handles high-volume data processing, ensures GDPR compliance, and optimizes for both "
            "performance and maintainability across multiple cloud environments."
        )
        complex_context = {
            "constraints": {
                "budget": "Limited",
                "timeline": "3 months",
                "team": "Cross-functional, 8 members"
            },
            "technologies": ["Kubernetes", "Kafka", "GraphQL", "PostgreSQL"],
            "requirements": ["High availability", "Data privacy", "Audit logging", "Scalability"]
        }
        
        logger.info(f"Creating plan for complex objective: {complex_objective[:50]}...")
        complex_plan = await client.create_plan(complex_objective, complex_context)
        
        # Log key information from the plan
        logger.info(f"Used latent reasoning: {complex_plan.get('used_latent_reasoning', False)}")
        logger.info(f"Complexity score: {complex_plan.get('complexity_score', 0.0)}")
        logger.info(f"Iterations: {complex_plan.get('iterations', 1)}")
    
    except Exception as e:
        logger.error(f"Error in plan creation example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def assess_complexity_example():
    """Example of using the Prometheus client for complexity assessment."""
    logger.info("=== Complexity Assessment Example ===")
    
    # Create a Prometheus client
    client = await get_prometheus_client()
    
    try:
        # Simple objective
        simple_objective = "Create a landing page for the product."
        
        # Complex objective
        complex_objective = (
            "Develop a distributed microservice architecture that integrates with legacy systems, "
            "handles high-volume data processing, ensures GDPR compliance, and optimizes for both "
            "performance and maintainability across multiple cloud environments."
        )
        
        # Assess complexity
        simple_complexity = await client.assess_complexity(simple_objective)
        complex_complexity = await client.assess_complexity(complex_objective)
        
        logger.info(f"Simple objective complexity: {simple_complexity:.4f}")
        logger.info(f"Complex objective complexity: {complex_complexity:.4f}")
    
    except Exception as e:
        logger.error(f"Error in complexity assessment example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def latent_reasoning_example():
    """Example of using the Prometheus client for latent reasoning."""
    logger.info("=== Latent Reasoning Example ===")
    
    # Create a Prometheus client
    client = await get_prometheus_client()
    
    try:
        # Input content for reasoning
        input_content = (
            "Question: What are the key considerations when designing a scalable microservice architecture?\n\n"
            "Initial thoughts: Microservices should be independently deployable, have clear boundaries, "
            "and communicate through well-defined APIs. However, there are many additional factors to consider "
            "for ensuring scalability, resilience, and maintainability."
        )
        
        # Perform latent reasoning
        result = await client.perform_latent_reasoning(
            input_content=input_content,
            max_iterations=2,
            namespace="architecture_design"
        )
        
        # Log key information from the result
        logger.info(f"Thought ID: {result.get('thought_id')}")
        logger.info(f"Iterations: {result.get('iterations', 1)}")
        logger.info(f"Complexity score: {result.get('complexity_score', 0.0)}")
        
        # Log the result
        if "result" in result:
            logger.info(f"Result summary: {result['result'][:100]}...")
    
    except Exception as e:
        logger.error(f"Error in latent reasoning example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def error_handling_example():
    """Example of handling errors with the Prometheus client."""
    logger.info("=== Error Handling Example ===")
    
    # Create a Prometheus client with a non-existent component ID
    try:
        client = await get_prometheus_client(component_id="prometheus.nonexistent")
        # This should raise ComponentNotFoundError
        
    except Exception as e:
        logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    # Create a valid client
    client = await get_prometheus_client()
    
    try:
        # Try to invoke a non-existent capability
        try:
            await client.invoke_capability("nonexistent_capability", {})
        except Exception as e:
            logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    finally:
        # Close the client
        await client.close()


async def main():
    """Run all examples."""
    try:
        await create_plan_example()
        await assess_complexity_example()
        await latent_reasoning_example()
        await error_handling_example()
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())