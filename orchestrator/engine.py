import asyncio
from .state_manager import StateManager



class OrchestrationEngine:
    def __init__(self, workflow_definition, node_registry):
        self.workflow_def = workflow_definition
        self.node_registry = node_registry
        self.nodes = self._initialize_nodes()
        self.state_manager = StateManager()
        self.work_queue = asyncio.Queue()
    def _initialize_nodes(self):
        """Instantiate all node classes defined in the workflow"""
        nodes = {}
        for node_id, node_config in self.workflow_def['nodes'].items():
            node_class_name = node_config['class']
            # we get the class from global scope and instantiate it.
            node_class = self.node_registry.get(node_class_name)
            if node_class:
                nodes[node_id] = node_class(node_id)
            else:
                raise ValueError("Node Class {node_class_name} not found. ")
        return nodes
    async def execute_step(self, run_id):
        """ The main logic for executing single step of workflow"""
        state = self.state_manager.get_state(run_id)
        if not state or state.get('status') != 'RUNNING':
            print(f"WARNING!: Halting Execution for run_id {run_id} with status {state.get('status')}.")
            return
        
        current_node_id = state['current_step']
        node = self.nodes.get(current_node_id)
        try:
            print(f" Executing node: {node}")
            if node.node_type == 'agent':
                state, next_node_id = await node.execute(state)
            else:
                # Normal task nodes just return the state
                state = await node.execute(state)
                # For normal nodes, get the next step from the definition
                next_node_id = self.workflow_def['nodes'][current_node_id].get('next_node')

            if next_node_id:
                state['current_step'] = next_node_id
            else:
                if state['status'] != 'COMPLETED':
                    state['status'] = 'STUCK'
            
            self.state_manager.save_state(run_id, state)

            if state['status'] == 'RUNNING':
                await self.work_queue.put(run_id)
        
        except Exception as e:
            print(f" Error Executing {current_node_id} for run_id: {run_id}: {e}")
            state['status'] = 'FAILED'
            state['error'] = str(e)
            self.state_manager.save_state(run_id, state)
    async def worker(self):
        """ The worker task is to continuously process work from the queue"""
        print(" Worker started, waiting for tasks..")
        while True:
            run_id = await self.work_queue.get()
            await self.execute_step(run_id)
            self.work_queue.task_done()

    async def start_workflow(self, run_id, initial_payload):
        """Start a new workflow run."""

        initial_state = self.state_manager.initialize_state(run_id, initial_payload)
        start_node_id = self.workflow_def['start_at']
        
        initial_state['current_step'] = start_node_id
        initial_state['status'] = 'RUNNING'
        
        self.state_manager.save_state(run_id,initial_state)
        await self.work_queue.put(run_id)
        print (f"Workflow {run_id} started, initial task queued.")

