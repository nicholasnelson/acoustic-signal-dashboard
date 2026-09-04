<script lang="ts">
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Activity from '@lucide/svelte/icons/activity';
	import Gauge from '@lucide/svelte/icons/gauge';
	import Radio from '@lucide/svelte/icons/radio';

	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import KpiCard from '$lib/components/ui/KpiCard.svelte';

	import WaveformChart from '$lib/components/charts/WaveformChart.svelte';
	import SpectrogramChart from '$lib/components/charts/SpectrogramChart.svelte';
	import GaugeChart from '$lib/components/charts/GaugeChart.svelte';
	import EventList from '$lib/components/dashboard/EventList.svelte';

	import {
		events,
		generateSpectrogram,
		generateWaveform,
		machines
	} from '$lib/data/mock';

	export let data: { id: string };

	$: machine = machines.find((item) => item.id === data.id) ?? machines[0];
	$: machineEvents = events.filter((event) => event.machineId === machine.id);

	$: waveform = generateWaveform(
		10,
		650,
		Number(machine.id.replace(/\D/g, '')) || 1
	);

	$: spectrogram = generateSpectrogram();
</script>

<svelte:head>
	<title>{machine.name} · Acoustic Monitoring</title>
</svelte:head>

<Sidebar />

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">

		<Topbar
			machineCount={machines.length}
			averageScore={machine.score}
			signalQuality={machine.signalQuality}
		/>

		<!-- Machine heading -->
		<div class="flex flex-col gap-4 pt-1">
			<a href="/machines" class="flex w-fit items-center gap-2 text-sm text-zinc-500 hover:text-zinc-200">
				<ArrowLeft size={17} />
				Back to machines
			</a>

			<div>
				<h2 class="text-xl font-semibold text-zinc-100">{machine.name}</h2>
				<p class="mt-1 text-xs text-zinc-500">{machine.type} · Detailed acoustic monitoring</p>
			</div>
		</div>

		<!-- KPIs -->
		<section class="grid gap-3 sm:grid-cols-3">
			<KpiCard
				label="Anomaly score"
				value={`${machine.score}`}
				helper="/100"
				tone="purple"
				icon={Gauge}
			/>

			<KpiCard
				label="Amplitude"
				value={`${machine.amplitude}`}
				helper="RMS"
				tone="purple"
				icon={Activity}
			/>

			<KpiCard
				label="Dominant frequency"
				value={`${machine.dominantFrequency}`}
				helper="kHz"
				tone="purple"
				icon={Radio}
			/>
		</section>

		<!-- Detector + Waveform -->
		<section class="grid gap-3 xl:grid-cols-[280px_minmax(0,1fr)]">
			<Panel title="Detector" subtitle="Current anomaly score">
				<GaugeChart value={machine.score} threshold={65} height="250px" />
			</Panel>

			<Panel title="Waveform" subtitle="Single-channel acoustic stream">
				<div slot="action" class="flex items-center gap-2 rounded bg-violet-500/10 px-2.5 py-1.5 text-[10px] font-medium uppercase text-violet-300">
					<span class="size-1.5 rounded-full bg-violet-400"></span>
					Live
				</div>

				<WaveformChart points={waveform} height="300px" />
			</Panel>
		</section>

		<!-- Spectrogram + Events -->
		<section class="grid gap-3 xl:grid-cols-[minmax(0,1.5fr)_340px]">
			<Panel title="Spectrogram" subtitle="Time-frequency acoustic representation">
				<SpectrogramChart points={spectrogram} height="340px" />
			</Panel>

			<Panel title="Machine events" subtitle="Recent detector activity">
				{#if machineEvents.length}
					<EventList events={machineEvents} />
				{:else}
					<div class="flex min-h-40 items-center justify-center">
						<p class="text-sm text-zinc-500">
							No anomaly events recorded for this machine.
						</p>
					</div>
				{/if}
			</Panel>
		</section>

	</div>
</main>