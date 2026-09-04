<script lang="ts">
  import type { EChartsOption } from 'echarts';
  import type { SignalPoint } from '$lib/types';
  import EChart from './EChart.svelte';

  export let points: SignalPoint[] = [];
  export let height = '280px';

  $: option = {
    animation: false,
    grid: { left: 46, right: 18, top: 18, bottom: 38 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#18181f',
      borderColor: '#34343f',
      textStyle: { color: '#f4f4f5' }
    },
    xAxis: {
      type: 'value',
      min: 0,
      max: 10,
      name: 'Time (s)',
      nameLocation: 'middle',
      nameGap: 26,
      axisLine: { lineStyle: { color: '#34343f' } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,.04)' } },
      axisLabel: { color: '#71717a' },
      nameTextStyle: { color: '#71717a' }
    },
    yAxis: {
      type: 'value',
      min: -1,
      max: 1,
      name: 'Amplitude',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,.05)' } },
      axisLabel: { color: '#71717a' },
      nameTextStyle: { color: '#71717a' }
    },
    series: [
      {
        type: 'line',
        data: points.map((point) => [point.time, point.value]),
        showSymbol: false,
        smooth: false,
        sampling: 'lttb',
        lineStyle: { width: 1.4, color: '#8b5cf6' },
        areaStyle: { color: 'rgba(124,58,237,.08)' }
      }
    ]
  } satisfies EChartsOption;
</script>

<EChart {option} {height} minHeight="220px" />
