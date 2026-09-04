<script lang="ts">
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import AlertCard from '$lib/components/dashboard/AlertCard.svelte';

	import { events, machines } from '$lib/data/mock';

	const averageScore = Math.round(
		machines.reduce((sum, item) => sum + item.score, 0) / machines.length
	);

	const signalQuality = Math.round(
		machines.reduce((sum, item) => sum + item.signalQuality, 0) / machines.length
	);

	const anomalyCount = events.filter((event) => event.severity === 'high').length;
	const warningCount = events.filter((event) => event.severity === 'medium').length;
</script>

<svelte:head>
	<title>Alerts · Acoustic Monitoring</title>
</svelte:head>

<Sidebar />

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar
			machineCount={machines.length}
			{averageScore}
			{signalQuality}
		/>

		<!-- Page heading -->
		<section class="flex flex-col gap-4 pt-1 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<h2 class="text-xl font-semibold tracking-tight text-zinc-100">
					Alert history
				</h2>

				<p class="mt-1 max-w-2xl text-xs leading-relaxed text-zinc-500">
					Review anomaly detections and inspect events before treating them as confirmed machine faults.
				</p>
			</div>

			<div class="flex items-center gap-2">
				<div class="rounded border border-rose-500/15 bg-rose-500/10 px-3 py-2">
					<span class="text-xs text-zinc-500">High</span>
					<span class="ml-2 text-sm font-semibold text-rose-400">{anomalyCount}</span>
				</div>

				<div class="rounded border border-amber-500/15 bg-amber-500/10 px-3 py-2">
					<span class="text-xs text-zinc-500">Warning</span>
					<span class="ml-2 text-sm font-semibold text-amber-400">{warningCount}</span>
				</div>
			</div>
		</section>

		<!-- Alert list -->
		<section class="rounded border border-white/10 bg-[#101014]/90">
			<div class="flex items-center justify-between border-b border-white/10 px-4 py-4 sm:px-5">
				<div>
					<h3 class="text-sm font-medium text-zinc-100">Detector events</h3>
					<p class="mt-1 text-xs text-zinc-500">{events.length} recorded events</p>
				</div>
			</div>

			<div class="space-y-2 p-3 sm:p-4">
				{#each events as event}
					<AlertCard {event} />
				{/each}
			</div>
		</section>
	</div>
</main>