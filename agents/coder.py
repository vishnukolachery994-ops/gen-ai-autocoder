import os
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class CoderAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")
        
        genai.configure(api_key=api_key)
        
        # Using the requested model version
        self.model_name = 'models/gemini-2.0-flash'
        self.client = genai.GenerativeModel(model_name=self.model_name)
        self.project_root = "generated_project"
        print(f"DEBUG: Coder initialized using Gemini ({self.model_name})")

    def generate_files(self, plan: dict):
        print("\n[DEBUG] Coder: Commencing generation sequence [Marketplace Mode]...")
        generated_files = []

        os.makedirs(os.path.join(self.project_root, "backend"), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "frontend/src/components"), exist_ok=True)

        print("[DEBUG] Coder: Generating Environment Configs (Vite/Tailwind)...")
        configs = self._get_config_templates(plan)
        for filename, content in configs.items():
            path = os.path.join(self.project_root, "frontend", filename)
            self._write_file(path, content)
            generated_files.append(f"frontend/{filename}")

        # Shared Product Type to ensure UI components match Backend exactly
        shared_product_type = (
            "interface Product { "
            "id: number; "
            "name: string; "
            "description: string; "
            "price: number; "
            "stock: number; "
            "image_url: string; "
            "category: string; "
            "}"
        )

        print("[DEBUG] Coder: Generating Database Layer...")
        db_prompt = (
            f"STRICT: Write raw Python code only. Write 'database.py' using 'sqlite3'. "
            "MANDATORY: You must include 'import sqlite3' and 'from contextlib import contextmanager'. "
            "CRITICAL: Every 'try' block MUST have a corresponding 'except Exception as e:' and 'finally:' block. "
            f"Schema: {plan.get('db_schema')}. Must include columns: id, name, description, price, stock, image_url, category. "
            "Include 'get_db()' using a contextmanager that yields a connection with row_factory = sqlite3.Row. "
            f"Seed the database with high-end luxury products for: {plan.get('ui_theme')}. "
            "End with 'if __name__ == \"__main__\":' calling init_db() and seed_data()."
        )
        db_code = self._ask_llm(db_prompt)
        if db_code:
            self._write_file(os.path.join(self.project_root, "backend", "database.py"), db_code)
            generated_files.append("backend/database.py")

        print("[DEBUG] Coder: Generating Functional API...")
        api_prompt = (
            "STRICT: Write raw FastAPI Python code only. Write 'main.py'. "
            "MANDATORY: Include 'from fastapi import FastAPI, Depends, HTTPException' and 'from fastapi.middleware.cors import CORSMiddleware'. "
            "Include 'from database import get_db'. "
            "CORS MUST allow origin 'http://localhost:5173'. "
            "Routes: GET /products (returning list of dicts), POST /orders (accepting product_id: int and quantity: int). "
            "CRITICAL: All try/except blocks must be syntactically complete."
        )
        api_code = self._ask_llm(api_prompt)
        if api_code:
            self._write_file(os.path.join(self.project_root, "backend", "main.py"), api_code)
            generated_files.append("backend/main.py")

        for component in plan.get('components', []):
            print(f"[DEBUG] Coder: Generating Component: {component}...")
            ui_prompt = (
                f"STRICT: Code only. Write React (.tsx) '{component}'. "
                f"Use this exact Type: {shared_product_type} "
                f"Theme: {plan.get('ui_theme')} (Dark mode, bg-black, blue-400 accents). "
                "Styling: Use Tailwind CSS. "
                "API: Fetch from 'http://127.0.0.1:8000/products'. "
                "Props: If this is 'CartDrawer', it must accept 'isOpen: boolean' and 'onClose: () => void'. "
                "Props: If this is 'Navbar', it must accept 'onCartClick: () => void'."
            )
            component_code = self._ask_llm(ui_prompt)
            if component_code:
                path = os.path.join(self.project_root, "frontend/src/components", f"{component}.tsx")
                self._write_file(path, component_code)
                generated_files.append(f"frontend/src/components/{component}.tsx")

        print("[DEBUG] Coder: Generation complete. App is ready for testing.")
        return generated_files

    def _get_config_templates(self, plan):
        components = plan.get('components', [])
        imports = "import { useState } from 'react';\n"
        imports += "\n".join([f"import {c} from './components/{c}';" for c in components])
        
        # Structure logic to ensure props (onCartClick and isOpen) are passed correctly
        renders = ""
        if "Navbar" in components:
            renders += "      <Navbar onCartClick={() => setCartOpen(true)} />\n"
        if "CartDrawer" in components:
            renders += "      <CartDrawer isOpen={cartOpen} onClose={() => setCartOpen(false)} />\n"
        
        for c in components:
            if c not in ["Navbar", "CartDrawer"]:
                renders += f"      <{c} />\n"
        
        app_tsx = (
            f"import React from 'react';\n{imports}\n\n"
            f"function App() {{\n"
            f"  const [cartOpen, setCartOpen] = useState(false);\n\n"
            f"  return (\n"
            f"    <div className=\"min-h-screen bg-black text-white selection:bg-blue-500/30\">\n"
            f"{renders}"
            f"    </div>\n"
            f"  );\n"
            f"}}\n\nexport default App;"
        )

        return {
            "package.json": '{\n  "name": "luxury-app",\n  "private": true,\n  "version": "0.1.0",\n  "type": "module",\n  "scripts": {\n    "dev": "vite",\n    "build": "tsc && vite build",\n    "preview": "vite preview"\n  },\n  "dependencies": {\n    "react": "^18.2.0",\n    "react-dom": "^18.2.0",\n    "lucide-react": "^0.284.0"\n  },\n  "devDependencies": {\n    "@types/react": "^18.2.15",\n    "@types/react-dom": "^18.2.7",\n    "@vitejs/plugin-react": "^4.0.3",\n    "autoprefixer": "^10.4.14",\n    "postcss": "^8.4.27",\n    "tailwindcss": "^3.3.3",\n    "typescript": "^5.0.2",\n    "vite": "^4.4.5"\n  }\n}',
            "tailwind.config.js": "/** @type {import('tailwindcss').Config} */\nexport default {\n  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],\n  theme: { \n    extend: { \n      colors: { \n        gray: { 950: '#0a0a0a' } \n      } \n    } \n  },\n  plugins: [],\n}",
            "postcss.config.js": "export default { plugins: { tailwindcss: {}, autoprefixer: {}, } }",
            "index.html": '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>LUX | Premium Collection</title></head><body class="bg-black"><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>',
            "src/main.tsx": "import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\nimport './index.css';\n\nReactDOM.createRoot(document.getElementById('root')!).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);",
            "src/index.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n@layer base {\n  body { @apply bg-black text-white; }\n}\n\n::-webkit-scrollbar {\n  width: 8px;\n}\n::-webkit-scrollbar-track {\n  background: #000;\n}\n::-webkit-scrollbar-thumb {\n  background: #1e3a8a;\n  border-radius: 10px;\n}",
            "src/App.tsx": app_tsx,
        }

    def _ask_llm(self, prompt, retries=3):
        system_instr = (
            "You are a professional Full-Stack Code Engine. "
            "Output ONLY raw, production-ready code. No markdown fences. No explanations. "
            "Every Python 'try' block MUST end with an 'except' block. "
            "Every React component MUST include necessary React imports."
        )

        banned_patterns = [
            r"^\*", r"^\d+\.", r"^-\s+\w",
            r"^(Wait|Note:|Sure|Here is|Here's|I will|I'll|Based on|This code|I noticed|"
            r"Goal:|Okay|Of course|Let me|The following|Below is|As requested|"
            r"Certainly|Absolutely|Great|This is|In this|We |This file|This component|"
            r"This script|This module|This implementation|This snippet|Final|Check|Refin)",
            r"^\(.*\)$",
            r"^#\s*(Here|This|The|Now|Next|First|Step|I |We |Above|Below|Following|Note|Final|Check|Wait|Let)",
            r"^/{2}\s*(Here|This|The|Now|Next|First|Step|I |We |Above|Below|Following|Note|Final|Check|Wait|Let)",
            r"^$",
        ]
        compiled_patterns = [re.compile(p, re.IGNORECASE) for p in banned_patterns]

        code_start_patterns = [
            r"^import ", r"^from ", r"^def ", r"^class ", r"^const ", r"^export ",
            r"^<!DOCTYPE", r"^<[a-zA-Z]", r"^\{", r"^@",
        ]

        for i in range(retries):
            try:
                full_prompt = f"{system_instr}\n\nTask: {prompt}"
                response = self.client.generate_content(full_prompt)

                code = response.text.strip()
                if not code:
                    raise ValueError("Empty response from Gemini")

                code = re.sub(r"```[a-zA-Z]*", "", code).replace("```", "").strip()

                lines = code.splitlines()
                start_index = 0
                for idx, line in enumerate(lines):
                    if any(re.match(p, line.strip()) for p in code_start_patterns):
                        start_index = idx
                        break
                code = "\n".join(lines[start_index:])

                cleaned_lines = []
                for line in code.splitlines():
                    l_strip = line.strip()
                    if not l_strip:
                        cleaned_lines.append(line)
                        continue
                    if any(p.match(l_strip) for p in compiled_patterns):
                        continue
                    cleaned_lines.append(line)

                return "\n".join(cleaned_lines).strip()

            except Exception as e:
                print(f"[DEBUG] Gemini Attempt {i+1} failed: {e}. Retrying...")
                time.sleep(2 * (i + 1))

        return None

    def _write_file(self, path, content):
        try:
            full_path = os.path.abspath(path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"    [SUCCESS] {path}")
        except Exception as e:
            print(f"    [FAILED] {path}: {e}")
