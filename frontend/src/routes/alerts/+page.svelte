<script lang="ts">
	import { onMount } from 'svelte';
	import Search from '@lucide/svelte/icons/search';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import AlertCard from '$lib/components/dashboard/AlertCard.svelte';
	import { alerts, clearAlertHistory, machines, startMonitoring } from '$lib/services/monitoring';

	let machineId = 'all';
	let search = '';

	$: scored = $machines.filter((machine) => machine.score !== null);
	$: averageScore = scored.length ? scored.reduce((sum, machine) => sum + (machine.score ?? 0), 0) / scored.length : null;
	$: filteredEvents = $alerts.filter((event) => {
		const machineMatch = machineId === 'all' || event.machineId === machineId;
		const term = search.trim().toLowerCase();
		const searchMatch = !term || event.machineName.toLowerCase().includes(term) || event.title.toLowerCase().includes(term) || event.message.toLowerCase().includes(term);
		return machineMatch && searchMatch;
	});

	onMount(startMonitoring);
</script>

<svelte:head><title>Alerts · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={$machines.length} {averageScore} />

		<section class="flex flex-col gap-4 pt-1 sm:flex-row sm:items-end sm:justify-between">
			<div><h2 class="text-xl font-semibold tracking-tight text-zinc-100">Alert history</h2><p class="mt-1 max-w-2xl text-xs leading-relaxed text-zinc-500">An alert is stored when a live source moves from below to above its learned threshold.</p></div>
			<button type="button" on:click={clearAlertHistory} disabled={!$alerts.length} class="flex min-h-10 items-center gap-2 rounded border border-white/10 px-3 text-xs font-medium text-zinc-500 transition hover:bg-white/[0.04] hover:text-zinc-200 disabled:cursor-not-allowed disabled:opacity-40"><Trash2 size={15} />Clear history</button>
		</section>

		<section class="grid gap-3 rounded border border-white/10 bg-[#101014]/90 p-4 md:grid-cols-[1fr_220px]">
			<label class="relative block"><Search size={16} class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600" /><input bind:value={search} placeholder="Search alerts" class="min-h-11 w-full rounded border border-white/10 bg-[#15151b] pl-9 pr-3 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-violet-500/50" /></label>
			<select bind:value={machineId} class="min-h-11 rounded border border-white/10 bg-[#15151b] px-3 text-sm text-zinc-200 outline-none focus:border-violet-500/50"><option value="all">All sources</option>{#each $machines as machine}<option value={machine.id}>{machine.name}</option>{/each}</select>
		</section>

		<section class="rounded border border-white/10 bg-[#101014]/90">
			<div class="border-b border-white/10 px-4 py-4 sm:px-5"><h3 class="text-sm font-medium text-zinc-100">Live detector alerts</h3><p class="mt-1 text-xs text-zinc-500">Showing {filteredEvents.length} of {$alerts.length} events stored in this browser</p></div>
			<div class="space-y-2 p-3 sm:p-4">{#if filteredEvents.length}{#each filteredEvents as event}<AlertCard {event} />{/each}{:else}<p class="py-6 text-center text-sm text-zinc-500">No alerts match the current filter.</p>{/if}</div>
		</section>
	</div>
</main>
