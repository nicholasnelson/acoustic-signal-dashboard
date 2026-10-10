<script lang="ts">
	import { onMount } from 'svelte';
	import Search from '@lucide/svelte/icons/search';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import AlertCard from '$lib/components/dashboard/AlertCard.svelte';
	import { monitoringClient } from '$lib/services/monitoring';
	import type { AlertEvent, Machine } from '$lib/types';

	let events: AlertEvent[] = [];
	let machines: Machine[] = [];
	let error = '';
	let severity: 'all' | 'critical' | 'warning' | 'info' = 'all';
	let machineId = 'all';
	let search = '';
	const severityOptions = ['all', 'critical', 'warning', 'info'] as const;

	function setSeverity(value: (typeof severityOptions)[number]) {
		severity = value;
	}

	$: criticalCount = events.filter((event) => event.severity === 'critical').length;
	$: warningCount = events.filter((event) => event.severity === 'warning').length;
	$: analysed = machines.filter((machine) => machine.score !== null);
	$: averageScore = analysed.length
		? analysed.reduce((sum, machine) => sum + (machine.score ?? 0), 0) / analysed.length
		: 0;
	$: quality = machines.filter((machine) => machine.signalQuality !== null);
	$: signalQuality = quality.length
		? quality.reduce((sum, machine) => sum + (machine.signalQuality ?? 0), 0) / quality.length
		: 0;
	$: filteredEvents = events.filter((event) => {
		const severityMatch = severity === 'all' || event.severity === severity;
		const machineMatch = machineId === 'all' || event.machineId === machineId;
		const term = search.trim().toLowerCase();
		const searchMatch =
			!term ||
			event.machineName.toLowerCase().includes(term) ||
			event.title.toLowerCase().includes(term) ||
			event.message.toLowerCase().includes(term);
		return severityMatch && machineMatch && searchMatch;
	});

	onMount(async () => {
		try {
			[events, machines] = await Promise.all([
				monitoringClient.getEvents(),
				monitoringClient.getMachines()
			]);
		} catch (cause) {
			error = cause instanceof Error ? cause.message : 'Unable to load detector events.';
		}
	});
</script>

<svelte:head><title>Alerts · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={machines.length} {averageScore} {signalQuality} />

		<section class="flex flex-col gap-4 pt-1 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<h2 class="text-xl font-semibold tracking-tight text-zinc-100">Alert history</h2>
				<p class="mt-1 max-w-2xl text-xs leading-relaxed text-zinc-500">
					Click any alert to inspect the detector score, threshold, analysis window and related fan.
				</p>
			</div>
			<div class="flex items-center gap-2">
				<div class="rounded border border-rose-500/15 bg-rose-500/10 px-3 py-2"><span class="text-xs text-zinc-500">Critical</span><span class="ml-2 text-sm font-semibold text-rose-400">{criticalCount}</span></div>
				<div class="rounded border border-amber-500/15 bg-amber-500/10 px-3 py-2"><span class="text-xs text-zinc-500">Warning</span><span class="ml-2 text-sm font-semibold text-amber-400">{warningCount}</span></div>
			</div>
		</section>

		{#if error}
			<div class="rounded border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">{error}</div>
		{/if}

		<section class="grid gap-3 rounded border border-white/10 bg-[#101014]/90 p-4 md:grid-cols-[1fr_180px_auto]">
			<label class="relative block">
				<Search size={16} class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600" />
				<input bind:value={search} placeholder="Search alerts" class="min-h-11 w-full rounded border border-white/10 bg-[#15151b] pl-9 pr-3 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-violet-500/50" />
			</label>
			<select bind:value={machineId} class="min-h-11 rounded border border-white/10 bg-[#15151b] px-3 text-sm text-zinc-200 outline-none focus:border-violet-500/50">
				<option value="all">All machines</option>
				{#each machines as machine}
					<option value={machine.id}>{machine.name}</option>
				{/each}
			</select>
			<div class="flex flex-wrap items-center gap-2">
				{#each severityOptions as item}
					<button type="button" on:click={() => setSeverity(item)} class={`min-h-11 rounded border px-3 text-xs font-medium capitalize transition ${severity === item ? 'border-violet-500/30 bg-violet-500/10 text-violet-300' : 'border-white/10 text-zinc-500 hover:bg-white/[0.04] hover:text-zinc-200'}`}>{item}</button>
				{/each}
			</div>
		</section>

		<section class="rounded border border-white/10 bg-[#101014]/90">
			<div class="border-b border-white/10 px-4 py-4 sm:px-5">
				<h3 class="text-sm font-medium text-zinc-100">Detector events</h3>
				<p class="mt-1 text-xs text-zinc-500">Showing {filteredEvents.length} of {events.length} events in the current dashboard history</p>
			</div>
			<div class="space-y-2 p-3 sm:p-4">
				{#if filteredEvents.length}
					{#each filteredEvents as event}
						<AlertCard {event} />
					{/each}
				{:else}
					<p class="py-6 text-center text-sm text-zinc-500">No alerts match the current filters.</p>
				{/if}
			</div>
		</section>
	</div>
</main>
