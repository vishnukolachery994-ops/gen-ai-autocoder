import os
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class CoderAgent:
    def __init__(self):
        # 1. API Configuration
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")
        
        genai.configure(api_key=api_key)
        
        # 2. Model Setup
        self.model_name = 'models/gemini-3-flash-preview' 
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=(
                "You are a professional Full-Stack Engine. "
                "Output ONLY raw, production-ready code. No markdown, no chatter. "
                "DESIGN PHILOSOPHY: Default to a clean, professional e-commerce layout (Amazon/Flipkart style). "
                "Use white backgrounds, light gray borders (#e5e7eb), and high-contrast text. "
                "Buttons should be prominent (e.g., Amber/Yellow for primary actions). "
                "ONLY deviate from this design if the specific prompt mentions a different color or theme. "
                "Start immediately with imports."
            )
        )
        self.project_root = "generated_project"
        print(f"DEBUG: Coder initialized using {self.model_name}")

    def generate_files(self, plan: dict):
        """Processes the plan to create a professional marketplace project structure."""
        print("\n[DEBUG] Coder: Commencing generation sequence [Marketplace Mode]...")
        generated_files = []

        # 1. Create Directory Structure
        os.makedirs(os.path.join(self.project_root, "backend"), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "frontend/components"), exist_ok=True)

        # 2. Database Layer
        print("[DEBUG] Coder: Generating Database Layer...")
        db_prompt = (
            f"STRICT: Code only. Write 'database.py' using sqlite3. "
            f"Schema: {plan.get('db_schema')}. "
            "Include 'get_db()' yielding a connection with row_factory = sqlite3.Row. "
            f"Seed the database with professional products for: {plan.get('ui_theme')}. "
            "End with execution block to init_db() and seed_data()."
        )
        db_code = self._ask_llm(db_prompt)
        if db_code:
            self._write_file(os.path.join(self.project_root, "backend", "database.py"), db_code)
            generated_files.append("backend/database.py")
        
        time.sleep(4) # Increased delay to prevent rate limits

        # 3. FastAPI Server
        print("[DEBUG] Coder: Generating Functional API...")
        api_prompt = (
            f"STRICT: Code only. Write FastAPI 'main.py'. "
            f"MUST include CORS for frontend. "
            f"Routes: GET /products, POST /orders. "
            "Use the 'get_db' dependency to interact with the database. "
            "Return clean JSON objects."
        )
        api_code = self._ask_llm(api_prompt)
        if api_code:
            self._write_file(os.path.join(self.project_root, "backend", "main.py"), api_code)
            generated_files.append("backend/main.py")

        # 4. UI Components
        for component in plan.get('components', []):
            time.sleep(4) # Respecting API quotas
            print(f"[DEBUG] Coder: Generating Component: {component}...")
            
            ui_prompt = (
                f"STRICT: Code only. Write React (.tsx) '{component}'. "
                f"Layout: Standard E-commerce pattern (Clean, white background, grid-based). "
                f"Styling: Use Tailwind CSS. Borders: thin-gray. Buttons: solid-amber. "
                f"Theme context provided: {plan.get('ui_theme')}. "
                "Ensure responsive design (mobile-first)."
            )
            
            component_code = self._ask_llm(ui_prompt)
            if component_code:
                path = os.path.join(self.project_root, "frontend", "components", f"{component}.tsx")
                self._write_file(path, component_code)
                generated_files.append(f"frontend/components/{component}.tsx")
            else:
                print(f"   [SKIPPED] Failed to generate {component} after retries.")

        print("[DEBUG] Coder: Generation complete. App is ready for testing.")
        return generated_files

    def _ask_llm(self, prompt, retries=3):
        """Advanced cleaning with built-in retry logic for 500 errors."""
        for i in range(retries):
            try:
                response = self.model.generate_content(prompt)
                
                # Check if response is valid
                if not response or not response.text:
                    raise ValueError("Empty response from AI")

                code = response.text.strip()
                
                # Filter out the 'Internal error' text if it appears in the text
                if "Internal error encountered" in code:
                    raise Exception("500 Error within response text")

                # Remove Markdown block wrappers
                code = re.sub(r"```[a-zA-Z]*", "", code).replace("```", "")

                cleaned_lines = []
                for line in code.splitlines():
                    l_strip = line.strip()
                    if not l_strip:
                        cleaned_lines.append(line)
                        continue

                    # Filter out LLM meta-talk
                    if (l_strip.startswith(("*", "-", "Goal:", "Note:", "Sure", "Here is")) or 
                        re.match(r"^\d+\.", l_strip)):
                        continue
                    
                    cleaned_lines.append(line)
                
                return "\n".join(cleaned_lines).strip()

            except Exception as e:
                # If it's a 500 error or rate limit, wait and retry
                print(f"[DEBUG] LLM Attempt {i+1} failed: {e}. Retrying...")
                time.sleep(5 * (i + 1)) # Wait longer each time (5s, 10s...)
                
        return None # Return None so generate_files knows to skip writing

    def _write_file(self, path, content):
        """Standard file writing utility."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"   [SUCCESS] {path}")
        except Exception as e:
            print(f"   [FAILED] {path}: {e}")