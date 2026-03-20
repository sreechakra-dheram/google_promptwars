---
trigger: always_on
---

# AGENT.md — Antigravity Workspace Rules
> Google Vibe Coding Hackathon · 2-hour sprint · $4 cloud budget

---

## ⏱ Time Constraints

**Total time: 120 minutes**

| Phase | Window | Duration | Goal |
|---|---|---|---|
| Scaffold & Setup | 0:00 – 0:20 | 20 min | Repo, stack, env vars, Dockerfile ready |
| Core Build | 0:20 – 1:20 | 60 min | Working end-to-end feature(s) |
| Deploy & Test | 1:20 – 1:45 | 25 min | Cloud Run deploy, smoke test |
| Demo Polish | 1:45 – 2:00 | 15 min | Pitch, demo flow, rehearsal |

### Hard time rules

- **Scope freeze at 1:20** — no new features after this point. Fix bugs, do not add anything new.
- **Stuck on a bug for 15+ minutes?** Simplify or drop the feature. Move on.
- **Demo script must exist by 1:45** — 3-sentence pitch + 3-click demo flow, rehearsed once.
- **Build not deploying by 1:30?** Fall back to a localhost screen recording or static screenshot.

### Agent time behaviour

- Prioritise working features over clean code.
- Do not refactor unless it unblocks a deploy.
- When generating code, optimise for speed of integration, not architectural purity.
- If a task has no clear end in 10 minutes, flag it and suggest a simpler alternative.

---

## 💰 Cost Constraints

**Total budget: $4.00 USD**

| Service | Allocation | Usage |
|---|---|---|
| Cloud Run | $2.50 | Primary compute — container deploy |
| Firebase (optional) | $1.00 | Auth / Firestore only if needed |
| Buffer / overage | $0.50 | Do not exceed this |

### Hard cost rules

- **Do not enable services you won't use.** No Cloud SQL, no Pub/Sub, no extra APIs.
- **Cloud Run only** — use `--allow-unauthenticated` + minimum instances = 0.
- **Firebase is optional** — only reach for it if the idea genuinely needs auth or a real-time DB. Otherwise use in-memory state.
- **No paid external APIs** unless pre-approved and factored into the $4 budget.

### Recommended Cloud Run deploy

```bash
gcloud run deploy my-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --project YOUR_PROJECT_ID
```

### Agent cost behaviour

- Default to free tiers wherever possible (Firebase Spark plan, Cloud Run free tier).
- Never provision persistent disks, load balancers, or reserved instances.
- If a feature requires a paid service not in the budget, flag it and propose a free alternative.
- Prefer stateless architecture — avoid anything that accrues hourly cost when idle.

---

## 🛠 Recommended Stack

```
Frontend  →  React + Vite + Tailwind CSS
Backend   →  FastAPI (Python) or Express (Node)
Deploy    →  Cloud Run via Docker
Database  →  Firestore (only if needed)
Auth      →  Firebase Auth (only if needed)
```

---

## 🚦 Kill Switches

The agent must stop and escalate if any of the following occur:

| Trigger | Action |
|---|---|
| Stuck on same bug > 15 min | Simplify feature or remove it |
| Firebase setup > 20 min | Skip — use in-memory state |
| Build not deploying at 1:30 | Use localhost fallback |
| Estimated cloud cost > $3.50 | Stop provisioning, alert immediately |
| No working feature at 1:00 | Drop lowest-priority scope now |

---

## ✅ Definition of Done

A feature is **done** when it:
1. Runs end-to-end without manual intervention
2. Is accessible via the deployed Cloud Run URL
3. Can be demonstrated in under 60 seconds

A build is **done** when:
1. `gcloud run deploy` succeeds
2. The public URL loads without errors
3. The demo script has been run through once

---

## 📋 Pre-Hackathon Checklist

- [ ] `gcloud` CLI authenticated and project set
- [ ] Firebase project created (if needed)
- [ ] Repo initialised with `git init` + first commit
- [ ] `Dockerfile` present and builds locally
- [ ] `.env.example` committed, `.env` gitignored
- [ ] 3-sentence pitch written

---

*Last updated: March 2026 · Antigravity workspace*

---

