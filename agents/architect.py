import os
import json
import re
import google.generativeai as genai  # Changed from Groq
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class ArchitectAgent:
    def __init__(self):
        # 1. API Configuration
        # Ensure you have GEMINI_API_KEY in your .env
        api_key = os.getenv("GEMINI_API_KEY") 
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")
            
        genai.configure(api_key=api_key)
        
        # 2. Model Setup - Using the specific Gemini model requested
        self.model_name = ' models/gemini-2.0-flash ' 
        self.client = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        
        print(f"DEBUG: Architect initialized using Gemini ({self.model_name})")

    def create_plan(self, prompt: str):
        print(f"\n[DEBUG] Architect: Planning architecture for: '{prompt}'...")
        
        # System instructions combined with prompt for Gemini
        system_instruction = (
            "You are a Senior Software Architect. Your task is to decompose user prompts "
            "into structured project plans. You must output ONLY raw JSON. "
            "CRITICAL: Do not include introductory text, bullet points, or markdown backticks. "
            "Your entire response must be a single valid JSON object."
        )

        prompt_template = (
            f"{system_instruction}\n\n"
            f"Generate a project plan for: '{prompt}'.\n\n"
            "The JSON must strictly contain these keys:\n"
            "1. 'db_schema': A single string with SQLite CREATE TABLE statements.\n"
            "2. 'components': A list of React component names.\n"
            "3. 'endpoints': A list of FastAPI route strings.\n"
            "4. 'ui_theme': A description of the visual style.\n\n"
            "STRICT: No conversational filler. JSON only."
        )
        
        try:
            # 3. Generate Content using Gemini SDK
            response = self.client.generate_content(prompt_template)
            
            text = response.text.strip()
            
            # DEBUG: See what the model actually returned
            print("-" * 30)
            print(f"DEBUG: RAW MODEL OUTPUT RECEIVED (Length: {len(text)} characters)")
            print(f"DEBUG: START OF OUTPUT: {text[:100]}...") 
            print("-" * 30)

            # 4. JSON PARSING
            try:
                parsed_plan = json.loads(text)
                print("[DEBUG] Architect: Plan successfully parsed and validated.")
                return parsed_plan
            except json.JSONDecodeError as je:
                # Substring repair as a safety net
                print(f"[DEBUG] JSON REPAIR: Attempting substring repair...")
                return self._repair_json(text)
            
        except Exception as e:
            print(f"[DEBUG] GENERAL ERROR in Architect: {e}")
            return self._get_fallback_plan(str(e))

    def _repair_json(self, text):
        """Attempts to find a valid JSON object using raw string regex."""
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
