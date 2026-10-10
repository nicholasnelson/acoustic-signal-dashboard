<script lang="ts">
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';

	import Topbar from '$lib/components/layout/Topbar.svelte';

	import Panel from '$lib/components/ui/Panel.svelte';

	import WaveformChart from '$lib/components/charts/WaveformChart.svelte';
	import SpectrogramChart from '$lib/components/charts/SpectrogramChart.svelte';
	import GaugeChart from '$lib/components/charts/GaugeChart.svelte';
	import TrendChart from '$lib/components/charts/TrendChart.svelte';

	import AlertCard from '$lib/components/dashboard/AlertCard.svelte';
	import EventList from '$lib/components/dashboard/EventList.svelte';
	import MachineCard from '$lib/components/dashboard/MachineCard.svelte';

	import { onMount } from 'svelte';

	import {
		events,
		generateSpectrogram,
		generateWaveform,
		machines
	} from '$lib/data/mock';
	import { connectStream, history, latest } from '$lib/services/stream';

	// Mock: waveform and spectrogram need the live display stream (#24); events and
	// alerts need the events API (#22); machines need the sources API (#9).
	const waveform = generateWaveform();
	const spectrogram = generateSpectrogram(64, 30);

	onMount(connectStream);

	// Live: the demo has one source. TODO: pick a source, or aggregate across sources
	$: live = Object.values($latest)[0];
	$: calibrating = !live || live.state === 'calibrating';
	$: threshold = live?.threshold ?? 0;
	// Scores are unbounded distances, so scale the gauge to 3x the threshold
	$: gaugeMax = threshold ? threshold * 3 : 100;
	$: gaugeValue = calibrating
		? Math.round((live?.progress ?? 0) * 100)
		: Math.round(Math.min(live.score ?? 0, gaugeMax) * 10) / 10;
	$: trend = $history.map((e) => ({
		label: new Date(e.timestamp).toLocaleTimeString(),
		value: Math.round((e.score ?? 0) * 100) / 100
	}));

	const averageScore = Math.round(
		machines.reduce((sum, machine) => sum + machine.score, 0) /
			machines.length
	);

	const signalQuality = Math.round(
		machines.reduce(
			(sum, machine) => sum + machine.signalQuality,
			0
		) / machines.length
	);
</script>

<svelte:head>
	<title>Overview · Acoustic Monitoring</title>
	<meta
		name="description"
		content="Acoustic signal monitoring and anomaly detection dashboard"
	/>
</svelte:head>


<main
	class="
		min-h-screen
		bg-[#09090d]
		px-3
		pb-24
		pt-3

		sm:px-5
		sm:pt-5

		lg:pl-[108px]
		lg:pr-6
		lg:pb-8
	"
>
	<div class="mx-auto max-w-[1700px] space-y-4">

		<!-- Floating top information / KPI section -->
		<Topbar
			machineCount={machines.length}
			{averageScore}
			{signalQuality}
		/>

<section class="grid gap-3 xl:grid-cols-[280px_minmax(0,1fr)_320px] 2xl:grid-cols-[300px_minmax(0,1fr)_340px]">
	<Panel
		title="Anomaly score"
		subtitle={live ? `Live · ${live.source_id}` : 'Waiting for detector…'}
		className="h-full"
	>
		<div class="flex h-full flex-col">
			{#if calibrating}
				<GaugeChart value={gaugeValue} threshold={101} label="Calibrating (%)" height="220px" />
			{:else}
				<GaugeChart value={gaugeValue} {threshold} max={gaugeMax} height="220px" />
			{/if}

			<div class="mt-auto flex items-center justify-between border-t border-white/10 pt-4">
				<div>
					<p class="text-[11px] uppercase tracking-wide text-zinc-600">Threshold</p>
					<p class="mt-1 text-xs text-zinc-500">Set at calibration</p>
				</div>

				<span class="text-lg font-semibold text-zinc-100">
					{calibrating ? '—' : threshold.toFixed(2)}
				</span>
			</div>
		</div>
	</Panel>

	<Panel title="Waveform" subtitle="Mock data · single-channel acoustic stream" className="h-full">
		<div slot="action" class="flex items-center gap-2 rounded bg-zinc-500/10 px-2.5 py-1.5 text-[10px] font-medium uppercase tracking-wider text-zinc-400">
			Mock
		</div>

		<WaveformChart points={waveform} height="285px" />

		<div class="mt-3 flex items-center justify-between border-t border-white/10 pt-3 text-xs">
			<span class="text-zinc-500">Audio source</span>
			<span class="font-medium text-zinc-300">MIMII · Fan</span>
		</div>
	</Panel>

	<Panel title="Alerts" subtitle="Mock data - requires attention" className="h-full">
		<div class="flex h-full flex-col">
			<div class="space-y-2">
				{#each events.slice(0, 2) as event}
					<AlertCard {event} />
				{/each}
			</div>

			<a href="/alerts" class="mt-auto flex min-h-11 items-center justify-between border-t border-white/10 pt-4 text-xs font-medium text-zinc-400 hover:text-violet-300">
				<span>View all alerts</span>
				<ChevronRight size={16} strokeWidth={1.8} class="text-zinc-600" />
			</a>
		</div>
	</Panel>
</section>

		<!-- Acoustic analysis row -->
		<section
			class="
				grid
				gap-4

				xl:grid-cols-[minmax(0,1.45fr)_minmax(320px,0.75fr)]
			"
		>
			<!-- Spectrogram -->
			<Panel
				title="Spectrogram"
				subtitle="Mock data - time-frequency representation"
			>
				<SpectrogramChart
					points={spectrogram}
					height="340px"
				/>
			</Panel>

			<div
				class="
					grid
					gap-4

					md:grid-cols-2
					xl:grid-cols-1
				"
			>
				<!-- Events -->
				<Panel
					title="Recent events"
					subtitle="Mock data - latest detector activity"
				>
					<EventList events={events} />
				</Panel>

				<!-- Live score trend. TODO: line chart and time axis; a longer history needs stored scores -->
				<Panel
					title="Anomaly score"
					subtitle="Live, last minute of windows"
				>
					<TrendChart
						values={trend}
						{threshold}
						max={null}
						height="220px"
					/>
				</Panel>
			</div>
		</section>

		<!-- Machines heading -->
		<section
			class="
				flex
				flex-col
				gap-3
				pt-2

				sm:flex-row
				sm:items-end
				sm:justify-between
			"
		>
			<div>
				<h2
					class="
						text-base
						font-semibold
						tracking-tight
						text-zinc-100
					"
				>
					Machines
				</h2>

				<p
					class="
						mt-1
						text-xs
						text-zinc-500
					"
				>
					Select a machine to inspect its acoustic data.
				</p>
			</div>

			<a
				href="/settings"
				class="
					flex
					min-h-11
					w-fit
					items-center
					gap-2
					rounded-xl
					border
					border-white/[0.08]
					px-4
					text-xs
					font-medium
					text-zinc-300
					transition

					hover:bg-white/[0.05]

					active:scale-[0.98]
				"
			>
				<SlidersHorizontal
					size={16}
					strokeWidth={1.8}
				/>

				Controls
			</a>
		</section>

		<!-- Machine cards -->
		<section
			class="
				grid
				gap-3

				sm:grid-cols-2
				xl:grid-cols-4
			"
		>
			{#each machines as machine}
				<MachineCard {machine} />
			{/each}
		</section>

	</div>
</main>