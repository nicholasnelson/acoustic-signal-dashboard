<script lang="ts">
	import type { EChartsOption } from 'echarts';
	import EChart from './EChart.svelte';

	export let value = 0;
	export let threshold = 100;
	export let label = 'Threshold index';
	export let height = '240px';

	$: status = value >= threshold ? 'Anomaly' : value >= threshold * 0.75 ? 'Warning' : 'Normal';
	$: color = value >= threshold ? '#f43f5e' : value >= threshold * 0.75 ? '#f59e0b' : '#8b5cf6';
	$: maxValue = Math.max(100, Math.ceil(Math.max(value, threshold) / 25) * 25);

	$: option = {
		animationDuration: 500,
		series: [
			{
				type: 'gauge',
				startAngle: 225,
				endAngle: -45,
				min: 0,
				max: maxValue,
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
					formatter: (displayValue: number) => `${Math.round(displayValue)}`,
					offsetCenter: [0, '4%'],
					color: '#fafafa',
					fontSize: 44,
					fontWeight: 600
				},
				data: [{ value, name: status }]
			}
		],
		graphic: [
			{ type: 'text', left: 'center', top: '70%', style: { text: label, fill: '#71717a', fontSize: 11 } },
			{ type: 'text', left: 'center', top: '79%', style: { text: '100 = detector threshold', fill: '#52525b', fontSize: 10 } }
		]
	} satisfies EChartsOption;
</script>

<EChart {option} {height} minHeight="210px" />
