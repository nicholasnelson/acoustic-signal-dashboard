import type {
	AlertEvent,
	BackendHealth,
	ClipLabel,
	Machine,
	MachineAnalysis,
	PipelineSettings
} from '$lib/types';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000/api';
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, '');

const ALERT_CACHE_KEY = 'acoustic-dashboard-alert-history-v1';
const MAX_CACHED_ALERTS = 100;

function alertIdentity(event: ApiAlert): string {
	return `${event.id}|${event.timestamp}|${event.machine_id}|${event.window_index ?? 'na'}|${event.score}`;
}

function readCachedApiAlerts(): ApiAlert[] {
	if (typeof window === 'undefined') return [];
	try {
		const raw = window.localStorage.getItem(ALERT_CACHE_KEY);
		if (!raw) return [];
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? (parsed as ApiAlert[]) : [];
	} catch {
		return [];
	}
}

function saveCachedApiAlerts(events: ApiAlert[]): void {
	if (typeof window === 'undefined') return;
	try {
		window.localStorage.setItem(ALERT_CACHE_KEY, JSON.stringify(events.slice(0, MAX_CACHED_ALERTS)));
	} catch {
		// The dashboard can still work from the backend if browser storage is unavailable.
	}
}

function mergeApiAlerts(...groups: ApiAlert[][]): ApiAlert[] {
	const merged = new Map<string, ApiAlert>();
	for (const group of groups) {
		for (const event of group) merged.set(alertIdentity(event), event);
	}
	return [...merged.values()]
		.sort((a, b) => Date.parse(b.timestamp) - Date.parse(a.timestamp))
		.slice(0, MAX_CACHED_ALERTS);
}

async function request<T>(path: string): Promise<T> {
	const response = await fetch(`${API_BASE_URL}${path}`, {
		headers: { Accept: 'application/json' }
	});

	if (!response.ok) {
		let message = `${response.status} ${response.statusText}`;
		try {
			const payload = await response.json();
			if (payload?.detail) message = payload.detail;
		} catch {
			// Keep the HTTP status text when the body is not JSON.
		}
		throw new Error(message);
	}

	return (await response.json()) as T;
}

type ApiMachine = {
	id: string;
	name: string;
	machine_type: string;
	normal_clips: number;
	abnormal_clips: number;
	status: Machine['status'];
	score_index: number | null;
	mean_distance: number | null;
	threshold: number | null;
	signal_quality: number | null;
	last_clip: string | null;
	last_label: ClipLabel | null;
};

type ApiAlert = {
	id: string;
	machine_id: string;
	machine_name: string;
	title: string;
	message: string;
	score: number;
	threshold: number;
	severity: AlertEvent['severity'];
	timestamp: string;
	window_index: number | null;
};

type ApiAnalysis = {
	machine: ApiMachine;
	clip: {
		name: string;
		label: ClipLabel;
		sample_rate: number;
		channels: number;
		duration_seconds: number;
	};
	summary: {
		status: Machine['status'];
		mean_distance: number;
		max_distance: number;
		threshold: number;
		threshold_index: number;
		anomalous_windows: number;
		total_windows: number;
		anomalous_fraction: number;
		rms: number;
		dominant_frequency_khz: number;
		signal_quality: number;
	};
	band_edges_hz: number[];
	waveform: Array<{ time: number; value: number }>;
	spectrogram: Array<{ time: number; frequency: number; intensity: number }>;
	events: ApiAlert[];
};

type ApiSettings = {
	window_seconds: number;
	band_edges_hz: number[];
	threshold_percentile: number;
	baseline_clips: number;
	max_baseline_windows: number;
	waveform_points: number;
};

