<script lang="ts">
	import type { EChartsOption } from 'echarts';
	import EChart from './EChart.svelte';

	export let values: Array<{ label: string; value: number }> = [];
	export let threshold = 100;
	export let height = '280px';

	$: maxValue = Math.max(
		125,
		Math.ceil(Math.max(threshold, ...values.map((item) => item.value), 0) / 25) * 25
	);

	$: option = {
		animationDuration: 200,
		grid: { left: 46, right: 18, top: 24, bottom: 34 },
		tooltip: {
			trigger: 'axis',
			backgroundColor: '#18181f',
			borderColor: '#34343f',
			textStyle: { color: '#f4f4f5' }
		},
		xAxis: {
			type: 'category',
			boundaryGap: false,
			data: values.map((item) => item.label),
			axisTick: { show: false },
			axisLine: { lineStyle: { color: '#34343f' } },
			axisLabel: { color: '#71717a', hideOverlap: true }
		},
		yAxis: {
			type: 'value',
			min: 0,
			max: maxValue,
			axisLine: { show: false },
			splitLine: { lineStyle: { color: 'rgba(255,255,255,.05)' } },
			axisLabel: { color: '#71717a' }
		},
		series: [
			{
				type: 'line',
				data: values.map((item) => item.value),
				showSymbol: false,
				smooth: 0.15,
				lineStyle: { width: 2, color: '#8b5cf6' },
				areaStyle: { color: 'rgba(139,92,246,.08)' },
				markLine: {
					symbol: 'none',
					label: { formatter: 'Alert level', color: '#fb7185' },
					lineStyle: { color: '#f43f5e', type: 'dashed' },
					data: [{ yAxis: threshold }]
				}
			}
		]
	} satisfies EChartsOption;
</script>

<EChart {option} {height} minHeight="220px" />
