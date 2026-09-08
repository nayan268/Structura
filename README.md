# Structura 📐

Structura is a next-generation distributed engineering canvas. Moving beyond traditional note-taking, it leverages Conflict-Free Replicated Data Types (CRDTs) to provide zero-latency collaborative editing, backed by an event-driven asynchronous architecture designed to handle high-frequency mutation payloads.

Structura acts as an active workspace equipped with hooks for local LLM inference and Vision-Language-Action models, continuously parsing, analyzing, and compiling architectural intent from raw engineering notes without data leaving your local hardware.

## Core Architecture

* **Synchronous Path:** Zero-latency sync via CRDTs (Yjs) over FastAPI WebSockets.
* **Pub/Sub Path:** Horizontal scaling and event fan-out via Redis.
* **Asynchronous Path:** Background workers process document states for persistent cold storage in PostgreSQL and handle heavy AI inference tasks.

---

## Prerequisites Checklist

To run the complete distributed stack locally, ensure the following are installed:

* **Containerization:** [Docker & Docker Compose](https://docs.docker.com/get-docker/) (for local Redis and PostgreSQL).
* **Backend:** [uv](https://github.com/astral-sh/uv) (for lightning-fast Python dependency management and virtual environments).
* **Frontend:** [Node.js 20+](https://nodejs.org/) (for the Vite + React SPA).
* **Local Edge-AI (Optional but Recommended):** 
  * [Ollama](https://ollama.com/) installed locally to serve models like Qwen2.5.
  * NVIDIA CUDA Toolkit installed and configured to leverage the dedicated RTX 1000 Ada Generation GPU for hardware-accelerated local inference. 
  * *Note: The full stack, including background workers and local LLM execution, runs comfortably within a 64GB RAM environment.*

---

## Directory Structure

```text
structura/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes and WebSocket endpoints
│   │   ├── core/         # Config and connection managers
│   │   ├── models/       # SQLAlchemy schemas (Users, Workspaces, Documents)
│   │   ├── services/     # CRDT merge logic and business rules
│   │   └── workers/      # Async queue consumers for AI and storage
│   ├── pyproject.toml    # Managed via uv
│   └── .env
├── frontend/             # Vite + React (Tldraw/Yjs integration)
└── docker-compose.yml    # Local Redis & PostgreSQL infrastructure