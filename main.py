# main.py

import asyncio
import uuid
from orchestrator.engine import OrchestrationEngine
from orchestrator.nodes import StartNode, GetUserDataNode, SendWelcomeEmailNode, Endnode,RouteUserByTypeNode,EscalateToPremiumSupportNode,ProcessStandardUserNode
# This dictionary maps the string name of a class to the actual class object.
NODE_REGISTRY = {
    "StartNode": StartNode,
    "GetUserDataNode": GetUserDataNode,
    "RouteUserByTypeNode": RouteUserByTypeNode, # Add the agent
    "EscalateToPremiumSupportNode": EscalateToPremiumSupportNode, # Add the new branch
    "ProcessStandardUserNode": ProcessStandardUserNode, # Add the other branch
    "SendWelcomeEmailNode": SendWelcomeEmailNode,
    "EndNode": Endnode,
}

# workflow structure using the new Node-based architecture
AGENTIC_WORKFLOW = {
    'name': 'Agentic User Onboarding',
    'start_at': 'step_start',
    'nodes': {
        'step_start': {
            'class': 'StartNode',
            'next_node': 'step_get_user'
        },
        'step_get_user': {
            'class': 'GetUserDataNode',
            'next_node': 'step_route_user' # Go to the agent next
        },
        'step_route_user': {
            'class': 'RouteUserByTypeNode' # The agent node doesn't need a 'next_node'
        },
        'step_escalate': { # Premium user branch
            'class': 'EscalateToPremiumSupportNode',
            'next_node': 'step_send_email'
        },
        'step_standard_process': { # Standard user branch
            'class': 'ProcessStandardUserNode',
            'next_node': 'step_send_email'
        },
        'step_send_email': { # Both branches converge here
            'class': 'SendWelcomeEmailNode',
            'next_node': 'step_end'
        },
        'step_end': {
            'class': 'EndNode'
        }
    }
}

async def main():
    # Instantiate the engine with our workflow definition
    engine = OrchestrationEngine(AGENTIC_WORKFLOW, NODE_REGISTRY)

    # Create a worker task to process jobs from the queue
    worker_task = asyncio.create_task(engine.worker())

    # --- Start a new workflow run ---
    run_id = str(uuid.uuid4())
    initial_payload = {"source": "web_signup"}
    await engine.start_workflow(run_id, initial_payload)

    # Wait for the queue to be processed
    await engine.work_queue.join()
    
    # In a real server, the worker would run forever.
    # For this script, we'll stop it after the work is done.
    worker_task.cancel()
    
    # Print the final state from Redis for verification
    final_state = engine.state_manager.get_state(run_id)
    print("\n--- Workflow Finished ---")
    print(f"Final Status: {final_state['status']}")
    print(f"History: {final_state['history']}")
    print(f"Final Payload: {final_state['payload']}")


if __name__ == "__main__":
    asyncio.run(main())