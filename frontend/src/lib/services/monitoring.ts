import { browser } from '$app/environment';
import { get, writable } from 'svelte/store';
import type {
	AlertEvent,
	BackendHealth,
	Machine,
	MachineStatus,
	ScorePoint,
	StreamConnectionState
} from '$lib/types';

// Same origin: the backend serves the built UI, and Vite proxies /api in dev
const DEFAULT_API_BASE_URL = '/api';
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, '');
const ALERT_CACHE_KEY = 'acoustic-dashboard-live-alert-history-v2';
const MAX_ALERTS = 100;
const MAX_HISTORY_POINTS = 120;

export const machines = writable<Machine[]>([]);
export const alerts = writable<AlertEvent[]>([]);
export const streamState = writable<StreamConnectionState>('idle');

let socket: WebSocket | null = null;
let reconnectTimer: number | null = null;
let started = false;
let previousAnomaly = new Map<string, boolean>();

function websocketUrl(): string {
	if (!browser) return '';
	if (/^https?:\/\//i.test(API_BASE_URL)) {
		return `${API_BASE_URL.replace(/^http/i, 'ws')}/stream`;
	}
	const scheme = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
	const path = API_BASE_URL.startsWith('/') ? API_BASE_URL : `/${API_BASE_URL}`;
	return `${scheme}//${window.location.host}${path}/stream`;
}

