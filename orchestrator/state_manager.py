import redis
import json
from config import REDIS_HOST,REDIS_DB,REDIS_PORT

class StateManager:
    """
    Handles all state-related operations by interfacing with Redis.
    The state for each workflow run is stored in a Redis Hash.
    """
    def __init__(self):
        self.redis_client=redis.Redis(
            host = REDIS_HOST,
            port = REDIS_PORT,
            db = REDIS_DB,
            decode_responses=True #decodes responses from bytes to strings
        )
        print("✅ StateManager connected to Redis.")
    def initialize_state(self, run_id, initial_payload):
        """creates initial state for new workflow run"""
        initial_state = {
            'run_id' : run_id,
            'status' : "PENDING",
            'current_step': None,
            'payload' : initial_payload,
            'history': [],
            'error': None
        }
        self.save_state(run_id,initial_state)
        return initial_state
    def save_state(self, run_id, state):
        """saves entire state dictionary to a redis hash"""
        # Serialize the entire state dictionary to a single JSON string
        self.redis_client.hset(f"Workflow_run:{run_id}","state",json.dumps(state))
    
    def get_state(self, run_id):
        """Retrieves and deserializes the state dictionary from Redis hash"""
        serialized_state = self.redis_client.hget(f"Workflow_run:{run_id}","state")
        if serialized_state:
            return json.loads(serialized_state)
        return None