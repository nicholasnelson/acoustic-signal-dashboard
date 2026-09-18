<script lang="ts">
  import type { EChartsOption } from 'echarts';
  import EChart from './EChart.svelte';

  export let value = 0;
  export let threshold = 65;
  export let label = 'Anomaly score';
  export let height = '240px';

  $: status = value >= threshold ? 'Anomaly' : value >= threshold * 0.75 ? 'Warning' : 'Normal';
  $: color = value >= threshold ? '#f43f5e' : value >= threshold * 0.75 ? '#f59e0b' : '#8b5cf6';

  $: option = {
    animationDuration: 500,
    series: [
      {
        type: 'gauge',
        startAngle: 225,
        endAngle: -45,
        min: 0,
        max: 100,
        pointer: { show: false },
        progress: { show: true, width: 14, roundCap: false, itemStyle: { color } },
        axisLine: { lineStyle: { width: 14, color: [[1, '#24242d']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        anchor: { show: false },
        title: { show: true, offsetCenter: [0, '40%'], color: '#a1a1aa', fontSize: 13 },
        detail: {
          valueAnimation: true,
          formatter: '{value}',
          offsetCenter: [0, '4%'],
          color: '#fafafa',
          fontSize: 44,
          fontWeight: 600
        },
        data: [{ value, name: status }]
      }
    ],
    graphic: [
      { type: 'text', left: 'center', top: '70%', style: { text: label, fill: '#71717a', fontSize: 11 } }
    ]
  } satisfies EChartsOption;
</script>

<EChart {option} {height} minHeight="210px" />
