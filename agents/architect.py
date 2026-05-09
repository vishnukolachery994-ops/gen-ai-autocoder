import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class ArchitectAgent:
    def __init__(self):
        # 1. API Configuration
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")
            
        genai.configure(api_key=api_key)
        
        # 2. Model Setup - Keeping your specific model choice
        self.model_name = 'models/gemini-3-flash-preview'
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=(
                "You are a Senior Software Architect. Your task is to decompose user prompts "
                "into structured project plans. You must output ONLY raw JSON. "
                "CRITICAL: Do not include introductory text, bullet points, goals, or headers. "
                "Do not include markdown backticks (```json). "
                "Your entire response must start with '{' and end with '}'. "
                "Ensure keys are always double-quoted and values are properly escaped."
            )
        )
        print(f"DEBUG: Architect initialized using {self.model_name}")

    def create_plan(self, prompt: str):
        print(f"\n[DEBUG] Architect: Planning architecture for: '{prompt}'...")
        
        prompt_template = (
            f"Generate a project plan for: '{prompt}'.\n\n"
            "The JSON must strictly contain these keys:\n"
            "1. 'db_schema': A single string with SQLite CREATE TABLE statements for products, categories, and orders.\n"
            "2. 'components': A list of React component names (e.g., ['Header', 'ProductList']).\n"
            "3. 'endpoints': A list of FastAPI route strings (e.g., ['/products', '/cart/add']).\n"
            "4. 'ui_theme': A description of the visual style (e.g., 'Gold and Black luxury theme').\n\n"
            "STRICT: No conversational filler. JSON only."
        )
        
        try:
            # 3. Generate Content
            response = self.model.generate_content(prompt_template)
            text = response.text.strip()
            
            # DEBUG: See what the model actually returned
            print("-" * 30)
            print(f"DEBUG: RAW MODEL OUTPUT RECEIVED (Length: {len(text)} characters)")
            print(f"DEBUG: START OF OUTPUT: {text[:100]}...") 
            print("-" * 30)

            # 4. ROBUST JSON EXTRACTION
            # Using r"" (Raw strings) to fix SyntaxWarnings
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            
            if not json_match:
                print("[DEBUG] WARNING: Regex failed to find curly braces. Checking for markdown blocks...")
                # Using r"" (Raw strings) here as well
                markdown_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
                if markdown_match:
                    clean_json = markdown_match.group(1)
                else:
                    raise ValueError("No JSON object or markdown block found in response.")
            else:
                clean_json = json_match.group(0)
            
            # 5. Final attempt to parse
            try:
                parsed_plan = json.loads(clean_json)
                print("[DEBUG] Architect: Plan successfully parsed and validated.")
                return parsed_plan
            except json.JSONDecodeError as je:
                print(f"[DEBUG] JSON REPAIR: Initial parse failed ({je}). Attempting substring repair...")
                return self._repair_json(clean_json)
            
        except Exception as e:
            print(f"[DEBUG] GENERAL ERROR in Architect: {e}")
            return self._get_fallback_plan(str(e))

    def _repair_json(self, text):
        """Attempts to find a valid JSON object using raw string regex to avoid warnings."""
        # Fix: Using r'\{' and r'\}' for raw string literals
        starts = [m.start() for m in re.finditer(r'\{', text)]
        ends = [m.start() for m in re.finditer(r'\}', text)]
        
        for start in starts:
            for end in reversed(ends):
                if end > start:
                    try:
                        potential_json = text[start:end+1]
                        return json.loads(potential_json)
                    except json.JSONDecodeError:
                        continue
        
        raise ValueError("Could not extract a valid JSON structure from the response.")

    def _get_fallback_plan(self, reason):
        """Ensures the system never crashes by providing a high-quality default."""
        print(f"[DEBUG] SYSTEM: Triggering Fallback Plan. Reason: {reason}")
        return {
            "db_schema": (
                "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER); "
                "CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT); "
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, total REAL);"
            ),
            "components": ["Navbar", "Hero", "ProductGrid", "ProductCard", "CartDrawer", "Footer"],
            "endpoints": ["/products", "/categories", "/orders"],
            "ui_theme": "Modern Luxury - Deep Black and Metallic Gold accents (Fallback)"
        }

if __name__ == "__main__":
    architect = ArchitectAgent()
    test_prompt = "Create a premium jewelry website with black and gold colors"
    test_plan = architect.create_plan(test_prompt)
    print("\nFINAL PROCESSED PLAN:")
    print(json.dumps(test_plan, indent=2))