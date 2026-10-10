// Live detector events from WS /api/stream (see backend api/stream.py).
// Minimal demo
import { writable } from 'svelte/store';

export interface ScoreEvent {
  source_id: string;
  timestamp: string;
  state: 'calibrating' | 'armed';
  progress?: number; // calibrating only, 0..1
  score?: number; // armed only
  threshold?: number;
  is_anomaly?: boolean;
}

const HISTORY = 240; // last minute of windows at a 0.25 s hop

// Most recent event per source.
export const latest = writable<Record<string, ScoreEvent>>({});
// Recent armed events, oldest first, for the trend chart
export const history = writable<ScoreEvent[]>([]);

export function connectStream(): () => void {
  let ws: WebSocket;
  let closed = false;

  const open = () => {
    const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
    ws = new WebSocket(`${scheme}://${location.host}/api/stream`);
    ws.onmessage = (message) => {
      const event: ScoreEvent = JSON.parse(message.data);
      latest.update((all) => ({ ...all, [event.source_id]: event }));
      if (event.state === 'armed') history.update((h) => [...h, event].slice(-HISTORY));
    };
    // Retry on close
    ws.onclose = () => {
      if (!closed) setTimeout(open, 2000);
    };
  };

  open();
  return () => {
    closed = true;
    ws.close();
  };
}
