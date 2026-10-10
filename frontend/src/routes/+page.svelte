<script lang="ts">
	import { onMount } from 'svelte';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';

	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import AlertCard from '$lib/components/dashboard/AlertCard.svelte';
	import MachineCard from '$lib/components/dashboard/MachineCard.svelte';
	import { monitoringClient } from '$lib/services/monitoring';
	import { getDashboardPreferences } from '$lib/services/preferences';
	import type { AlertEvent, Machine } from '$lib/types';

	let machines: Machine[] = [];
	let events: AlertEvent[] = [];
	let loading = true;
	let error = '';
	let recentAlertLimit = 3;

	$: scored = machines.filter((machine) => machine.score !== null);
	$: qualityMeasured = machines.filter((machine) => machine.signalQuality !== null);
	$: averageScore = scored.length
		? scored.reduce((sum, machine) => sum + (machine.score ?? 0), 0) / scored.length
		: 0;
	$: signalQuality = qualityMeasured.length
		? qualityMeasured.reduce((sum, machine) => sum + (machine.signalQuality ?? 0), 0) /
			qualityMeasured.length
		: 0;

	$: normalCount = machines.filter((machine) => machine.status === 'normal').length;
	$: warningCount = machines.filter((machine) => machine.status === 'warning').length;
	$: anomalyCount = machines.filter((machine) => machine.status === 'anomaly').length;
	$: readyCount = machines.filter((machine) => machine.status === 'ready').length;
	$: attentionCount = warningCount + anomalyCount;

	$: sortedMachines = [...machines].sort((a, b) => {
		const rank: Record<string, number> = {
			anomaly: 0,
			warning: 1,
			ready: 2,
			normal: 3,
			unavailable: 4
		};

		const severityDifference = (rank[a.status] ?? 99) - (rank[b.status] ?? 99);
		if (severityDifference !== 0) return severityDifference;
		return a.name.localeCompare(b.name);
	});

	async function refreshDashboard(showLoader = false) {
		if (showLoader) loading = true;

		try {
			const [nextMachines, nextEvents] = await Promise.all([
				monitoringClient.getMachines(),
				monitoringClient.getEvents()
			]);
			machines = nextMachines;
			events = nextEvents;
			error = '';
		} catch (cause) {
			error = cause instanceof Error ? cause.message : 'Unable to load backend data.';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		recentAlertLimit = getDashboardPreferences().recentAlertLimit;
		void refreshDashboard(true);

		const timer = window.setInterval(() => {
			void refreshDashboard(false);
		}, 2000);

		const refreshOnFocus = () => void refreshDashboard(false);
		const refreshOnVisibility = () => {
			if (document.visibilityState === 'visible') void refreshDashboard(false);
		};

		window.addEventListener('focus', refreshOnFocus);
		document.addEventListener('visibilitychange', refreshOnVisibility);

		return () => {
			window.clearInterval(timer);
			window.removeEventListener('focus', refreshOnFocus);
			document.removeEventListener('visibilitychange', refreshOnVisibility);
		};
	});
</script>

<svelte:head>
	<title>Overview · Acoustic Monitoring</title>
	<meta name="description" content="Acoustic condition-monitoring research dashboard" />
</svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={machines.length} {averageScore} {signalQuality} />

		<section class="flex flex-col gap-3 pt-1 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<h1 class="text-xl font-semibold tracking-tight text-zinc-100 sm:text-2xl">System overview</h1>
				<p class="mt-1 text-sm text-zinc-500">
					Machine activity and alerts at a glance.
				</p>
			</div>

			<a
				href="/settings"
				class="flex min-h-10 w-fit items-center gap-2 rounded-xl border border-white/[0.08] px-3 text-xs font-medium text-zinc-400 transition hover:bg-white/[0.05] hover:text-zinc-200 active:scale-[0.98]"
			>
				<SlidersHorizontal size={15} strokeWidth={1.8} />
				Pipeline settings
			</a>
		</section>

		{#if error}
			<div class="rounded border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">
				{error}<br />
				<span class="text-xs text-rose-300/70">Start FastAPI and check that data/6_dB/fan exists.</span>
			</div>
		{/if}

		<!-- Alerts are intentionally first: an operator should see exceptions before normal state. -->
		<Panel
			title="Recent alerts"
			subtitle={events.length
				? `${events.length} detector ${events.length === 1 ? 'event' : 'events'} available to review`
				: 'No detector alerts have been generated in this session'}
			className={anomalyCount > 0
				? 'border-rose-500/20'
				: warningCount > 0
					? 'border-amber-500/20'
					: ''}
			contentClass={events.length ? 'space-y-2' : 'py-4'}
		>
			<a
				slot="action"
				href="/alerts"
				class="inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-white/[0.08] px-3 text-xs font-medium text-zinc-400 transition hover:border-violet-500/25 hover:text-violet-300"
			>
				View all
				<ChevronRight size={14} strokeWidth={1.8} />
			</a>

			{#if events.length}
				{#each events.slice(0, recentAlertLimit) as event}
					<AlertCard {event} />
				{/each}
			{:else}
				<div class="flex items-center justify-between gap-4">
					<p class="text-sm text-zinc-500">No detector alerts yet.</p>
					<a href="/machines" class="text-xs font-medium text-violet-300 hover:text-violet-200">
						Open machines
					</a>
				</div>
			{/if}
		</Panel>

		<!-- Critical state is first; anomaly count gains visual salience only when non-zero. -->
		<section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
			<a
				href="/alerts"
				class={`rounded-xl border bg-white/[0.025] p-4 transition hover:bg-white/[0.04] ${
					anomalyCount > 0
						? 'border-rose-500/25 hover:border-rose-500/40'
						: 'border-white/[0.08] hover:border-white/[0.12]'
				}`}
			>
				<p class="text-xs font-medium text-zinc-500">Alert</p>
				<p class={`mt-3 text-2xl font-semibold ${anomalyCount > 0 ? 'text-rose-400' : 'text-zinc-100'}`}>
					{anomalyCount}
				</p>
				<p class="mt-1 text-xs text-zinc-600">Detection score crossed the alert level</p>
			</a>

			<a
				href="/alerts"
				class="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4 transition hover:border-amber-500/25 hover:bg-white/[0.04]"
			>
				<p class="text-xs font-medium text-zinc-500">Warning</p>
				<p class={`mt-3 text-2xl font-semibold ${warningCount > 0 ? 'text-amber-300' : 'text-zinc-100'}`}>
					{warningCount}
				</p>
				<p class="mt-1 text-xs text-zinc-600">At least one window exceeded</p>
			</a>

			<a
				href="/machines"
				class="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4 transition hover:border-emerald-500/25 hover:bg-white/[0.04]"
			>
				<p class="text-xs font-medium text-zinc-500">Within threshold</p>
				<p class="mt-3 text-2xl font-semibold text-zinc-100">{normalCount}</p>
				<p class="mt-1 text-xs text-zinc-600">No alert detected in the current analysis</p>
			</a>

			<a
				href="/machines"
				class="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4 transition hover:border-violet-500/25 hover:bg-white/[0.04]"
			>
				<p class="text-xs font-medium text-zinc-500">Total machines</p>
				<p class="mt-3 text-2xl font-semibold text-zinc-100">{machines.length}</p>
				<p class="mt-1 text-xs text-zinc-600">{readyCount} not analysed this session</p>
			</a>
		</section>

		<section>
			<div class="mb-2 flex items-end justify-between gap-3">
				<div>
					<h2 class="text-base font-semibold tracking-tight text-zinc-100">Machines</h2>
					<p class="mt-1 text-xs text-zinc-500">
						Alerting machines are shown first. Select a fan for waveform, features, score and events.
					</p>
				</div>

				<div class="flex items-center gap-2">
					{#if attentionCount > 0}
						<a
							href="/alerts"
							class={`hidden rounded-lg border px-3 py-2 text-xs font-medium transition sm:block ${
								anomalyCount > 0
									? 'border-rose-400/15 bg-rose-400/[0.06] text-rose-300 hover:bg-rose-400/[0.1]'
									: 'border-amber-400/15 bg-amber-400/[0.06] text-amber-300 hover:bg-amber-400/[0.1]'
							}`}
						>
							{attentionCount} {attentionCount === 1 ? 'machine requires' : 'machines require'} attention
						</a>
					{/if}

					<a
						href="/machines"
						class="inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-white/[0.08] px-3 text-xs font-medium text-zinc-400 transition hover:border-violet-500/25 hover:text-violet-300"
					>
						View all
						<ChevronRight size={14} strokeWidth={1.8} />
					</a>
				</div>
			</div>

			{#if loading}
				<div class="rounded border border-white/10 bg-[#101014]/90 p-6 text-sm text-zinc-500">
					Loading machines…
				</div>
			{:else if sortedMachines.length}
				<div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
					{#each sortedMachines as machine}
						<MachineCard {machine} />
					{/each}
				</div>
			{/if}
		</section>
	</div>
</main>
