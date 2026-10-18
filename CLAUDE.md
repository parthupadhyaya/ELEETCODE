# Project Overview
We are building a LeetCode visualizer to help users master algorithms. It executes Python code, captures the state trace, uses the Gemini API to translate the trace into animation steps, and visualizes those steps in React using Framer Motion. 

# Tech Stack & Architecture
* Backend: Python, FastAPI, Uvicorn, Google GenAI SDK (gemini-3.8-flash).
* Frontend: React 19, Vite, TailwindCSS (dark mode), Framer Motion, Axios.
* Editor: @monaco-editor/react@next
* Terminal: @pablo-lion/xterm-react

# Build & Run Commands
* Start Backend: `cd backend && venv\Scripts\activate && uvicorn main:app --reload`
* Start Frontend: `cd frontend && npm run dev`
* Install Python packages: `pip install -r requirements.txt`
* Install NPM packages: `npm install`

# Strict Rules
* IMPORTANT: We are using React 19. All libraries must be compatible or use the `@next` tag.
* Never write class components; strictly use functional components and hooks.
* Maintain a minimalist, dark-mode visual style similar to NeetCode. Avoid overly complex 3D graphics.
* Always handle API calls with Axios; never use the native fetch API.
* The backend MUST return a strictly formatted JSON array matching the UI's animation expectations.
