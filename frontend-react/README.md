# Flight Control Center (React)

React + TypeScript frontend migrated from the Flutter app in `../frontend`. Connects to the existing FastAPI backend for live telemetry and Excel export.

## Prerequisites

- Node.js 20+
- Backend running at `http://127.0.0.1:8000` (see `../backend` and `../scripts/run_backend.bat`)

## Installation

```bash
cd frontend-react
npm install
```

Optional: copy `.env.example` to `.env` and adjust API URLs.

## Run (development)

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Build (production)

```bash
npm run build
npm run preview
```

## Features

- **Analyse** — real-time charts (altitude, speed, az, orientation) + Excel download
- **Navigation** — simulated GPS map with yaw indicator + telemetry sidebar
- **Pilotage** — joystick UI and flight mode placeholders (display-only, same as Flutter)
- Live/pause toggle, theme switch (dark/light), graph buffer reset
- WebSocket telemetry with auto-reconnect

## Stack

- Vite, React 19, TypeScript
- Tailwind CSS v4
- React Router v7
- Zustand (UI state)
- Recharts (graphs)
- Framer Motion (transitions)
- Lucide React (icons)
