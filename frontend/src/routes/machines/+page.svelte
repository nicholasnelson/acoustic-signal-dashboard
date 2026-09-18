<script lang="ts">
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import MachineCard from '$lib/components/dashboard/MachineCard.svelte';

	import { machines } from '$lib/data/mock';

	const averageScore = Math.round(
		machines.reduce((sum, item) => sum + item.score, 0) / machines.length
	);

	const signalQuality = Math.round(
		machines.reduce((sum, item) => sum + item.signalQuality, 0) / machines.length
	);

	const normalCount = machines.filter((machine) => machine.status === 'normal').length;
	const warningCount = machines.filter((machine) => machine.status === 'warning').length;
	const anomalyCount = machines.filter((machine) => machine.status === 'anomaly').length;
</script>

<svelte:head>
	<title>Machines · Acoustic Monitoring</title>
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
		<section class="flex flex-col gap-3 border-b border-white/10 pb-4 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<h2 class="text-xl font-semibold tracking-tight text-zinc-100">Machines</h2>
				<p class="mt-1 text-xs text-zinc-500">MIMII machine instances available for acoustic monitoring.</p>
			</div>

			<div class="flex flex-wrap items-center gap-2">
				<div class="flex items-center gap-2 rounded border border-white/10 bg-[#101014]/90 px-3 py-2 text-xs">
					<span class="size-1.5 rounded-full bg-emerald-400"></span>
					<span class="text-zinc-500">Normal</span>
					<span class="font-medium text-zinc-200">{normalCount}</span>
				</div>

				<div class="flex items-center gap-2 rounded border border-white/10 bg-[#101014]/90 px-3 py-2 text-xs">
					<span class="size-1.5 rounded-full bg-amber-400"></span>
					<span class="text-zinc-500">Warning</span>
					<span class="font-medium text-zinc-200">{warningCount}</span>
				</div>

				<div class="flex items-center gap-2 rounded border border-white/10 bg-[#101014]/90 px-3 py-2 text-xs">
					<span class="size-1.5 rounded-full bg-rose-400"></span>
					<span class="text-zinc-500">Anomaly</span>
					<span class="font-medium text-zinc-200">{anomalyCount}</span>
				</div>
			</div>
		</section>

		<!-- Machine grid -->
		<section>
			

			<div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
				{#each machines as machine}
					<MachineCard {machine} />
				{/each}
			</div>
		</section>

	</div>
</main>