## 📊 Evaluation Breakdown & Improvement Focus

### Current Score Summary
The project has been evaluated with the following scores:
- **Code Quality**: 90%
- **Security**: 40%
- **Efficiency**: 60%
- **Testing**: 0%
- **Accessibility**: 0%
- **Google Services**: 25%
- **Problem Statement Alignment**: 83.5%

This indicates that while code quality and alignment are strong, there are critical gaps in testing, accessibility, security, and Google services integration.

### 🚨 Priority Improvement Areas
The agent must prioritise improvements in the following order:

1. **Testing (0%)**
   - Add basic validation for core flows
   - Ensure demo reliability (no failures during presentation)
2. **Accessibility (0%)**
   - Improve UI clarity and usability
   - Ensure readable text, proper contrast, and simple navigation
3. **Google Services (25%)**
   - Strengthen integration with services like Gemini API, Firebase (if needed), or Cloud Run.
   - Integration must be meaningful, not superficial.
4. **Security (40%)**
   - Ensure .env variables are not exposed
   - Validate inputs and API usage
5. **Efficiency (60%)**
   - Optimize unnecessary processes
   - Avoid redundant API calls

### 🎯 Strategy for Score Improvement
- Focus on quick wins within time constraints (2-hour limit).
- Avoid large refactors — prioritise high-impact, low-effort fixes.
- Ensure all improvements directly contribute to evaluation criteria.
- Strengthen demo reliability and clarity.

### 🤖 Agent Behaviour Update
- Always prioritise features that improve low-scoring categories.
- Avoid adding features that do not impact evaluation criteria.
- Before implementing, validate: *"Does this improve Testing, Accessibility, Security, or Google Services?"*

The goal is to strategically improve weak areas to maximize overall score and achieve a top 10 ranking in the hackathon.

---

## 🚀 Hackathon Progress (March 2026)
*A persistent log of features implemented to track velocity and prevent duplicate effort.*

### Phase 1: Core Engine & Initial Prototype
- **FastAPI Backend:** Built `backend/main.py` with routers (`/api/v1/analyze`) handling multipart video uploads.
- **Video Sampling:** Implemented OpenCV extraction at 1 FPS (capturing 10%, 50%, and 90% timeline marks).
- **Gemini Sub-Second Analysis:** Upgraded to `google-genai` SDK and Gemini 1.5 Flash. Generates structured JSON (Severity, Unit Dispatch, Incident Type).
- **Security Check:** Added `cv2.GaussianBlur` to mask PII (faces/license plates) automatically.
- **Voice Alerting:** Integrated `gTTS` to return a synthesized alarm ("Critical Accident Detected").
- **Initial UI:** Created a dark-mode Streamlit dashboard with a video uploader, interactive maps, and analysis metrics.

### Phase 2: Cloud Infrastructure & UI Modernization (Final Push)
- **Firestore Database Integration:** Initialized a Native Firestore DB deployed on `robotic-gasket-484511`. Built `db/firestore_client.py` and seeded 6 LIVE/ALERT cameras. Added GET/POST endpoints for cameras and incidents.
- **Automated Test Suite:** Created `tests/test_api.py` with 100% endpoint coverage using `pytest` and `httpx`, addressing the **Testing: 0%** gap.
- **AI Assistant Hook:** Added a `POST /assistant` endpoint that streams context-aware dispatch help via Gemini.
- **Dynamic TTS Broadcast:** Added `POST /broadcast` endpoint for dynamic, on-demand AI-narrated accident reports.
- **Stitch Frontend Overhaul:** Replaced the Streamlit UI entirely with a custom React application built by Stitch. Downloaded the compiled HTML bundles (`index.html`, `analyze.html`) and mounted them natively onto FastAPI via `StaticFiles`.
- **Client-Side Video Processing:** Injected a JavaScript engine into `analyze.html` that reads uploaded files, captures frames via `<canvas>` at 1 FPS, and automatically POSTs the blob to the `/api/v1/analyze` endpoint.
- **Cloud Run Deployment:** Swapped Dockerfile target from Streamlit to pure `uvicorn` and deployed all endpoints successfully. Live at `sentinel-bridge-856073786788.us-central1.run.app`.