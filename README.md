# agentic-orchestrator
A scalable orchestration engine unifying deterministic DAGs with adaptive, agent-driven workflows.
# Agentic Orchestrator 🚀

This project is a dynamic, event-driven orchestration engine built to handle both predictable workflows and adaptive, agentic tasks. Think of it as a smart factory floor that can manage both fixed assembly lines and master craftsmen who need to make decisions on the fly.

---

## 🤔 The Big Idea

We started with a simple question: What if a workflow tool could *think*?

Traditional tools like n8n are great for running tasks in a fixed order (a DAG). But in the real world, especially with AI, you often don't know the next step until you see the current result. Our goal was to build an engine that embraces this uncertainty.

At its heart, our system is a **hybrid**. It can execute a simple, predefined sequence, but it can also pause and hand control over to an "agent" (a smart Python function) to analyze the situation and decide where to go next.

---

## 💡 Core Architecture

We didn't just want to build a script; we wanted to build a proper framework. We based our design on a few key principles you'd find in a real production system.

* **Asynchronous & Event-Driven:** The engine is built on Python's `asyncio`. It doesn't run tasks one by one. Instead, it puts work onto a central queue, and independent workers pick up jobs. This makes it non-blocking, fast, and ready to scale.

* **Resilient State Management:** We use **Redis** as the single source of truth for all workflow states. If the engine crashes mid-workflow, the state is safe. On restart, it can pick up right where it left off, which is a huge deal for reliability.

* **Decoupled API Layer:** The core engine is separate from the outside world. We've exposed its power through a **FastAPI** REST API. This means any UI, script, or external service can control it.

* **Pluggable Node System:** Every task is a self-contained Python class that inherits from a `BaseNode`. This makes the system incredibly extensible. To add a new tool or integration, you just write a new class and add it to the registry—no need to touch the core engine code.

---

## ⚙️ How to Run It

Ready to see it in action? Here’s how to get it running.

1.  **Set up the Environment:**
    First, make sure you're inside the virtual environment.
    ```bash
    # Activate the environment
    source .venv/bin/activate
    
    # Install all the needed packages
    pip install -r requirements.txt
    ```

2.  **Start the Redis Database:**
    The engine needs its memory, so let's start up Redis.
    ```bash
    sudo service redis-server start
    ```

3.  **Launch the API Server:**
    Now, fire up the main application.
    ```bash
    uvicorn api:app --reload
    ```

4.  **Open the UI:**
    Your Codespace will forward port 8000. Just open the forwarded URL in your browser to access the control panel.

---

## 🕹️ How to Use It

The UI is simple. On the left, you define your workflow as a JSON object. On the right, you can execute it and see the live status.

1.  **Define a Workflow:**
    Paste a workflow definition into the text area. For example, use the "Agentic User Onboarding" workflow to test the system's ability to choose between a "premium" and "standard" user path.

### Example Workflow: Agentic User Onboarding

To get you started, here's the JSON for the agentic user onboarding workflow. Just copy and paste this into the UI to test the system's dynamic routing capabilities.

```json
{
    "name": "Agentic User Onboarding",
    "start_at": "step_start",
    "nodes": {
        "step_start": {
            "class": "StartNode",
            "next_node": "step_get_user"
        },
        "step_get_user": {
            "class": "GetUserDataNode",
            "next_node": "step_route_user"
        },
        "step_route_user": {
            "class": "RouteUserByTypeNode"
        },
        "step_escalate": {
            "class": "EscalateToPremiumSupportNode",
            "next_node": "step_send_email"
        },
        "step_standard_process": {
            "class": "ProcessStandardUserNode",
            "next_node": "step_send_email"
        },
        "step_send_email": {
            "class": "SendWelcomeEmailNode",
            "next_node": "step_end"
        },
        "step_end": {
            "class": "EndNode"
        }
    }
}
```

By default, the `GetUserDataNode` will create a "premium" user. To test the agent's other path, you can edit `orchestrator/nodes.py` and change the `user_type` to "standard".

2.  **Save and Run:**
    Click **Save Workflow**, which registers it with the engine. Then click **Run Saved Workflow** to kick it off.

3.  **Watch the Magic:**
    You'll see the status update in real-time on the right. Check the terminal logs to see the detailed step-by-step execution and the agent's decisions.

---
## 🎯 Future Roadmap

This project is in active development. Here are the next big features on the roadmap:

* [ ] **Database Persistence:** Move workflow state from Redis to a persistent SQL database (like PostgreSQL) for long-term logging and auditing.
* [ ] **Visual Workflow Builder:** A drag-and-drop UI (using a library like React Flow) to build workflows instead of writing JSON.
* [ ] **More Node Types:** Add a library of pre-built nodes for common tasks (e.g., `SendSlackMessage`, `QueryDatabase`, `CallLLM`).
* [ ] **CI/CD Pipeline:** Implement GitHub Actions to automatically run tests and deploy the API.