function machineName(sourceId: string): string {
	const fanMatch = sourceId.match(/fan[-_ ]?(\d+)/i);
	if (fanMatch) return `Fan ${fanMatch[1].padStart(2, '0')}`;
	return sourceId.replace(/[-_]+/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function machineType(sourceId: string): string {
	const token = sourceId.split(/[-_]/)[0] || 'machine';
	return token.charAt(0).toUpperCase() + token.slice(1);
}

function displayTime(timestamp: string): string {
	const date = new Date(timestamp);
	if (Number.isNaN(date.getTime())) return timestamp;
	return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function readCachedAlerts(): AlertEvent[] {
	if (!browser) return [];
	try {
		const raw = window.localStorage.getItem(ALERT_CACHE_KEY);
		if (!raw) return [];
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? parsed.slice(0, MAX_ALERTS) : [];
	} catch {
		return [];
	}
}

function saveCachedAlerts(value: AlertEvent[]): void {
	if (!browser) return;
	try {
		window.localStorage.setItem(ALERT_CACHE_KEY, JSON.stringify(value.slice(0, MAX_ALERTS)));
	} catch {
		// The live dashboard still works when local storage is unavailable.
	}
}

function upsertMachine(sourceId: string, patch: Partial<Machine>): Machine {
	let updated!: Machine;
	machines.update((current) => {
		const index = current.findIndex((item) => item.id === sourceId);
		const existing: Machine =
			index >= 0
				? current[index]
				: {
						id: sourceId,
						name: machineName(sourceId),
						type: machineType(sourceId),
						status: 'calibrating',
						score: null,
						rawScore: null,
						threshold: null,
						calibrationProgress: 0,
						lastUpdate: null,
						history: []
					};

		updated = { ...existing, ...patch };
		if (index >= 0) {
			const next = [...current];
			next[index] = updated;
			return next;
		}
		return [...current, updated];
	});
	return updated;
}

function pushHistory(machine: Machine, point: ScorePoint): ScorePoint[] {
	return [...machine.history, point].slice(-MAX_HISTORY_POINTS);
}

function addAlert(machine: Machine, timestamp: string, rawScore: number, threshold: number, scoreIndex: number): void {
	const isoTimestamp = new Date(timestamp).toISOString();
	const event: AlertEvent = {
		id: `${machine.id}-${Date.parse(isoTimestamp)}-${Math.round(rawScore * 1000)}`,
		machineId: machine.id,
		machineName: machine.name,
		title: 'Detection score crossed the alert level',
		message: `${machine.name} moved above the learned alert threshold.`,
		score: rawScore,
		threshold,
		scoreIndex,
		severity: 'critical',
		timestamp: displayTime(timestamp),
		isoTimestamp
	};

	alerts.update((current) => {
		const next = [event, ...current.filter((item) => item.id !== event.id)].slice(0, MAX_ALERTS);
		saveCachedAlerts(next);
		return next;
	});
}

type CalibrationEvent = {
	source_id: string;
	timestamp: string;
	state: 'calibrating';
	progress: number;
};

type ArmedEvent = {
	source_id: string;
	timestamp: string;
	state: 'armed';
	score: number;
	threshold: number;
	is_anomaly: boolean;
};

type StreamEvent = CalibrationEvent | ArmedEvent;

function handleEvent(event: StreamEvent): void {
	if (!event?.source_id || !event?.state) return;

	if (event.state === 'calibrating') {
		upsertMachine(event.source_id, {
			status: 'calibrating',
			score: null,
			rawScore: null,
			threshold: null,
			calibrationProgress: Math.max(0, Math.min(1, Number(event.progress) || 0)),
			lastUpdate: event.timestamp
		});
		previousAnomaly.set(event.source_id, false);
		return;
	}

	const rawScore = Number(event.score);
	const threshold = Number(event.threshold);
	const scoreIndex = threshold > 0 ? (rawScore / threshold) * 100 : 0;
	const previous = get(machines).find((item) => item.id === event.source_id);
	const point: ScorePoint = {
		label: displayTime(event.timestamp),
		value: scoreIndex,
		timestamp: event.timestamp
	};
	const status: MachineStatus = event.is_anomaly ? 'anomaly' : 'normal';

	const machine = upsertMachine(event.source_id, {
		status,
		score: scoreIndex,
		rawScore,
		threshold,
		calibrationProgress: 1,
		lastUpdate: event.timestamp,
		history: pushHistory(previous ?? {
			id: event.source_id,
			name: machineName(event.source_id),
			type: machineType(event.source_id),
			status,
			score: null,
			rawScore: null,
			threshold: null,
			calibrationProgress: 1,
			lastUpdate: null,
			history: []
		}, point)
	});

	const wasAnomaly = previousAnomaly.get(event.source_id) ?? false;
	if (event.is_anomaly && !wasAnomaly) {
		addAlert(machine, event.timestamp, rawScore, threshold, scoreIndex);
	}
	previousAnomaly.set(event.source_id, event.is_anomaly);
}

function connect(): void {
	if (!browser) return;
	if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) return;

	streamState.set('connecting');
	socket = new WebSocket(websocketUrl());

	socket.addEventListener('open', () => {
		streamState.set('connected');
	});

	socket.addEventListener('message', (message) => {
		try {
			handleEvent(JSON.parse(String(message.data)) as StreamEvent);
		} catch {
			// Ignore malformed stream messages and keep the connection alive.
		}
	});

	socket.addEventListener('close', () => {
		streamState.set('disconnected');
		machines.update((current) => current.map((machine) => ({ ...machine, status: 'unavailable' })));
		socket = null;
		if (reconnectTimer !== null) window.clearTimeout(reconnectTimer);
		reconnectTimer = window.setTimeout(connect, 2000);
	});

	socket.addEventListener('error', () => {
		streamState.set('disconnected');
	});
}

export function startMonitoring(): void {
	if (!browser) return;
	if (!started) {
		started = true;
		alerts.set(readCachedAlerts());
	}
	connect();
}

export function clearAlertHistory(): void {
	alerts.set([]);
	if (browser) window.localStorage.removeItem(ALERT_CACHE_KEY);
}

async function getHealth(): Promise<BackendHealth | null> {
	const controller = new AbortController();
	const timeout = browser ? window.setTimeout(() => controller.abort(), 2500) : undefined;
	try {
		const response = await fetch(`${API_BASE_URL}/health`, {
			signal: controller.signal,
			headers: { Accept: 'application/json' }
		});
		if (!response.ok) return null;
		const health = (await response.json()) as BackendHealth;
		return health.status === 'ok' ? health : null;
	} catch {
		return null;
	} finally {
		if (browser && timeout !== undefined) window.clearTimeout(timeout);
	}
}

export function getMachine(machineId: string): Machine | null {
	return get(machines).find((machine) => machine.id === machineId) ?? null;
}

export function getAlert(alertId: string): AlertEvent | null {
	return get(alerts).find((event) => event.id === alertId) ?? null;
}

export const monitoringClient = {
	getHealth
};
