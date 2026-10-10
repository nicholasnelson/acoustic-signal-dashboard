<script lang="ts">
	import { onMount } from 'svelte';
	import Search from '@lucide/svelte/icons/search';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import MachineCard from '$lib/components/dashboard/MachineCard.svelte';
	import { monitoringClient } from '$lib/services/monitoring';
	import type { Machine, MachineStatus } from '$lib/types';

	let machines: Machine[] = [];
	let error = '';
	let loading = true;
	let search = '';
	let status: 'all' | MachineStatus = 'all';
	const statusOptions: Array<'all' | MachineStatus> = ['all', 'ready', 'normal', 'warning', 'anomaly'];

	function setStatus(value: 'all' | MachineStatus) {
		status = value;
	}

	$: analysed = machines.filter((machine) => machine.score !== null);
	$: averageScore = analysed.length
		? analysed.reduce((sum, item) => sum + (item.score ?? 0), 0) / analysed.length
		: 0;
	$: measuredQuality = machines.filter((machine) => machine.signalQuality !== null);
	$: signalQuality = measuredQuality.length
		? measuredQuality.reduce((sum, item) => sum + (item.signalQuality ?? 0), 0) / measuredQuality.length
		: 0;
	$: normalCount = machines.filter((machine) => machine.status === 'normal').length;
	$: warningCount = machines.filter((machine) => machine.status === 'warning').length;
	$: anomalyCount = machines.filter((machine) => machine.status === 'anomaly').length;
	$: readyCount = machines.filter((machine) => machine.status === 'ready').length;
	$: filteredMachines = machines.filter((machine) => {
		const statusMatch = status === 'all' || machine.status === status;
		const term = search.trim().toLowerCase();
		const searchMatch = !term || machine.name.toLowerCase().includes(term) || machine.id.toLowerCase().includes(term);
		return statusMatch && searchMatch;
	});

	onMount(async () => {
		try {
			machines = await monitoringClient.getMachines();
		} catch (cause) {
			error = cause instanceof Error ? cause.message : 'Unable to load machines.';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head><title>Machines · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={machines.length} {averageScore} {signalQuality} />

		<section class="flex flex-col gap-3 border-b border-white/10 pb-4 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<h2 class="text-xl font-semibold tracking-tight text-zinc-100">Machines</h2>
				<p class="mt-1 text-xs text-zinc-500">Open each MIMII fan to inspect normal or abnormal recordings and detector output.</p>
			</div>
			<div class="flex flex-wrap items-center gap-2 text-xs">
				<div class="rounded border border-white/10 px-3 py-2 text-zinc-400">Ready <span class="ml-1 text-zinc-200">{readyCount}</span></div>
				<div class="rounded border border-white/10 px-3 py-2 text-zinc-400">Normal <span class="ml-1 text-emerald-400">{normalCount}</span></div>
				<div class="rounded border border-white/10 px-3 py-2 text-zinc-400">Warning <span class="ml-1 text-amber-400">{warningCount}</span></div>
				<div class="rounded border border-white/10 px-3 py-2 text-zinc-400">Anomaly <span class="ml-1 text-rose-400">{anomalyCount}</span></div>
			</div>
		</section>

		<section class="grid gap-3 rounded border border-white/10 bg-[#101014]/90 p-4 md:grid-cols-[1fr_auto]">
			<label class="relative block">
				<Search size={16} class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600" />
				<input bind:value={search} placeholder="Search fan ID" class="min-h-11 w-full rounded border border-white/10 bg-[#15151b] pl-9 pr-3 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-violet-500/50" />
			</label>
			<div class="flex flex-wrap items-center gap-2">
				{#each statusOptions as item}
					<button type="button" on:click={() => setStatus(item)} class={`min-h-11 rounded border px-3 text-xs font-medium capitalize transition ${status === item ? 'border-violet-500/30 bg-violet-500/10 text-violet-300' : 'border-white/10 text-zinc-500 hover:bg-white/[0.04] hover:text-zinc-200'}`}>{item}</button>
				{/each}
			</div>
		</section>

		{#if error}
			<div class="rounded border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">{error}</div>
		{:else if loading}
			<div class="rounded border border-white/10 bg-[#101014]/90 p-6 text-sm text-zinc-500">Loading machines…</div>
		{:else if filteredMachines.length}
			<section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
				{#each filteredMachines as machine}
					<MachineCard {machine} />
				{/each}
			</section>
		{:else}
			<div class="rounded border border-white/10 bg-[#101014]/90 p-8 text-center text-sm text-zinc-500">No machines match the current filter.</div>
		{/if}
	</div>
</main>
