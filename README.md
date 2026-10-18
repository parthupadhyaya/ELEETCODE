# ELEETCODE: LeetCode Visualizer

Step through 150 classic LeetCode solutions and watch the algorithm run: arrays,
pointers, hashmaps, grids, trees, graphs and recursion are drawn live, and every
key moment is explained in plain English.

**Live site:** _coming soon_

## How it works

1. **Trace:** the Python solution runs in a sandboxed subprocess that records
   every line, variable and data structure (`backend/tracer.py`).
2. **Explain:** Gemini turns the trace into an animation script, with one
   plain-English sentence per key moment (`backend/gemini.py`).
3. **Visualize:** React and Framer Motion draw each data structure and highlight
   what the current line reads, writes and changes (`frontend/src/viz`).

Pick **Key moments** to skip the steps where nothing changes. Choose an
explanation level (**Beginner**, **Standard** or **Expert**) to set how much
detail is shown. You can edit the solution or the test input and press
**Run & Visualize** to trace your own code.

## Run locally

Requires Python 3.11+, Node 22+ and a Gemini API key.

```sh
# Backend (http://127.0.0.1:8000)
cd backend
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
echo GEMINI_API_KEY=your-key > .env
uvicorn main:app --reload

# Frontend (http://localhost:5173), in a second terminal
cd frontend
npm install
npm run dev
```

The visualizer works without a key. Only the AI explanations need one.

## Deploy

`render.yaml` and `Dockerfile` deploy the whole site as one Render web service.
In Render, go to **New → Blueprint**, pick this repo, and enter `GEMINI_API_KEY`
when asked.
