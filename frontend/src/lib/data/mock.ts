import type { AlertEvent, Machine, SignalPoint, SpectrogramPoint } from '$lib/types';

// Development-only fixtures. Application routes now use the FastAPI service in
// $lib/services/monitoring.ts rather than importing these values directly.
export const machines: Machine[] = [
	{ id: 'id_00', name: 'Fan 00', type: 'MIMII Fan', status: 'ready', score: null, signalQuality: null, normalClips: 0, abnormalClips: 0, meanDistance: null, threshold: null, lastClip: null, lastLabel: null },
	{ id: 'id_02', name: 'Fan 02', type: 'MIMII Fan', status: 'ready', score: null, signalQuality: null, normalClips: 0, abnormalClips: 0, meanDistance: null, threshold: null, lastClip: null, lastLabel: null }
];

export const events: AlertEvent[] = [];

export function generateWaveform(seconds = 10, samples = 650, seed = 1): SignalPoint[] {
	let state = seed * 9301 + 49297;
	const random = () => {
		state = (state * 233280 + 49297) % 233280;
		return state / 233280;
	};

	return Array.from({ length: samples }, (_, index) => {
		const time = (index / (samples - 1)) * seconds;
		const carrier = Math.sin(time * 16.3) * 0.23 + Math.sin(time * 42.7) * 0.1;
		const noise = (random() - 0.5) * 0.32;
		return { time, value: carrier + noise };
	});
}

export function generateSpectrogram(timeBins = 20, frequencyBins = 6): SpectrogramPoint[] {
	const output: SpectrogramPoint[] = [];
	for (let x = 0; x < timeBins; x += 1) {
		for (let y = 0; y < frequencyBins; y += 1) {
			output.push({ time: x + 0.5, frequency: y + 0.5, intensity: -60 + x + y });
		}
	}
	return output;
}

export const weeklyScores = [
	{ label: 'Mon', value: 28 },
	{ label: 'Tue', value: 31 },
	{ label: 'Wed', value: 26 }
];
