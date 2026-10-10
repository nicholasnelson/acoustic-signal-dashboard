<script lang="ts">
	import { onMount } from 'svelte';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Clock from '@lucide/svelte/icons/clock';
	import Fan from '@lucide/svelte/icons/fan';
	import Gauge from '@lucide/svelte/icons/gauge';
	import ScanLine from '@lucide/svelte/icons/scan-line';

	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import KpiCard from '$lib/components/ui/KpiCard.svelte';
	import { monitoringClient } from '$lib/services/monitoring';
	import type { AlertEvent, Machine } from '$lib/types';

	export let data: { id: string };

	let event: AlertEvent | null = null;
	let machines: Machine[] = [];
	let loading = true;
	let error = '';

	$: machine = event ? machines.find((item) => item.id === event?.machineId) ?? null : null;
	$: averageScore = machine?.score ?? event?.scoreIndex ?? 0;
	$: signalQuality = machine?.signalQuality ?? 0;
	$: inspectHref = machine
		? `/machines/${machine.id}?label=${machine.lastLabel ?? 'normal'}${machine.lastClip ? `&clip=${encodeURIComponent(machine.lastClip)}` : ''}`
		: event
			? `/machines/${event.machineId}`
			: '/machines';

	onMount(async () => {
		try {
			const [events, machineList] = await Promise.all([
				monitoringClient.getEvents(),
				monitoringClient.getMachines()
			]);
			machines = machineList;
			event = events.find((item) => item.id === data.id) ?? null;
			if (!event) error = 'This detector event is no longer available in the current dashboard history.';
		} catch (cause) {
			error = cause instanceof Error ? cause.message : 'Unable to load alert details.';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head><title>{event?.title ?? 'Alert'} · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={machines.length} {averageScore} {signalQuality} scoreLabel="Detection score" />

		<a href="/alerts" class="flex w-fit items-center gap-2 text-sm text-zinc-500 transition hover:text-zinc-200"><ArrowLeft size={17} />Back to alerts</a>

		{#if loading}
			<div class="rounded border border-white/10 bg-[#101014]/90 p-6 text-sm text-zinc-500">Loading alert…</div>
		{:else if error}
			<div class="rounded border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">{error}</div>
		{:else if event}
			<section class="flex flex-col gap-4 rounded border border-white/10 bg-[#101014]/90 p-5 sm:p-6 lg:flex-row lg:items-center lg:justify-between">
				<div>
					<div class={`mb-3 inline-flex items-center gap-2 rounded px-2.5 py-1 text-[11px] font-medium uppercase tracking-wide ${event.severity === 'critical' ? 'bg-rose-500/10 text-rose-400' : event.severity === 'warning' ? 'bg-amber-500/10 text-amber-400' : 'bg-violet-500/10 text-violet-300'}`}>
						<span class="size-1.5 rounded-full bg-current"></span>{event.severity}
					</div>
					<h1 class="text-xl font-semibold text-zinc-100 sm:text-2xl">{event.title}</h1>
					<p class="mt-2 max-w-3xl text-sm leading-6 text-zinc-500">{event.message}</p>
				</div>
				<a href={inspectHref} class="group flex min-h-11 items-center gap-2 rounded bg-violet-600 px-4 text-sm font-medium text-white transition hover:bg-violet-500">
					Inspect {event.machineName}<ChevronRight size={16} class="transition group-hover:translate-x-0.5" />
				</a>
			</section>

			<section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
				<KpiCard label="Machine" value={event.machineName} helper={event.machineId} tone="purple" icon={Fan} />
				<KpiCard label="Window" value={event.windowIndex === null ? '—' : `${event.windowIndex}`} helper="analysis window index" tone="purple" icon={ScanLine} />
				<KpiCard label="Distance" value={event.score.toFixed(2)} helper={`threshold ${event.threshold.toFixed(2)}`} tone={event.severity === 'critical' ? 'red' : 'orange'} icon={Gauge} />
				<KpiCard label="Detection score" value={`${Math.round(event.scoreIndex)}`} helper="alert at 100" tone={event.severity === 'critical' ? 'red' : 'orange'} icon={Clock} />
			</section>

			<section class="grid gap-3 xl:grid-cols-[minmax(0,1fr)_360px]">
				<Panel title="Alert details" subtitle="Detector threshold event used to support review; it is not a final equipment diagnosis">
					<div class="grid gap-4 sm:grid-cols-2">
						<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">Learned threshold</p><p class="mt-1 text-lg font-semibold text-zinc-100">{event.threshold.toFixed(4)}</p></div>
						<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">Detection score</p><p class="mt-1 text-lg font-semibold text-zinc-100">{event.scoreIndex.toFixed(1)}</p></div>
						<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">Recorded</p><p class="mt-1 text-sm font-medium text-zinc-200">{event.timestamp}</p></div>
					</div>
					<p class="mt-5 border-t border-white/10 pt-4 text-xs leading-5 text-zinc-500">A detection score of 100 is the alert level. Higher values indicate a stronger difference from the normal baseline.</p>
				</Panel>

				<Panel title="Related fan" subtitle="Open the latest analysed clip for this source">
					<div class="space-y-3">
						<div class="flex items-center justify-between"><span class="text-xs text-zinc-500">Machine</span><span class="text-sm font-medium text-zinc-200">{event.machineName}</span></div>
						<div class="flex items-center justify-between"><span class="text-xs text-zinc-500">Last clip</span><span class="text-xs font-medium text-zinc-300">{machine?.lastClip ?? '—'}</span></div>
						<div class="flex items-center justify-between"><span class="text-xs text-zinc-500">Dataset label</span><span class="text-xs font-medium capitalize text-zinc-300">{machine?.lastLabel ?? '—'}</span></div>
						<a href={inspectHref} class="mt-3 flex min-h-11 items-center justify-between border-t border-white/10 pt-4 text-xs font-medium text-zinc-400 transition hover:text-violet-300"><span>Open full machine analysis</span><ChevronRight size={16} /></a>
					</div>
				</Panel>
			</section>
		{/if}
	</div>
</main>
