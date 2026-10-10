<script lang="ts">
	import { onMount } from 'svelte';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Clock from '@lucide/svelte/icons/clock';
	import Fan from '@lucide/svelte/icons/fan';
	import Gauge from '@lucide/svelte/icons/gauge';
	import Activity from '@lucide/svelte/icons/activity';

	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import KpiCard from '$lib/components/ui/KpiCard.svelte';
	import { alerts, machines, startMonitoring } from '$lib/services/monitoring';

	export let data: { id: string };
	$: event = $alerts.find((item) => item.id === data.id) ?? null;
	$: machine = event ? $machines.find((item) => item.id === event.machineId) ?? null : null;

	onMount(startMonitoring);
</script>

<svelte:head><title>{event?.title ?? 'Alert'} · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={$machines.length} averageScore={machine?.score ?? event?.scoreIndex ?? null} scoreLabel="Detection score" />
		<a href="/alerts" class="flex w-fit items-center gap-2 text-sm text-zinc-500 transition hover:text-zinc-200"><ArrowLeft size={17} />Back to alerts</a>

		{#if !event}
			<div class="rounded border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">This alert is not available in the current browser history.</div>
		{:else}
			<section class="flex flex-col gap-4 rounded border border-rose-500/20 bg-rose-500/[0.04] p-5 sm:p-6 lg:flex-row lg:items-center lg:justify-between">
				<div><div class="mb-3 inline-flex items-center gap-2 rounded bg-rose-500/10 px-2.5 py-1 text-[11px] font-medium uppercase tracking-wide text-rose-400"><span class="size-1.5 rounded-full bg-current"></span>alert</div><h1 class="text-xl font-semibold text-zinc-100 sm:text-2xl">{event.title}</h1><p class="mt-2 max-w-3xl text-sm leading-6 text-zinc-500">{event.message}</p></div>
				<a href={`/machines/${event.machineId}`} class="group flex min-h-11 items-center gap-2 rounded bg-violet-600 px-4 text-sm font-medium text-white transition hover:bg-violet-500">Inspect {event.machineName}<ChevronRight size={16} class="transition group-hover:translate-x-0.5" /></a>
			</section>

			<section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
				<KpiCard label="Machine" value={event.machineName} helper={event.machineId} tone="purple" icon={Fan} />
				<KpiCard label="Detection score" value={`${Math.round(event.scoreIndex)}`} helper="alert at 100" tone="red" icon={Gauge} />
				<KpiCard label="Raw score" value={event.score.toFixed(3)} helper="backend output" tone="purple" icon={Activity} />
				<KpiCard label="Threshold" value={event.threshold.toFixed(3)} helper={event.timestamp} tone="purple" icon={Clock} />
			</section>

			<Panel title="Alert details" subtitle="The live detector score crossed the source threshold">
				<div class="grid gap-4 sm:grid-cols-3">
					<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">Recorded</p><p class="mt-1 text-sm font-medium text-zinc-200">{new Date(event.isoTimestamp).toLocaleString()}</p></div>
					<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">Current source state</p><p class="mt-1 text-sm font-medium capitalize text-zinc-200">{machine ? (machine.status === 'anomaly' ? 'alert' : machine.status) : 'waiting'}</p></div>
					<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">Score calculation</p><p class="mt-1 text-sm font-medium text-zinc-200">raw score ÷ threshold × 100</p></div>
				</div>
				<p class="mt-5 border-t border-white/10 pt-4 text-xs leading-5 text-zinc-500">A detection score of 100 is the alert level. The dashboard treats the backend result as an indicator for review, not a confirmed mechanical diagnosis.</p>
			</Panel>
		{/if}
	</div>
</main>
