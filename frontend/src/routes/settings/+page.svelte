<script lang="ts">
	import { onMount } from 'svelte';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import Save from '@lucide/svelte/icons/save';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import { machines, startMonitoring, streamState } from '$lib/services/monitoring';
	import { getDashboardPreferences, resetDashboardPreferences, saveDashboardPreferences, type DashboardPreferences } from '$lib/services/preferences';

	let preferences: DashboardPreferences = getDashboardPreferences();
	let saved = false;

	function savePreferences() {
		saveDashboardPreferences(preferences);
		saved = true;
		window.setTimeout(() => (saved = false), 1600);
	}

	function resetPreferences() {
		preferences = resetDashboardPreferences();
		saved = true;
		window.setTimeout(() => (saved = false), 1600);
	}

	onMount(startMonitoring);
</script>

<svelte:head><title>Settings · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={$machines.length} averageScore={null} showScore={false} />
		<section class="pt-1"><h2 class="text-xl font-semibold tracking-tight text-zinc-100">Settings</h2><p class="mt-1 text-xs text-zinc-500">Only dashboard display preferences are changed here. Detector configuration stays in the backend sources file.</p></section>

		<Panel title="Dashboard preference" subtitle="Interface only">
			<label class="block rounded border border-white/10 bg-white/[0.02] p-4">
				<p class="text-sm font-medium text-zinc-200">Overview alert count</p><p class="mt-1 text-xs leading-5 text-zinc-500">How many recent alerts appear on the Overview page.</p>
				<select bind:value={preferences.recentAlertLimit} class="mt-3 min-h-10 w-full max-w-xs rounded border border-white/10 bg-[#15151b] px-3 text-sm text-zinc-200 outline-none focus:border-violet-500/50"><option value={3}>3 alerts</option><option value={5}>5 alerts</option><option value={10}>10 alerts</option></select>
			</label>
			<div class="mt-5 flex flex-wrap items-center gap-2 border-t border-white/10 pt-4"><button type="button" on:click={savePreferences} class="flex min-h-11 items-center gap-2 rounded bg-violet-600 px-4 text-sm font-medium text-white transition hover:bg-violet-500"><Save size={16} />Save</button><button type="button" on:click={resetPreferences} class="flex min-h-11 items-center gap-2 rounded border border-white/10 px-4 text-sm font-medium text-zinc-400 transition hover:bg-white/[0.04] hover:text-zinc-200"><RotateCcw size={16} />Reset</button>{#if saved}<span class="text-xs text-emerald-400">Saved</span>{/if}</div>
		</Panel>

		<Panel title="Connection" subtitle="Read-only live status">
			<div class="grid gap-3 sm:grid-cols-2"><div class="rounded border border-white/10 bg-white/[0.02] p-4"><p class="text-xs text-zinc-500">WebSocket</p><p class={`mt-2 text-sm font-medium ${$streamState === 'connected' ? 'text-emerald-400' : 'text-zinc-300'}`}>{$streamState}</p></div><div class="rounded border border-white/10 bg-white/[0.02] p-4"><p class="text-xs text-zinc-500">Live sources</p><p class="mt-2 text-sm font-medium text-zinc-200">{$machines.length}</p></div></div>
		</Panel>
	</div>
</main>
