<script lang="ts">
	import { onMount } from 'svelte';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Activity from '@lucide/svelte/icons/activity';
	import Gauge from '@lucide/svelte/icons/gauge';
	import Radio from '@lucide/svelte/icons/radio';

	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import KpiCard from '$lib/components/ui/KpiCard.svelte';
	import GaugeChart from '$lib/components/charts/GaugeChart.svelte';
	import TrendChart from '$lib/components/charts/TrendChart.svelte';
	import EventList from '$lib/components/dashboard/EventList.svelte';
	import { alerts, machines, startMonitoring, streamState } from '$lib/services/monitoring';

	export let data: { id: string };

	$: machine = $machines.find((item) => item.id === data.id) ?? null;
	$: machineEvents = $alerts.filter((event) => event.machineId === data.id);
	$: statusLabel = machine?.status === 'anomaly' ? 'Alert' : machine?.status === 'normal' ? 'Normal' : machine?.status === 'calibrating' ? 'Calibrating' : 'Waiting';
	$: statusClass = machine?.status === 'anomaly' ? 'bg-rose-500/10 text-rose-400' : machine?.status === 'normal' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-violet-500/10 text-violet-300';

	onMount(startMonitoring);
</script>

<svelte:head><title>{machine?.name ?? data.id} · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={$machines.length} averageScore={machine?.score ?? null} scoreLabel="Detection score" />
		<a href="/machines" class="flex w-fit items-center gap-2 text-sm text-zinc-500 hover:text-zinc-200"><ArrowLeft size={17} />Back to machines</a>

		<section class="flex flex-col gap-3 rounded border border-white/10 bg-[#101014]/90 p-5 sm:p-6 lg:flex-row lg:items-center lg:justify-between">
			<div>
				<div class="flex flex-wrap items-center gap-2"><h2 class="text-xl font-semibold text-zinc-100">{machine?.name ?? data.id}</h2><div class={`flex items-center gap-1.5 rounded px-2 py-1 text-[11px] font-medium ${statusClass}`}><span class="size-1.5 rounded-full bg-current"></span>{statusLabel}</div></div>
				<p class="mt-1 text-xs text-zinc-500">Live source · {data.id} · backend /api/stream</p>
			</div>
			<div class={`w-fit rounded-lg border px-3 py-2 text-xs ${$streamState === 'connected' ? 'border-emerald-500/20 text-emerald-400' : 'border-rose-500/20 text-rose-400'}`}>{$streamState === 'connected' ? 'Stream connected' : 'Stream disconnected'}</div>
		</section>

		{#if !machine}
			<div class="rounded border border-white/10 bg-[#101014]/90 p-6 text-sm text-zinc-500">Waiting for this source to publish its first event. Check the source ID in the backend sources config.</div>
		{:else if machine.status === 'calibrating'}
			<Panel title="Calibration" subtitle="The backend is learning the initial normal baseline for this source">
				<div class="flex items-end justify-between gap-4"><div><p class="text-4xl font-semibold text-zinc-100">{Math.round((machine.calibrationProgress ?? 0) * 100)}%</p><p class="mt-2 text-sm text-zinc-500">The detector becomes active after the configured calibration windows are collected.</p></div><Activity size={34} class="text-violet-400" /></div>
				<progress value={(machine.calibrationProgress ?? 0) * 100} max="100" class="mt-5 h-2 w-full appearance-none overflow-hidden rounded bg-zinc-800 [&::-webkit-progress-bar]:bg-zinc-800 [&::-webkit-progress-value]:bg-violet-500 [&::-moz-progress-bar]:bg-violet-500" />
			</Panel>
		{:else}
			<section class="grid gap-3 sm:grid-cols-3">
				<KpiCard label="Detection score" value={machine.score === null ? '—' : `${Math.round(machine.score)}`} helper="alert at 100" tone={machine.status === 'anomaly' ? 'red' : 'purple'} icon={Gauge} />
				<KpiCard label="Raw score" value={machine.rawScore === null ? '—' : machine.rawScore.toFixed(3)} helper="backend detector output" tone="purple" icon={Activity} />
				<KpiCard label="Threshold" value={machine.threshold === null ? '—' : machine.threshold.toFixed(3)} helper="learned from calibration" tone="purple" icon={Radio} />
			</section>

			<section class="grid gap-3 xl:grid-cols-[300px_minmax(0,1fr)]">
				<Panel title="Alert level" subtitle="Detection score is raw score divided by threshold × 100"><GaugeChart value={machine.score ?? 0} threshold={100} label="Detection score" height="260px" /></Panel>
				<Panel title="Live score trend" subtitle="Recent detector output from this source"><TrendChart values={machine.history} threshold={100} height="300px" /></Panel>
			</section>

			<section class="grid gap-3 xl:grid-cols-[minmax(0,1fr)_360px]">
				<Panel title="Source state" subtitle="Current information received from the backend runner">
					<div class="grid gap-4 sm:grid-cols-2">
						<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">Source ID</p><p class="mt-1 text-sm font-medium text-zinc-200">{machine.id}</p></div>
						<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">State</p><p class="mt-1 text-sm font-medium capitalize text-zinc-200">{machine.status === 'anomaly' ? 'alert' : machine.status}</p></div>
						<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">Last update</p><p class="mt-1 text-sm font-medium text-zinc-200">{machine.lastUpdate ? new Date(machine.lastUpdate).toLocaleString() : '—'}</p></div>
						<div><p class="text-[11px] uppercase tracking-wide text-zinc-600">History points</p><p class="mt-1 text-sm font-medium text-zinc-200">{machine.history.length}</p></div>
					</div>
				</Panel>
				<Panel title="Machine events" subtitle="Alert transitions recorded in this browser">{#if machineEvents.length}<EventList events={machineEvents.slice(0, 8)} />{:else}<div class="flex min-h-40 items-center justify-center"><p class="text-sm text-zinc-500">No alert events for this source yet.</p></div>{/if}</Panel>
			</section>
		{/if}
	</div>
</main>