function mapMachine(machine: ApiMachine): Machine {
	return {
		id: machine.id,
		name: machine.name,
		type: machine.machine_type,
		status: machine.status,
		score: machine.score_index,
		signalQuality: machine.signal_quality,
		normalClips: machine.normal_clips,
		abnormalClips: machine.abnormal_clips,
		meanDistance: machine.mean_distance,
		threshold: machine.threshold,
		lastClip: machine.last_clip,
		lastLabel: machine.last_label
	};
}

function mapAlert(event: ApiAlert): AlertEvent {
	return {
		id: event.id,
		machineId: event.machine_id,
		machineName: event.machine_name,
		title: event.title,
		message: event.message,
		score: event.score,
		threshold: event.threshold,
		scoreIndex: event.threshold > 0 ? (event.score / event.threshold) * 100 : 0,
		severity: event.severity,
		timestamp: new Date(event.timestamp).toLocaleTimeString([], {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
		windowIndex: event.window_index
	};
}

async function getHealth(): Promise<BackendHealth | null> {
	const controller = new AbortController();
	const timeout = window.setTimeout(() => controller.abort(), 2500);

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
		window.clearTimeout(timeout);
	}
}

async function getMachines(): Promise<Machine[]> {
	const machines = await request<ApiMachine[]>('/machines');
	return machines.map(mapMachine);
}

async function getClips(machineId: string, label: ClipLabel, limit = 50): Promise<string[]> {
	const payload = await request<{ clips: string[] }>(
		`/machines/${encodeURIComponent(machineId)}/clips?label=${label}&limit=${limit}`
	);
	return payload.clips;
}

async function getMachineAnalysis(
	machineId: string,
	label: ClipLabel,
	clip?: string
): Promise<MachineAnalysis> {
	const query = new URLSearchParams({ label });
	if (clip) query.set('clip', clip);
	const payload = await request<ApiAnalysis>(
		`/machines/${encodeURIComponent(machineId)}/analysis?${query.toString()}`
	);

	if (payload.events.length) {
		const cached = readCachedApiAlerts();
		saveCachedApiAlerts(mergeApiAlerts(payload.events, cached));
	}

	return {
		machine: mapMachine(payload.machine),
		clip: {
			name: payload.clip.name,
			label: payload.clip.label,
			sampleRate: payload.clip.sample_rate,
			channels: payload.clip.channels,
			durationSeconds: payload.clip.duration_seconds
		},
		summary: {
			status: payload.summary.status,
			meanDistance: payload.summary.mean_distance,
			maxDistance: payload.summary.max_distance,
			threshold: payload.summary.threshold,
			thresholdIndex: payload.summary.threshold_index,
			anomalousWindows: payload.summary.anomalous_windows,
			totalWindows: payload.summary.total_windows,
			anomalousFraction: payload.summary.anomalous_fraction,
			rms: payload.summary.rms,
			dominantFrequencyKHz: payload.summary.dominant_frequency_khz,
			signalQuality: payload.summary.signal_quality
		},
		bandEdgesHz: payload.band_edges_hz,
		waveform: payload.waveform,
		spectrogram: payload.spectrogram,
		events: payload.events.map(mapAlert)
	};
}

async function getEvents(): Promise<AlertEvent[]> {
	const cached = readCachedApiAlerts();
	try {
		const backendEvents = await request<ApiAlert[]>('/events');
		const merged = mergeApiAlerts(backendEvents, cached);
		saveCachedApiAlerts(merged);
		return merged.map(mapAlert);
	} catch {
		return cached.map(mapAlert);
	}
}

async function getSettings(): Promise<PipelineSettings> {
	const value = await request<ApiSettings>('/settings');
	return {
		windowSeconds: value.window_seconds,
		bandEdgesHz: value.band_edges_hz,
		thresholdPercentile: value.threshold_percentile,
		baselineClips: value.baseline_clips,
		maxBaselineWindows: value.max_baseline_windows,
		waveformPoints: value.waveform_points
	};
}

export const monitoringClient = {
	getHealth,
	getMachines,
	getClips,
	getMachineAnalysis,
	getEvents,
	getSettings
};
