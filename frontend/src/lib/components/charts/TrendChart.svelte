<script lang="ts">
  import type { EChartsOption } from 'echarts';
  import EChart from './EChart.svelte';

  export let values: Array<{ label: string; value: number }> = [];
  export let threshold = 65;
  export let height = '230px';

  $: option = {
    animationDuration: 450,
    grid: { left: 38, right: 16, top: 22, bottom: 30 },
    tooltip: { trigger: 'axis', backgroundColor: '#18181f', borderColor: '#34343f', textStyle: { color: '#f4f4f5' } },
    xAxis: {
      type: 'category',
      data: values.map((item) => item.label),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#34343f' } },
      axisLabel: { color: '#71717a' }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,.05)' } },
      axisLabel: { color: '#71717a' }
    },
    series: [
      {
        type: 'bar',
        data: values.map((item) => item.value),
        barMaxWidth: 34,
        itemStyle: { color: '#7c3aed', borderRadius: [8, 8, 2, 2] },
        markLine: {
          symbol: 'none',
          label: { formatter: 'Threshold', color: '#fb7185' },
          lineStyle: { color: '#f43f5e', type: 'dashed' },
          data: [{ yAxis: threshold }]
        }
      }
    ]
  } satisfies EChartsOption;
</script>

<EChart {option} {height} minHeight="200px" />
