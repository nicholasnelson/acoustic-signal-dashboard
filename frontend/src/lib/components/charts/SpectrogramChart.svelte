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
		minIntensity: number;
		maxIntensity: number;
	};

	let lastInput: SpectrogramPoint[] | undefined;
	let lastPrepared: SpectrogramData = {
		timeLabels: [],
		frequencyLabels: [],
		data: [],
		minIntensity: 0,
		maxIntensity: 1
	};

	function prepareSpectrogram(input: SpectrogramPoint[]): SpectrogramData {
		if (input === lastInput) return lastPrepared;
		lastInput = input;

		if (!input.length) {
			lastPrepared = {
				timeLabels: [],
				frequencyLabels: [],
				data: [],
				minIntensity: 0,
				maxIntensity: 1
			};
			return lastPrepared;
		}

		const times = Array.from(new Set(input.map((point) => point.time))).sort((a, b) => a - b);
		const frequencies = Array.from(new Set(input.map((point) => point.frequency))).sort(
			(a, b) => a - b
		);
		const timeIndex = new Map(times.map((value, index) => [value, index]));
		const frequencyIndex = new Map(frequencies.map((value, index) => [value, index]));

		let minIntensity = input[0].intensity;
		let maxIntensity = input[0].intensity;

		const data: Array<[number, number, number]> = input.map((point) => {
			minIntensity = Math.min(minIntensity, point.intensity);
			maxIntensity = Math.max(maxIntensity, point.intensity);
			return [
				timeIndex.get(point.time) ?? 0,
				frequencyIndex.get(point.frequency) ?? 0,
				point.intensity
			];
		});

		if (minIntensity === maxIntensity) maxIntensity = minIntensity + 1;

		lastPrepared = {
			timeLabels: times.map((value) => value.toFixed(2)),
			frequencyLabels: frequencies.map((value) => value.toFixed(2)),
			data,
			minIntensity,
			maxIntensity
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
				return `<div style="font-weight:600;margin-bottom:6px;color:#fff">Band energy</div>
				<div style="color:#a1a1aa">Time <span style="float:right;margin-left:20px;color:#e4e4e7">${timeLabels[x]} s</span></div>
				<div style="color:#a1a1aa">Band centre <span style="float:right;margin-left:20px;color:#e4e4e7">${frequencyLabels[y]} kHz</span></div>
				<div style="color:#a1a1aa">Energy <span style="float:right;margin-left:20px;color:#c4b5fd">${Number(intensity).toFixed(2)} dB</span></div>`;
			}
		},
		xAxis: {
			type: 'category',
			data: timeLabels,
			name: 'Time (s)',
			nameLocation: 'middle',
			nameGap: 30,
			axisLine: { lineStyle: { color: '#303039' } },
			axisTick: { show: false },
			axisLabel: {
				color: '#71717a',
				fontSize: 11,
				margin: 10,
				interval: Math.max(0, Math.floor(timeLabels.length / 6)),
				formatter: (value: string) => Number(value).toFixed(1)
			},
			nameTextStyle: { color: '#71717a', fontSize: 11 },
			splitLine: { show: false }
		},
		yAxis: {
			type: 'category',
			data: frequencyLabels,
			name: 'Band centre (kHz)',
			nameLocation: 'end',
			nameGap: 12,
			axisLine: { lineStyle: { color: '#303039' } },
			axisTick: { show: false },
			axisLabel: {
				color: '#71717a',
				fontSize: 11,
				margin: 10,
				interval: 0,
				formatter: (value: string) => Number(value).toFixed(2)
			},
			nameTextStyle: { color: '#71717a', fontSize: 11, align: 'left' },
			splitLine: { show: false }
		},
		visualMap: {
			min: prepared.minIntensity,
			max: prepared.maxIntensity,
			dimension: 2,
			orient: 'vertical',
			right: 12,
			top: 'center',
			itemWidth: 9,
			itemHeight: 120,
			calculable: false,
			text: ['High', 'Low'],
			textGap: 8,
			textStyle: { color: '#71717a', fontSize: 10 },
			inRange: {
				color: [
					'#08040f', '#16072d', '#2e1065', '#5b21b6', '#9333ea',
					'#c026d3', '#f43f5e', '#f97316', '#facc15'
				]
			}
		},
		series: [
			{
				type: 'heatmap',
				data,
				progressive: 1000,
				progressiveThreshold: 2000,
				animation: false,
				silent: false,
				itemStyle: { borderWidth: 0 },
				emphasis: { disabled: true }
			}
		]
	} satisfies EChartsOption;
</script>

<EChart {option} {height} minHeight="260px" />
