## Repository Structure
```
theta-llm/
├── .github/                   # CI/CD Workflows (Automating Vercel & Digital Ocean)
│   └── workflows/
│       ├── deploy-backend.yml
│       └── deploy-frontend.yml
├── backend/                   # The Brain (FastAPI + Gemini/Local LLM) -> Deploys to Digital Ocean
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Entry point
│   │   ├── core/              # Configs, Secrets, Security
│   │   ├── api/               # API Routes (v1/webhooks, v1/stats)
│   │   ├── services/          # Logic (FacebookService, GeminiService, DatabaseService)
│   │   └── models/            # Pydantic Schemas & DB Models
│   ├── tests/                 # Pytest folder
│   ├── .env.example           # Template for secrets
│   ├── Dockerfile             # Production Docker setup
│   ├── requirements.txt
│   └── start.sh               # Gunicorn/Uvicorn entry script
├── frontend/                  # The Face (Next.js) -> Deploys to Vercel
│   ├── app/                   # App Router (Next.js 14+)
│   ├── components/            # UI Components (Terminal, Stats Card)
│   ├── lib/                   # Utils (API fetchers)
│   ├── public/                # Static assets (images, fonts)
│   ├── package.json
│   └── next.config.js
├── research/                  # The Lab (TeraMind Research)
│   ├── notebooks/             # Jupyter notebooks for testing prompts/ideas
│   ├── datasets/              # Raw data for future fine-tuning
│   └── experiments/           # Scripts to test Gemini vs Llama response quality
├── infra/                     # DevOps & Infrastructure
│   ├── nginx/                 # Nginx configs for Digital Ocean
│   └── docker-compose.yml     # Local development (Run everything with 1 command)
├── .gitignore
└── README.md
```