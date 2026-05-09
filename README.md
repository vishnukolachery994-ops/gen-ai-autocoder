

# 🤖 GenAI AutoCoder: Autonomous Full-Stack Engine (POC)

**GenAI AutoCoder** is an agentic coding system designed to transform high-level master prompts into fully functional applications. This POC demonstrates a **Fully Autonomous Distributed Parallel Model** where specialized AI agents collabrate to build a complete project from scratch.

---

## 📂 Project Structure

The repository is organized into two sections: the **System Orchestrator** and the **AI-Generated Output**.

### 1. System Orchestrator (The "Maker")

This is the core infrastructure used to build the jewelry site.

* **`main.py`**: The FastAPI server that manages the generation lifecycle.
* **`index.html`**: The main dashboard UI for entering the Master Prompt.
* **`frontend/`**: Contains internal system logic for the Orchestrator's UI.
* `cart.py`: Manages internal state/session logic for the orchestrator interface (not part of the generated app).


* **`agents/`**: The "Brains" of the system.
* `architect.py`: Handles high-level planning and dependency mapping.
* `coder.py`: Powered by `models/gemma-4-26b-a4b-it` to write the actual code.


* **`requirements.txt`**: System dependencies (FastAPI, LangChain, Google Generative AI).

### 2. Generated Project (The "Output")

This is the "Real Project" produced by the agents based on the user's prompt.

* **`generated_project/backend/`**:
* `main.py`: The AI-generated FastAPI server.
* `database.py`: Logic to initialize and seed the SQLite database.
* `ecommerce.db`: The persistent SQLite database created by the agent.


* **`generated_project/frontend/components/`**:
* A library of **TSX** (React + TypeScript) components like `Navbar.tsx`, `ProductGrid.tsx`, and `Hero.tsx`, styled with **Tailwind CSS** in an Amazon/Flipkart aesthetic.



---

## 🚀 Key Strategy: The Distributed Parallel Model

This system utilizes a **Contract-First** approach to ensure that the backend and frontend are perfectly synced without a "toy-app" feel:

1. **Dependency Mapping:** The `ArchitectAgent` defines the DB schema and API endpoints before coding begins.
2. **Parallel Execution:** The `CoderAgent` generates frontend and backend files simultaneously using the blueprint.
3. **Real-Time Validation:** The system auto-executes the generated `database.py` to seed real data, proving the backend is fully functional.

## ⚡ Quick Start

### 1. Setup

```bash
# Install system dependencies
pip install -r requirements.txt

```

### 2. Launch Orchestrator

```bash
python main.py

```

Open `http://127.0.0.1:8000`, enter a prompt (e.g., *"Create a premium jewelry store"*), and monitor the live agent logs.

### 3. Deploy Generated App

Once complete, you can run the new application:

```bash
# Run Backend
cd generated_project/backend
uvicorn main:app --port 8001

```

---

**Developed by:** Vishnu | AI Engineer Intern | 2025 ECE Graduate
