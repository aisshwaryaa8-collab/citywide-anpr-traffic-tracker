# Person C — Backend + Dashboard: Full Step-by-Step Guide

You are Person C. Your job: build the API and the website that shows the
cars moving between cameras on a map. Everything below assumes you know
**nothing** — follow it in order.

Two files are already built for you in this folder, ready to run:
- `backend/main.py` — the API
- `frontend/index.html` — the dashboard (map + search + chart)

---

## PART 0 — One-time setup on your laptop

1. Install **Python** (3.10+): https://python.org — during install, tick
   "Add Python to PATH".
2. Install **VS Code**: https://code.visualstudio.com
3. Install **Git**: https://git-scm.com

Check they installed correctly. Open a terminal (VS Code → Terminal → New
Terminal) and type:
```bash
python3 --version
git --version
```
You should see version numbers, not an error.

---

## PART 1 — Accept the GitHub invite and download the project

1. Open the "View invitation" link → click **Accept invitation**.
2. In your terminal, go to a folder where you keep projects, then:
   ```bash
   git clone https://github.com/aisshwaryaa8-collab/citywide-anpr-traffic-tracker.git
   cd citywide-anpr-traffic-tracker
   ```
3. Open that folder in VS Code: `code .`

You'll see folders `detection/`, `trajectory_engine/`, `backend_frontend/`,
`shared/`. **`backend_frontend/` is yours.** Don't edit the other two.

---

## PART 2 — Create your own branch

Never work directly on `main` or `dev`. Always make your own branch:
```bash
git checkout dev
git pull
git checkout -b feature/dashboard-ui
```

---

## PART 3 — Drop in the code

Copy the files I built into your repo like this:
```
citywide-anpr-traffic-tracker/
└── backend_frontend/
    ├── backend/
    │   ├── main.py
    │   ├── requirements.txt
    │   └── sample_data/
    │       ├── trajectories_sample.json
    │       └── camera_locations.json
    └── frontend/
        └── index.html
```
So: copy this project's `backend/` folder and `frontend/` folder straight
into your repo's `backend_frontend/` folder.

---

## PART 4 — Run the backend (the API)

In your terminal:
```bash
cd backend_frontend/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Leave this terminal running. Open your browser and go to:
```
http://localhost:8000/docs
```
You'll see an auto-generated page listing your API endpoints
(`/trajectories`, `/trajectories/{plate}`, `/cameras`, `/analytics`).
Click "Try it out" on any of them to see it return data — this is your
backend, already working, using the sample data.

**If `pip install` fails**, try `pip3` instead of `pip`, or
`python3 -m pip install -r requirements.txt`.

---

## PART 5 — Run the frontend (the dashboard)

You can't just double-click `index.html` (browsers block some things when
opening files directly). Instead, open a **second** terminal tab and run:
```bash
cd backend_frontend/frontend
python3 -m http.server 5500
```
Now open your browser to:
```
http://localhost:5500
```
You should see:
- A dark map with 3 amber camera dots
- A left sidebar listing tracked vehicles
- Click any vehicle → a teal dashed line draws its route across cameras
- A search box — type `TN22AB1234` and hit Trace
- A bar chart at the bottom showing vehicle counts per camera

**You now have both pieces of your stage running and talking to each
other**, using the sample JSON data — exactly per Section 3 of the plan.

---

## PART 6 — Understand what each part does (so you can extend it)

**`backend/main.py`**
- Reads two JSON files (`trajectories_sample.json`, `camera_locations.json`)
- Serves them through 4 URLs ("endpoints"):
  - `GET /trajectories` → all vehicles
  - `GET /trajectories/{plate}` → one vehicle by plate
  - `GET /cameras` → camera lat/lng positions
  - `GET /analytics` → counts per camera, computed on the fly
- At the top there are 2 lines (`TRAJECTORIES_FILE`, `CAMERAS_FILE`) — this
  is the ONLY thing you change later to switch from fake to real data.

**`frontend/index.html`**
- One file with HTML + CSS + JavaScript together (simplest for a hackathon).
- On load, it calls your backend's `/cameras` and `/trajectories`, draws
  the camera dots, and lists vehicles in the sidebar.
- Clicking a vehicle (or searching a plate) draws its path as a line
  connecting the cameras in the order it visited them.
- `loadAnalytics()` calls `/analytics` and feeds the numbers into a bar
  chart (using the Chart.js library, loaded from a CDN link at the top).

---

## PART 7 — Save your work to GitHub

```bash
git add .
git commit -m "dashboard: add FastAPI backend + map/search/chart frontend"
git push origin feature/dashboard-ui
```
Then on GitHub.com: open the repo → you'll see a banner
"Compare & pull request" → click it → make sure the target branch is
**`dev`** (not `main`) → tag a teammate → open the pull request.

Do this every hour or two as you make changes — small commits, not one
giant one at the end.

---

## PART 8 — What to build next (in priority order)

1. ✅ Map with camera markers — done
2. ✅ Search by plate — done
3. ✅ Path drawn across cameras — done
4. ✅ Analytics bar chart — done
5. Polish: loading spinner while data fetches, better error message if a
   plate isn't found, mobile-friendly layout tweaks.
6. Nice-to-have: animate a marker moving along the path over time instead
   of a static line (can add later if time allows — not required to win).
7. Prepare your demo narration (you're the one presenting, per the plan):
   "Here's a car entering camera 1... now cam 3... here's the congestion
   chart."

---

## PART 9 — Final integration (do this together with Person A & B)

When Person A and B have real files ready:

1. In `backend/main.py`, change:
   ```python
   TRAJECTORIES_FILE = BASE_DIR / "sample_data" / "trajectories_sample.json"
   CAMERAS_FILE = BASE_DIR / "sample_data" / "camera_locations.json"
   ```
   to point at their real files, e.g.:
   ```python
   TRAJECTORIES_FILE = BASE_DIR.parent.parent / "trajectory_engine" / "trajectories.json"
   CAMERAS_FILE = BASE_DIR.parent.parent / "detection" / "camera_locations.json"
   ```
   (Exact paths depend on where they save them — agree on this together.)
2. Restart the backend (`Ctrl+C`, then re-run `uvicorn main:app --reload --port 8000`).
3. Refresh the dashboard in your browser. It should just work — if it
   doesn't, the plan says: check Section 3 (the contract) first. Usually
   it's a renamed field, a date format mismatch, or an unsorted path array
   — not a bug in your code.
4. Once it works twice in a row, merge `dev` → `main` together.

---

## Troubleshooting cheat sheet

| Problem | Fix |
|---|---|
| Dashboard says "Can't reach the backend" | Make sure `uvicorn` terminal is still running on port 8000 |
| `pip install` errors | Use `pip3` or `python3 -m pip install ...` |
| Port 8000 already in use | `uvicorn main:app --reload --port 8001` and update `API_BASE` in `index.html` |
| Search says "No trajectory found" | Check your spelling matches a plate in the sample data, e.g. `TN22AB1234` |
| Map is grey/blank | Check your internet connection — the map tiles load from the internet |
