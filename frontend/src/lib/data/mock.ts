import type { AlertEvent, Machine, SignalPoint, SpectrogramPoint } from '$lib/types';

export const machines: Machine[] = [
  { id: 'fan-00', name: 'Fan 00', type: 'MIMII Fan', score: 23, signalQuality: 94, amplitude: 0.38, dominantFrequency: 1.42, status: 'normal' },
  { id: 'fan-02', name: 'Fan 02', type: 'MIMII Fan', score: 31, signalQuality: 91, amplitude: 0.42, dominantFrequency: 1.36, status: 'normal' },
  { id: 'fan-04', name: 'Fan 04', type: 'MIMII Fan', score: 78, signalQuality: 87, amplitude: 0.71, dominantFrequency: 2.18, status: 'anomaly' },
  { id: 'fan-06', name: 'Fan 06', type: 'MIMII Fan', score: 61, signalQuality: 90, amplitude: 0.56, dominantFrequency: 1.83, status: 'warning' }
];

export const events: AlertEvent[] = [
  { id: 'evt-1', machineId: 'fan-04', machineName: 'Fan 04', title: 'High anomaly detected', message: 'Score exceeded configured threshold.', score: 78, severity: 'critical', timestamp: '10:24:18' },
  { id: 'evt-2', machineId: 'fan-06', machineName: 'Fan 06', title: 'Moderate anomaly', message: 'Sustained deviation from normal acoustic profile.', score: 61, severity: 'warning', timestamp: '10:22:03' },
  { id: 'evt-3', machineId: 'fan-02', machineName: 'Fan 02', title: 'Signal recovered', message: 'Acoustic features returned to normal range.', score: 31, severity: 'info', timestamp: '10:18:47' }
];

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
    const pulse = index % 91 < 5 ? (random() - 0.5) * 0.9 : 0;
    return { time, value: carrier + noise + pulse };
  });
}

export function generateSpectrogram(timeBins = 82, frequencyBins = 38): SpectrogramPoint[] {
  const output: SpectrogramPoint[] = [];

  for (let x = 0; x < timeBins; x += 1) {
    for (let y = 0; y < frequencyBins; y += 1) {
      const time = (x / (timeBins - 1)) * 10;
      const frequency = (y / (frequencyBins - 1)) * 8;
      const harmonic = Math.exp(-Math.pow(frequency - (0.75 + 0.08 * Math.sin(time)), 2) * 5.2) * 72;
      const harmonic2 = Math.exp(-Math.pow(frequency - 2.05, 2) * 3.1) * 37;
      const transient = x % 13 < 2 ? Math.exp(-frequency / 4.2) * 26 : 0;
      const floor = 8 + 7 * Math.sin(x * 0.41 + y * 0.23);
      output.push({ time, frequency, intensity: Math.max(0, Math.min(100, floor + harmonic + harmonic2 + transient)) });
    }
  }

  return output;
}

export const weeklyScores = [
  { label: 'Mon', value: 28 },
  { label: 'Tue', value: 31 },
  { label: 'Wed', value: 26 },
  { label: 'Thu', value: 42 },
  { label: 'Fri', value: 48 },
  { label: 'Sat', value: 35 },
  { label: 'Sun', value: 23 }
];
