import { events, generateSpectrogram, generateWaveform, machines, weeklyScores } from '$lib/data/mock';

export const monitoringClient = {
  async getOverview() {
    return {
      machines,
      events,
      waveform: generateWaveform(),
      spectrogram: generateSpectrogram(),
      weeklyScores,
      threshold: 65
    };
  },

  async getMachine(id: string) {
    const machine = machines.find((item) => item.id === id) ?? machines[0];
    return {
      machine,
      waveform: generateWaveform(10, 650, Number(id.replace(/\D/g, '')) || 1),
      spectrogram: generateSpectrogram(),
      events: events.filter((event) => event.machineId === machine.id),
      threshold: 65
    };
  }
};
