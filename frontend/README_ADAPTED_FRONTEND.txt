FULL ADAPTED FRONTEND FOR THE NEW LIVE BACKEND

This is the complete frontend folder, not only a source-code patch.

It is adapted to:
- GET /api/health
- WebSocket /api/stream
- live source discovery
- calibration state
- live detection score = backend score / threshold * 100
- live alert history
- alerting machines sorted first
- live score trend
- Vite proxy with WebSocket support
- ngrok / trycloudflare allowed hosts

The old manual REST analysis flow is intentionally removed:
- no /api/machines REST dependency
- no clip list endpoint dependency
- no /analysis endpoint dependency
- no old /events endpoint dependency
- no old detector/settings REST dependency

INSTALL
1. Replace your project's frontend folder with this frontend folder.
2. Open CMD:
   cd /d "D:\CDU\Capstone Project\acoustic-signal-dashboard-live\frontend"
3. Run:
   pnpm install
4. Then:
   pnpm check
5. Then:
   pnpm dev

The FastAPI backend must be running on 127.0.0.1:8000.
Vite proxies /api and /api/stream to it.

IMPORTANT:
The dashboard score is a display ratio:
    detection score = backend raw score / backend threshold * 100

100 = the backend threshold.
It is not a probability and not model accuracy.
