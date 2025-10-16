import asyncio

class BaseNode:
    """Base node for all other nodes in workflow"""

    def __init__(self, node_id, node_type="task"):
        self.node_id = node_id
        self.node_type = node_type
    
    async def execute(self, state):
        """
        The main method to execute the node's logic
        It must be implemented by all subclasses
        """
        raise NotImplementedError("Each node must implement the execute method")
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.node_id})"

# -------- Node Implementations -------
class StartNode(BaseNode):
    """ A node that marks the beginning of the work flow"""
    def __init__(self, node_id):
        super().__init__(node_id, node_type="start")
    
    async def execute(self, state):
        print(f"INFO: Executing {self.node_id}....")
        state['history'].append(self.node_id)
        return state

class GetUserDataNode(BaseNode):
    """ To fetch user data asynchronously."""
    async def execute(self, state):
        print(f"INFO: Executing {self.node_id} ......")
        await asyncio.sleep(1) #I/O operation
        state['payload']['user_name'] = "Alex"
        state['payload']['user_email'] = "Alex@example.com"
        state['payload']['user_type'] = "standard"
        state['history'].append(self.node_id)
        return state

class SendWelcomeEmailNode(BaseNode):
    """Simulates sending welcome Email"""
    async def execute(self, state):
        print(f"INFO: Executing: {self.node_id}....")
        await asyncio.sleep(0.5) # simulates I/O (e.g., API Call)
        user_name = state['payload'].get('user_name', 'there')
        email = state['payload'].get('user_email')
        print(f"✅ Email sent to: {email} with body 'Welcome, {user_name}!'")
        state['history'].append(self.node_id)
        return state

class Endnode(BaseNode):
    """ A node that marks the end of a workflow """
    def __init__(self, node_id):
        super().__init__(node_id, node_type="end")
    
    async def execute(self, state):
        print(f"INFO: Executing {self.node_id}...")
        state['history'].append(self.node_id)
        state['status'] = "COMPLETED"
        return state

class EscalateToPremiumSupportNode(BaseNode):
    """A special step for premium users."""
    async def execute(self, state):
        print(f"INFO: Executing {self.node_id}...")
        print("Escalating to premium support queue for user:", state['payload']['user_name'])
        state['history'].append(self.node_id)
        return state

class ProcessStandardUserNode(BaseNode):
    """A simple step for standard users."""
    async def execute(self, state):
        print(f"INFO: Executing {self.node_id}...")
        print(" Processing as a standard user.")
        state['history'].append(self.node_id)
        return state

class RouteUserByTypeNode(BaseNode):
    """
    This is our 'agent'. It inspects the state and decides where to go next.
    """
    def __init__(self, node_id):
        # We explicitly mark this node as type 'agent'
        super().__init__(node_id, node_type="agent")

    async def execute(self, state):
        print(f"INFO: Executing agent {self.node_id}...")
        state['history'].append(self.node_id)
        
        # The agent's decision-making logic
        if state['payload'].get('user_type') == 'premium':
            next_node_id = 'step_escalate'
        else:
            next_node_id = 'step_standard_process'
        
        print(f"🧠 Agent decided the next step is: {next_node_id}")
        
        # Agent nodes return the next node's ID along with the state
        return state, next_node_id
        