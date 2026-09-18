<script lang="ts">
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';

	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import Topbar from '$lib/components/layout/Topbar.svelte';

	import Panel from '$lib/components/ui/Panel.svelte';

	import WaveformChart from '$lib/components/charts/WaveformChart.svelte';
	import SpectrogramChart from '$lib/components/charts/SpectrogramChart.svelte';
	import GaugeChart from '$lib/components/charts/GaugeChart.svelte';
	import TrendChart from '$lib/components/charts/TrendChart.svelte';

	import AlertCard from '$lib/components/dashboard/AlertCard.svelte';
	import EventList from '$lib/components/dashboard/EventList.svelte';
	import MachineCard from '$lib/components/dashboard/MachineCard.svelte';

	import {
		events,
		generateSpectrogram,
		generateWaveform,
		machines,
		weeklyScores
	} from '$lib/data/mock';

	const waveform = generateWaveform();
	const spectrogram = generateSpectrogram();

	const threshold = 65;

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

<!-- Floating desktop navigation -->
<Sidebar />

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
	<Panel title="Anomaly score" subtitle="Aggregate detector output" className="h-full">
		<div class="flex h-full flex-col">
			<GaugeChart value={averageScore} {threshold} height="220px" />

			<div class="mt-auto flex items-center justify-between border-t border-white/10 pt-4">
				<div>
					<p class="text-[11px] uppercase tracking-wide text-zinc-600">Threshold</p>
					<p class="mt-1 text-xs text-zinc-500">Detection limit</p>
				</div>

				<div class="flex items-baseline gap-1">
					<span class="text-lg font-semibold text-zinc-100">{threshold}</span>
					<span class="text-xs text-zinc-600">/100</span>
				</div>
			</div>
		</div>
	</Panel>

	<Panel title="Live waveform" subtitle="Single-channel acoustic stream" className="h-full">
		<div slot="action" class="flex items-center gap-2 rounded bg-violet-500/10 px-2.5 py-1.5 text-[10px] font-medium uppercase tracking-wider text-violet-300">
			<span class="size-1.5 rounded-full bg-violet-400"></span>
			Live
		</div>

		<WaveformChart points={waveform} height="285px" />

		<div class="mt-3 flex items-center justify-between border-t border-white/10 pt-3 text-xs">
			<span class="text-zinc-500">Audio source</span>
			<span class="font-medium text-zinc-300">MIMII · Fan</span>
		</div>
	</Panel>

	<Panel title="Alerts" subtitle="Requires attention" className="h-full">
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
				subtitle="Time-frequency acoustic representation"
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
					subtitle="Latest detector activity"
				>
					<EventList events={events} />
				</Panel>

				<!-- Weekly Trend -->
				<Panel
					title="Weekly anomaly trend"
					subtitle="Average anomaly score over time"
				>
					<TrendChart
						values={weeklyScores}
						{threshold}
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