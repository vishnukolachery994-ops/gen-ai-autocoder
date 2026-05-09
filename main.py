import subprocess
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent

app = FastAPI(title="GenAI AutoCoder POC")

# Enable CORS so the browser-based prompt frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. FRONTEND FOR USER PROMPT ---
@app.get("/", response_class=HTMLResponse)
async def serve_prompt_ui():
    """Serves the dashboard for entering the Master Prompt."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "index.html")
    
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return """
    <html>
        <body style='font-family:sans-serif; text-align:center; padding-top:50px; background:#0f172a; color:white;'>
            <h1>POC Orchestrator is Running</h1>
            <p style='color:#94a3b8;'>Please ensure <b>index.html</b> is in the root directory: """ + current_dir + """</p>
        </body>
    </html>
    """

# --- 2. THE GENERATION ENDPOINT ---
@app.post("/generate")
async def generate_app(prompt: str):
    """
    Fully Autonomous Strategy:
    Decomposes the prompt, generates a full-stack project structure,
    and initializes the database automatically.
    """
    
    # Phase 1: Architecture Planning
    try:
        architect = ArchitectAgent()
        plan = architect.create_plan(prompt)
    except Exception as e:
        return {"status": f"Architecture Phase Failed: {str(e)}", "files": []}

    # Phase 2: Autonomous Code Generation
    try:
        coder = CoderAgent()
        generated_files_list = coder.generate_files(plan)
    except Exception as e:
        return {"status": f"Coding Phase Failed: {str(e)}", "files": []}

    # Phase 3: Auto-Execution & Initialization
    # Proving the 'Real Project' requirement by auto-seeding the DB
    db_script_path = os.path.normpath(os.path.join("generated_project", "backend", "database.py"))
    
    try:
        # Run the AI-generated script to create jewelry.db / ecommerce.db
        result = subprocess.run(
            ["python", db_script_path], 
            capture_output=True, 
            text=True, 
            check=True
        )
        status_msg = "Success: Full-stack project generated and database seeded!"
    except subprocess.CalledProcessError as e:
        status_msg = f"Warning: Files generated, but database auto-init failed: {e.stderr}"
    except Exception as e:
        status_msg = f"Project generated, but execution error: {str(e)}"

    # CRITICAL: The key 'files' matches the .forEach loop in index.html
    return {
        "status": status_msg,
        "blueprint": plan,
        "files": generated_files_list, 
        "instructions": {
            "backend": "cd generated_project/backend && uvicorn main:app --port 8001",
            "frontend": "React components generated in generated_project/frontend/components",
            "database": "SQLite database initialized and seeded."
        }
    }

if __name__ == "__main__":
    print("--- Starting GenAI AutoCoder POC Orchestrator ---")
    print("Dashboard available at: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)