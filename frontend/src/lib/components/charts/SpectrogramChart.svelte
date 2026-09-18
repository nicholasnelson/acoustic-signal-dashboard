<script lang="ts">
	import type { EChartsOption } from 'echarts';
	import type { SpectrogramPoint } from '$lib/types';
	import EChart from './EChart.svelte';

	export let points: SpectrogramPoint[] = [];
	export let height = '320px';

	$: timeLabels = [...new Set(points.map((p) => p.time.toFixed(2)))]
		.sort((a, b) => Number(a) - Number(b));

	$: frequencyLabels = [...new Set(points.map((p) => p.frequency.toFixed(2)))]
		.sort((a, b) => Number(a) - Number(b));

	$: timeIndex = new Map(timeLabels.map((value, index) => [value, index]));
	$: frequencyIndex = new Map(frequencyLabels.map((value, index) => [value, index]));

	$: data = points.map((point) => [
		timeIndex.get(point.time.toFixed(2)) ?? 0,
		frequencyIndex.get(point.frequency.toFixed(2)) ?? 0,
		Number(point.intensity.toFixed(1))
	]);

	$: option = {
		animation: false,
		backgroundColor: 'transparent',

		grid: {
			left: 62,
			right: 74,
			top: 18,
			bottom: 48,
			containLabel: false
		},

		tooltip: {
			trigger: 'item',
			backgroundColor: '#15151a',
			borderColor: '#2d2d35',
			borderWidth: 1,
			padding: [10, 12],
			textStyle: {
				color: '#e4e4e7',
				fontSize: 12
			},
			extraCssText: 'box-shadow: 0 12px 30px rgba(0,0,0,.35); border-radius: 6px;',
			formatter: (params: any) => {
				const [x, y, intensity] = params.value;

				return `
					<div style="font-weight:600;margin-bottom:6px;color:#fff">Spectral sample</div>
					<div style="color:#a1a1aa">Time <span style="float:right;margin-left:20px;color:#e4e4e7">${timeLabels[x]} s</span></div>
					<div style="color:#a1a1aa">Frequency <span style="float:right;margin-left:20px;color:#e4e4e7">${frequencyLabels[y]} kHz</span></div>
					<div style="color:#a1a1aa">Intensity <span style="float:right;margin-left:20px;color:#c4b5fd">${intensity}</span></div>
				`;
			}
		},

		xAxis: {
			type: 'category',
			data: timeLabels,
			name: 'Time (s)',
			nameLocation: 'middle',
			nameGap: 30,

			axisLine: {
				lineStyle: {
					color: '#303039'
				}
			},

			axisTick: {
				show: false
			},

			axisLabel: {
				color: '#71717a',
				fontSize: 11,
				margin: 10,
				interval: Math.max(0, Math.floor(timeLabels.length / 6)),
				formatter: (value: string) => Number(value).toFixed(1)
			},

			nameTextStyle: {
				color: '#71717a',
				fontSize: 11
			},

			splitLine: {
				show: false
			}
		},

		yAxis: {
			type: 'category',
			data: frequencyLabels,
			name: 'Frequency (kHz)',
			nameLocation: 'end',
			nameGap: 12,

			axisLine: {
				lineStyle: {
					color: '#303039'
				}
			},

			axisTick: {
				show: false
			},

			axisLabel: {
				color: '#71717a',
				fontSize: 11,
				margin: 10,
				interval: Math.max(0, Math.floor(frequencyLabels.length / 5)),
				formatter: (value: string) => Number(value).toFixed(1)
			},

			nameTextStyle: {
				color: '#71717a',
				fontSize: 11,
				align: 'left'
			},

			splitLine: {
				show: false
			}
		},

		visualMap: {
			min: 0,
			max: 100,
			dimension: 2,
			orient: 'vertical',
			right: 12,
			top: 'center',
			itemWidth: 9,
			itemHeight: 120,
			calculable: false,

			text: ['High', 'Low'],
			textGap: 8,

			textStyle: {
				color: '#71717a',
				fontSize: 10
			},

			inRange: {
				color: [
					'#08040f',
					'#16072d',
					'#2e1065',
					'#5b21b6',
					'#9333ea',
					'#c026d3',
					'#f43f5e',
					'#f97316',
					'#facc15'
				]
			}
		},

		series: [
			{
				type: 'heatmap',
				data,

				itemStyle: {
					borderWidth: 0
				},

				emphasis: {
					itemStyle: {
						borderColor: '#ddd6fe',
						borderWidth: 1
					}
				}
			}
		]
	} satisfies EChartsOption;
</script>

<EChart {option} {height} minHeight="260px" />