<script lang="ts">
  import type { EChartsOption } from 'echarts';
  import type { SpectrogramPoint } from '$lib/types';
  import EChart from './EChart.svelte';

  export let points: SpectrogramPoint[] = [];
  export let height = '320px';

  type SpectrogramData = {
    timeLabels: string[];
    frequencyLabels: string[];
    data: Array<[number, number, number]>;
  };

  let lastInput: SpectrogramPoint[] | undefined;
  let lastPrepared: SpectrogramData = { timeLabels: [], frequencyLabels: [], data: [] };

  function prepareSpectrogram(input: SpectrogramPoint[]): SpectrogramData {
    if (input === lastInput) return lastPrepared;
    lastInput = input;

    if (!input.length) {
      lastPrepared = { timeLabels: [], frequencyLabels: [], data: [] };
      return lastPrepared;
    }

    const uniqueTimes = Array.from(new Set(input.map((p) => Math.round(p.time * 100)))).sort((a, b) => a - b);
    const uniqueFreqs = Array.from(new Set(input.map((p) => Math.round(p.frequency * 100)))).sort((a, b) => a - b);

    // A dashboard-sized heatmap does not need thousands of individual canvas cells.
    // Keep the same visual appearance while capping the rendered grid.
    const maxTimeBins = 64;
    const maxFrequencyBins = 30;
    const timeStep = Math.max(1, Math.ceil(uniqueTimes.length / maxTimeBins));
    const freqStep = Math.max(1, Math.ceil(uniqueFreqs.length / maxFrequencyBins));

    const times = uniqueTimes.filter((_, i) => i % timeStep === 0 || i === uniqueTimes.length - 1);
    const frequencies = uniqueFreqs.filter((_, i) => i % freqStep === 0 || i === uniqueFreqs.length - 1);
    const selectedTimes = new Set(times);
    const selectedFreqs = new Set(frequencies);
    const timeIndex = new Map(times.map((value, index) => [value, index]));
    const frequencyIndex = new Map(frequencies.map((value, index) => [value, index]));
    const data: Array<[number, number, number]> = [];

    for (const point of input) {
      const t = Math.round(point.time * 100);
      const f = Math.round(point.frequency * 100);
      if (!selectedTimes.has(t) || !selectedFreqs.has(f)) continue;
      data.push([
        timeIndex.get(t) ?? 0,
        frequencyIndex.get(f) ?? 0,
        Math.round(point.intensity * 10) / 10
      ]);
    }

    lastPrepared = {
      timeLabels: times.map((value) => (value / 100).toFixed(2)),
      frequencyLabels: frequencies.map((value) => (value / 100).toFixed(2)),
      data
    };
    return lastPrepared;
  }

  $: prepared = prepareSpectrogram(points);
  $: timeLabels = prepared.timeLabels;
  $: frequencyLabels = prepared.frequencyLabels;
  $: data = prepared.data;

  $: option = {
    animation: false,
    backgroundColor: 'transparent',
    grid: { left: 62, right: 74, top: 18, bottom: 48, containLabel: false },
    tooltip: {
      trigger: 'item',
      transitionDuration: 0,
      enterable: false,
      confine: true,
      backgroundColor: '#15151a',
      borderColor: '#2d2d35',
      borderWidth: 1,
      padding: [10, 12],
      textStyle: { color: '#e4e4e7', fontSize: 12 },
      extraCssText: 'box-shadow: 0 12px 30px rgba(0,0,0,.35); border-radius: 6px;',
      formatter: (params: any) => {
        const [x, y, intensity] = params.value;
        return `<div style="font-weight:600;margin-bottom:6px;color:#fff">Spectral sample</div><div style="color:#a1a1aa">Time <span style="float:right;margin-left:20px;color:#e4e4e7">${timeLabels[x]} s</span></div><div style="color:#a1a1aa">Frequency <span style="float:right;margin-left:20px;color:#e4e4e7">${frequencyLabels[y]} kHz</span></div><div style="color:#a1a1aa">Intensity <span style="float:right;margin-left:20px;color:#c4b5fd">${intensity}</span></div>`;
      }
    },
    xAxis: {
      type: 'category', data: timeLabels, name: 'Time (s)', nameLocation: 'middle', nameGap: 30,
      axisLine: { lineStyle: { color: '#303039' } }, axisTick: { show: false },
      axisLabel: { color: '#71717a', fontSize: 11, margin: 10, interval: Math.max(0, Math.floor(timeLabels.length / 6)), formatter: (value: string) => Number(value).toFixed(1) },
      nameTextStyle: { color: '#71717a', fontSize: 11 }, splitLine: { show: false }
    },
    yAxis: {
      type: 'category', data: frequencyLabels, name: 'Frequency (kHz)', nameLocation: 'end', nameGap: 12,
      axisLine: { lineStyle: { color: '#303039' } }, axisTick: { show: false },
      axisLabel: { color: '#71717a', fontSize: 11, margin: 10, interval: Math.max(0, Math.floor(frequencyLabels.length / 5)), formatter: (value: string) => Number(value).toFixed(1) },
      nameTextStyle: { color: '#71717a', fontSize: 11, align: 'left' }, splitLine: { show: false }
    },
    visualMap: {
      min: 0, max: 100, dimension: 2, orient: 'vertical', right: 12, top: 'center', itemWidth: 9, itemHeight: 120, calculable: false,
      text: ['High', 'Low'], textGap: 8, textStyle: { color: '#71717a', fontSize: 10 },
      inRange: { color: ['#08040f','#16072d','#2e1065','#5b21b6','#9333ea','#c026d3','#f43f5e','#f97316','#facc15'] }
    },
    series: [{
      type: 'heatmap',
      data,
      progressive: 1000,
      progressiveThreshold: 2000,
      animation: false,
      silent: false,
      itemStyle: { borderWidth: 0 },
      emphasis: { disabled: true }
    }]
  } satisfies EChartsOption;
</script>

<EChart {option} {height} minHeight="260px" />
