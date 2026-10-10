<script lang="ts">
	import { onMount } from 'svelte';
	import Search from '@lucide/svelte/icons/search';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import MachineCard from '$lib/components/dashboard/MachineCard.svelte';
	import { machines, startMonitoring } from '$lib/services/monitoring';
	import type { MachineStatus } from '$lib/types';

	let search = '';
	let status: 'all' | MachineStatus = 'all';
	const statusOptions: Array<'all' | MachineStatus> = ['all', 'calibrating', 'normal', 'anomaly'];

	$: scored = $machines.filter((machine) => machine.score !== null);
	$: averageScore = scored.length ? scored.reduce((sum, item) => sum + (item.score ?? 0), 0) / scored.length : null;
	$: normalCount = $machines.filter((machine) => machine.status === 'normal').length;
	$: anomalyCount = $machines.filter((machine) => machine.status === 'anomaly').length;
	$: calibratingCount = $machines.filter((machine) => machine.status === 'calibrating').length;
	$: filteredMachines = [...$machines]
		.sort((a, b) => {
			const rank: Record<string, number> = { anomaly: 0, calibrating: 1, normal: 2, unavailable: 3 };
			return (rank[a.status] ?? 99) - (rank[b.status] ?? 99) || a.name.localeCompare(b.name);
		})
		.filter((machine) => {
			const statusMatch = status === 'all' || machine.status === status;
			const term = search.trim().toLowerCase();
			return statusMatch && (!term || machine.name.toLowerCase().includes(term) || machine.id.toLowerCase().includes(term));
		});

	onMount(startMonitoring);
</script>

<svelte:head><title>Machines · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={$machines.length} {averageScore} />
		<section class="flex flex-col gap-3 pb-4 sm:flex-row sm:items-end sm:justify-between">
			<div><h2 class="text-xl font-semibold tracking-tight text-zinc-100">Machines</h2><p class="mt-1 text-xs text-zinc-500">Live sources discovered from the backend WebSocket stream.</p></div>
			<div class="flex flex-wrap items-center gap-2 text-xs">
				<div class="rounded border border-white/10 px-3 py-2 text-zinc-400">Calibrating <span class="ml-1 text-violet-300">{calibratingCount}</span></div>
				<div class="rounded border border-white/10 px-3 py-2 text-zinc-400">Normal <span class="ml-1 text-emerald-400">{normalCount}</span></div>
				<div class="rounded border border-white/10 px-3 py-2 text-zinc-400">Alert <span class="ml-1 text-rose-400">{anomalyCount}</span></div>
			</div>
		</section>

		<section class="grid gap-3 rounded border border-white/10 bg-[#101014]/90 p-4 md:grid-cols-[1fr_auto]">
			<label class="relative block"><Search size={16} class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600" /><input bind:value={search} placeholder="Search source" class="min-h-11 w-full rounded border border-white/10 bg-[#15151b] pl-9 pr-3 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-violet-500/50" /></label>
			<div class="flex flex-wrap items-center gap-2">{#each statusOptions as item}<button type="button" on:click={() => (status = item)} class={`min-h-11 rounded border px-3 text-xs font-medium capitalize transition ${status === item ? 'border-violet-500/30 bg-violet-500/10 text-violet-300' : 'border-white/10 text-zinc-500 hover:bg-white/[0.04] hover:text-zinc-200'}`}>{item === 'anomaly' ? 'alert' : item}</button>{/each}</div>
		</section>

		{#if filteredMachines.length}
			<section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">{#each filteredMachines as machine}<MachineCard {machine} />{/each}</section>
		{:else}
			<div class="rounded border border-white/10 bg-[#101014]/90 p-8 text-center text-sm text-zinc-500">{$machines.length ? 'No sources match the current filter.' : 'Waiting for source data from /api/stream.'}</div>
		{/if}
	</div>
</main>
