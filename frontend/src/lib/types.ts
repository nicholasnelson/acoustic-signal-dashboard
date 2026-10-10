export type MachineStatus = 'calibrating' | 'normal' | 'anomaly' | 'unavailable';

export interface ScorePoint {
	label: string;
	value: number;
	timestamp: string;
}

export interface Machine {
	id: string;
	name: string;
	type: string;
	status: MachineStatus;
	score: number | null;
	rawScore: number | null;
	threshold: number | null;
	calibrationProgress: number | null;
	lastUpdate: string | null;
	history: ScorePoint[];
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
	severity: 'critical' | 'info';
	timestamp: string;
	isoTimestamp: string;
}

export interface BackendHealth {
	status: string;
	version: string;
}

export type StreamConnectionState = 'idle' | 'connecting' | 'connected' | 'disconnected';
