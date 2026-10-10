export type MachineStatus = 'ready' | 'normal' | 'warning' | 'anomaly' | 'unavailable';
export type ClipLabel = 'normal' | 'abnormal';

export interface Machine {
	id: string;
	name: string;
	type: string;
	status: MachineStatus;
	score: number | null;
	signalQuality: number | null;
	normalClips: number;
	abnormalClips: number;
	meanDistance: number | null;
	threshold: number | null;
	lastClip: string | null;
	lastLabel: ClipLabel | null;
}

export interface AlertEvent {
	id: string;
	machineId: string;
	machineName: string;
	title: string;
	message: string;
	score: number;
	threshold: number;
	scoreIndex: number;
	severity: 'info' | 'warning' | 'critical';
	timestamp: string;
	windowIndex: number | null;
}

export interface SignalPoint {
	time: number;
	value: number;
}

export interface SpectrogramPoint {
	time: number;
	frequency: number;
	intensity: number;
}

export interface BackendHealth {
	status: string;
	version: string;
}

export interface AnalysisSummary {
	status: MachineStatus;
	meanDistance: number;
	maxDistance: number;
	threshold: number;
	thresholdIndex: number;
	anomalousWindows: number;
	totalWindows: number;
	anomalousFraction: number;
	rms: number;
	dominantFrequencyKHz: number;
	signalQuality: number;
}

export interface MachineAnalysis {
	machine: Machine;
	clip: {
		name: string;
		label: ClipLabel;
		sampleRate: number;
		channels: number;
		durationSeconds: number;
	};
	summary: AnalysisSummary;
	bandEdgesHz: number[];
	waveform: SignalPoint[];
	spectrogram: SpectrogramPoint[];
	events: AlertEvent[];
}

export interface PipelineSettings {
	windowSeconds: number;
	bandEdgesHz: number[];
	thresholdPercentile: number;
	baselineClips: number;
	maxBaselineWindows: number;
	waveformPoints: number;
}
