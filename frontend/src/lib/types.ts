export type MachineStatus = 'normal' | 'warning' | 'anomaly';

export interface Machine {
  id: string;
  name: string;
  type: string;
  score: number;
  signalQuality: number;
  amplitude: number;
  dominantFrequency: number;
  status: MachineStatus;
}

export interface AlertEvent {
  id: string;
  machineId: string;
  machineName: string;
  title: string;
  message: string;
  score: number;
  severity: 'info' | 'warning' | 'critical';
  timestamp: string;
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
