# Clarity

**Turn city chaos into staffing clarity.** Predict foot traffic using weather, events, and maps data—then automatically act.

Built for small businesses (cafes, retail) to predict foot traffic, adjust staffing, and manage inventory in real time.

## Features

- **Foot Traffic Forecast** — Multi-agent predictions fusing weather, MTA subway, and nearby congestion signals
- **Event Surge Simulation** — Simulate weather/construction impacts; see adjusted forecasts, staffing, and inventory
- **Staffing Overview** — Employee schedule with demand-based recommendations
- **Inventory Management** — Low-stock detection, reorder levels, and restock confirmation
- **Restock Email** — Confirm orders to send inventory reports to configured email addresses
- **Agent Dashboard** — Orchestrator, Predictor, and Operator panels with MCP tools

## Tech Stack

| Layer      | Stack                              |
|-----------|------------------------------------|
| Frontend  | Next.js 16, React 19, Tailwind CSS |
| Backend   | FastAPI, Python 3.13               |
| Agents    | OpenAI/OpenRouter (Gemini), MTA API, Open-Meteo |
| UI        | Radix UI, Recharts, shadcn/ui      |

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- pnpm (or npm)

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/BrownHacks2026.git
cd BrownHacks2026
pnpm install
```

### 2. Environment

Create a `.env` file in the project root with your keys:

```bash
# Required for foot traffic forecast
GEMINI_API_KEY=           # or OPENAI_API_KEY (OpenRouter / Gemini)
OPENAI_API_KEY=           # For master agent
WEATHER_API=              # Open-Meteo (optional)
APP_TOKEN=                # NYC Open Data (Socrata)
GOOGLE_PLACE=             # Google Places API (optional)
GOOGLE_API_KEY=           # Google APIs

# Optional: Restock email
DEMO_SMTP_HOST=smtp.gmail.com
DEMO_SMTP_PORT=587
DEMO_SMTP_USERNAME=your@gmail.com
DEMO_SMTP_APP_PASSWORD=   # Google App Password
DEMO_FROM_EMAIL=your@gmail.com
DEMO_TO_EMAILS=recipient@gmail.com
```

### 3. Run Backend

```bash
cd backend
pip install -r requirements.txt   # or uv, poetry, etc.
uvicorn main:app --reload --port 8002
```

### 4. Run Frontend

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Project Structure

```
├── app/                    # Next.js App Router
│   ├── api/                # API routes (proxies to backend)
│   ├── dashboard/          # Main dashboard page
│   ├── agents/             # Agent panels
│   └── layout.tsx
├── components/
│   ├── dashboard/          # Forecast, inventory, staffing, charts
│   ├── agents/             # Orchestrator, Predictor, Operator
│   ├── landing/            # Hero, footer, sections
│   └── ui/                 # shadcn/ui components
├── backend/
│   ├── main.py             # FastAPI app, foot-traffic + restock endpoints
│   ├── agents/             # Master agent, MTA, nearby congestion
│   ├── services/           # send_demo_email, inventory status
│   └── mcp/                # MCP tools
└── lib/                    # Shared types, utils
```

## API Endpoints

| Method | Endpoint                  | Description                    |
|--------|---------------------------|--------------------------------|
| GET    | `/api/foot-traffic-forecast` | Foot traffic prediction (proxied) |
| POST   | `/api/send-restock-email` | Send inventory report email   |
| POST   | `/predict-foot-traffic`   | Raw prediction (backend)      |

Backend runs on port 8002; Next.js proxies `/api/*` to it via `FOOT_TRAFFIC_API_URL`.

## Event Surge Mode

From the Agent panel, click **Simulate Event Surge** to see:

- Weather impact reduced 50%; other sources set to 0
- Predicted customers hardcoded (e.g., 20/hr)
- Demand level "Low", confidence 95%
- Staffing and inventory adjustments
- Confirm Order disabled (tooltip: weather conditions)

## MCP Compatible

The Operator Agent exposes MCP (Model Context Protocol) tools for scheduling, notifications, and ordering. See `backend/mcp/tools.py`.

## Fetch AI Agents

### 🌤️  WeatherAgent 
📍 **Agent Address**: agent1qd9z7s4jujjkyfqphn82yltm0sl7hcwjq8twa3y53kcedw84twveg6hn2k6 <br>
💰 **Wallet Address**: fetch1fw2nyteetn704za08tu2sewqrwsr54jxkgl32s <br>

### 🚇 MTAAgent 
📍 **Agent Address**: agent1qw5h9uz6dd2y04vsz9s5qdasdrtnvl3qkfz0vp82g740wu8eemp3gnpmwge <br>
💰 Wallet Address: fetch1zpzs70a0f7kq3zg3g6a6v0fer3fdcqvpdad5fp  <br>

### 🚗 TrafficAgent 
📍 Agent Address: agent1qdxuu309p6zx8s2dgjrf9st6cjvshf26mrs5cjnuafgesrtdp7lvkfk5fmv <br>
💰 Wallet Address: fetch1r995285yh0yrlv09e9vgrpmahahmppe2pumdug <br>

## License

MIT
