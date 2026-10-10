<script lang="ts">
	import { onMount } from 'svelte';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';

	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import AlertCard from '$lib/components/dashboard/AlertCard.svelte';
	import MachineCard from '$lib/components/dashboard/MachineCard.svelte';
	import { alerts, machines, startMonitoring, streamState } from '$lib/services/monitoring';
	import { getDashboardPreferences } from '$lib/services/preferences';

	let recentAlertLimit = 3;

	$: scored = $machines.filter((machine) => machine.score !== null);
	$: averageScore = scored.length ? scored.reduce((sum, machine) => sum + (machine.score ?? 0), 0) / scored.length : null;
	$: normalCount = $machines.filter((machine) => machine.status === 'normal').length;
	$: anomalyCount = $machines.filter((machine) => machine.status === 'anomaly').length;
	$: calibratingCount = $machines.filter((machine) => machine.status === 'calibrating').length;
	$: sortedMachines = [...$machines].sort((a, b) => {
		const rank: Record<string, number> = { anomaly: 0, calibrating: 1, normal: 2, unavailable: 3 };
		const difference = (rank[a.status] ?? 99) - (rank[b.status] ?? 99);
		return difference !== 0 ? difference : a.name.localeCompare(b.name);
	});

	onMount(() => {
		recentAlertLimit = getDashboardPreferences().recentAlertLimit;
		startMonitoring();
	});
</script>

<svelte:head>
	<title>Overview · Acoustic Monitoring</title>
	<meta name="description" content="Live acoustic condition-monitoring dashboard" />
</svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={$machines.length} {averageScore} />

		<section class="flex flex-col gap-3 pt-1 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<h1 class="text-xl font-semibold tracking-tight text-zinc-100 sm:text-2xl">System overview</h1>
				<p class="mt-1 text-sm text-zinc-500">Live source activity and alerts from the backend stream.</p>
			</div>
			
		</section>

		<Panel
			title="Recent alerts"
			subtitle={$alerts.length ? `${$alerts.length} alert ${$alerts.length === 1 ? 'event' : 'events'} available to review` : 'No alert events have been generated yet'}
			className={anomalyCount > 0 ? 'border-rose-500/20' : ''}
			contentClass={$alerts.length ? 'space-y-2' : 'py-4'}
		>
			<a slot="action" href="/alerts" class="inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-white/[0.08] px-3 text-xs font-medium text-zinc-400 transition hover:border-violet-500/25 hover:text-violet-300">View all<ChevronRight size={14} strokeWidth={1.8} /></a>
			{#if $alerts.length}
				{#each $alerts.slice(0, recentAlertLimit) as event}<AlertCard {event} />{/each}
			{:else}
				<div class="flex items-center justify-between gap-4"><p class="text-sm text-zinc-500">Waiting for a source to cross its alert level.</p><a href="/machines" class="text-xs font-medium text-violet-300 hover:text-violet-200">Open machines</a></div>
			{/if}
		</Panel>

		<section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
			<a href="/alerts" class={`rounded-xl border bg-white/[0.025] p-4 transition hover:bg-white/[0.04] ${anomalyCount > 0 ? 'border-rose-500/25 hover:border-rose-500/40' : 'border-white/[0.08] hover:border-white/[0.12]'}`}>
				<p class="text-xs font-medium text-zinc-500">Alert</p><p class={`mt-3 text-2xl font-semibold ${anomalyCount > 0 ? 'text-rose-400' : 'text-zinc-100'}`}>{anomalyCount}</p><p class="mt-1 text-xs text-zinc-600">Sources currently above the learned threshold</p>
			</a>
			<a href="/machines" class="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4 transition hover:border-violet-500/25 hover:bg-white/[0.04]">
				<p class="text-xs font-medium text-zinc-500">Calibrating</p><p class="mt-3 text-2xl font-semibold text-violet-300">{calibratingCount}</p><p class="mt-1 text-xs text-zinc-600">Learning an initial normal baseline</p>
			</a>
			<a href="/machines" class="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4 transition hover:border-emerald-500/25 hover:bg-white/[0.04]">
				<p class="text-xs font-medium text-zinc-500">Normal</p><p class="mt-3 text-2xl font-semibold text-zinc-100">{normalCount}</p><p class="mt-1 text-xs text-zinc-600">Current score is below the alert level</p>
			</a>
			<a href="/machines" class="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4 transition hover:border-violet-500/25 hover:bg-white/[0.04]">
				<p class="text-xs font-medium text-zinc-500">Live sources</p><p class="mt-3 text-2xl font-semibold text-zinc-100">{$machines.length}</p><p class="mt-1 text-xs text-zinc-600">Sources discovered from /api/stream</p>
			</a>
		</section>

		<section>
			<div class="mb-2 flex items-end justify-between gap-3">
				<div><h2 class="text-base font-semibold tracking-tight text-zinc-100">Machines</h2><p class="mt-1 text-xs text-zinc-500">Alerting sources are shown first. Open a source for its live score trend and event history.</p></div>
				<a href="/machines" class="inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-white/[0.08] px-3 text-xs font-medium text-zinc-400 transition hover:border-violet-500/25 hover:text-violet-300">View all<ChevronRight size={14} strokeWidth={1.8} /></a>
			</div>

			{#if sortedMachines.length}
				<div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{#each sortedMachines as machine}<MachineCard {machine} />{/each}</div>
			{:else}
				<div class="rounded border border-white/10 bg-[#101014]/90 p-6 text-sm text-zinc-500">Waiting for the backend runner to publish source data. Start the device server and FastAPI with a sources config.</div>
			{/if}
		</section>
	</div>
</main>
