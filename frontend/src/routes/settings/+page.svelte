<script lang="ts">
	import { onMount } from 'svelte';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import Save from '@lucide/svelte/icons/save';
	import Server from '@lucide/svelte/icons/server';

	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import { monitoringClient } from '$lib/services/monitoring';
	import {
		getDashboardPreferences,
		resetDashboardPreferences,
		saveDashboardPreferences,
		type DashboardPreferences
	} from '$lib/services/preferences';
	import type { BackendHealth, Machine } from '$lib/types';

	let machines: Machine[] = [];
	let health: BackendHealth | null = null;
	let error = '';
	let saved = false;
	let preferences: DashboardPreferences = {
		recentAlertLimit: 3,
		showTechnicalDetails: true,
		autoAnalyseOnOpen: true
	};

	function savePreferences() {
		preferences.autoAnalyseOnOpen = true;
		saveDashboardPreferences(preferences);
		saved = true;
		window.setTimeout(() => (saved = false), 1800);
	}

	function resetPreferences() {
		preferences = resetDashboardPreferences();
		saved = true;
		window.setTimeout(() => (saved = false), 1800);
	}

	onMount(async () => {
		preferences = getDashboardPreferences();
		try {
			[machines, health] = await Promise.all([
				monitoringClient.getMachines(),
				monitoringClient.getHealth()
			]);
		} catch (cause) {
			error = cause instanceof Error ? cause.message : 'Unable to load pipeline settings.';
		}
	});
</script>

<svelte:head><title>Settings · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={machines.length} averageScore={0} signalQuality={0} showScore={false} />

		<section class="flex flex-col gap-2 pt-1 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<h2 class="text-xl font-semibold tracking-tight text-zinc-100">Settings</h2>
				<p class="mt-1 text-xs text-zinc-500">Simple dashboard options for the monitoring interface.</p>
			</div>
			<div class={`flex w-fit items-center gap-2 rounded border px-3 py-2 text-xs ${health ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400' : 'border-rose-500/20 bg-rose-500/10 text-rose-400'}`}>
				<Server size={15} />{health ? `Backend connected${health.version ? ` · v${health.version}` : ''}` : 'Backend unavailable'}
			</div>
		</section>

		{#if error}
			<div class="rounded border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">{error}</div>
		{/if}

		<Panel title="Dashboard preferences" subtitle="Interface options">
			<div class="grid gap-5 lg:grid-cols-2">
				<div class="rounded border border-emerald-500/15 bg-emerald-500/[0.04] p-4">
					<div class="flex items-start justify-between gap-4">
						<div>
							<p class="text-sm font-medium text-zinc-200">Automatic replay analysis</p>
							<p class="mt-1 text-xs leading-5 text-zinc-500">Opening a fan, switching Normal/Abnormal, or selecting another clip automatically runs the detector.</p>
						</div>
						<span class="rounded bg-emerald-500/10 px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-emerald-400">Enabled</span>
					</div>
				</div>
				<label class="rounded border border-white/10 bg-white/[0.02] p-4">
					<p class="text-sm font-medium text-zinc-200">Overview alert count</p>
					<p class="mt-1 text-xs leading-5 text-zinc-500">How many recent alerts appear on the overview page.</p>
					<select bind:value={preferences.recentAlertLimit} class="mt-3 min-h-10 w-full rounded border border-white/10 bg-[#15151b] px-3 text-sm text-zinc-200 outline-none focus:border-violet-500/50">
						<option value={3}>3 alerts</option>
						<option value={5}>5 alerts</option>
						<option value={10}>10 alerts</option>
					</select>
				</label>
			</div>
			<div class="mt-5 flex flex-wrap items-center gap-2 border-t border-white/10 pt-4">
				<button type="button" on:click={savePreferences} class="flex min-h-11 items-center gap-2 rounded bg-violet-600 px-4 text-sm font-medium text-white transition hover:bg-violet-500"><Save size={16} />Save dashboard settings</button>
				<button type="button" on:click={resetPreferences} class="flex min-h-11 items-center gap-2 rounded border border-white/10 px-4 text-sm font-medium text-zinc-400 transition hover:bg-white/[0.04] hover:text-zinc-200"><RotateCcw size={16} />Reset</button>
				{#if saved}<span class="text-xs text-emerald-400">Settings saved</span>{/if}
			</div>
		</Panel>

	</div>
</main>
