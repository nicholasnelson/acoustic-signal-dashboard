<script lang="ts">
	import { onMount } from 'svelte';
	import Activity from '@lucide/svelte/icons/activity';
	import Waves from '@lucide/svelte/icons/waves';

	import KpiCard from '$lib/components/ui/KpiCard.svelte';
	import { monitoringClient } from '$lib/services/monitoring';

	export let machineCount = 0;
	export let averageScore: number | null = null;
	export let scoreLabel = 'Detection score';
	export let scoreHelper = 'alert at 100';
	export let showScore = true;

	let backendState: 'checking' | 'online' | 'offline' = 'checking';
	let backendVersion = '';

	onMount(async () => {
		const health = await monitoringClient.getHealth();
		if (health) {
			backendState = 'online';
			backendVersion = health.version;
		} else {
			backendState = 'offline';
		}
	});
</script>

<div class="flex flex-col gap-3 xl:flex-row xl:items-stretch xl:justify-between">
	<section class="flex min-h-[92px] flex-1 items-center justify-between gap-4 px-5 py-4 shadow-xl shadow-black/20 backdrop-blur-xl sm:px-6">
		<div class="min-w-0">
			<h1 class="truncate text-lg font-semibold tracking-tight text-zinc-50 sm:text-xl">Acoustic Monitoring</h1>
			<p class="mt-1 truncate text-xs text-zinc-500 sm:text-[13px]">Live MIMII acoustic monitoring dashboard</p>
			
		</div>
	</section>

	<section class={`grid gap-2.5 ${showScore ? 'grid-cols-2 xl:w-[390px]' : 'grid-cols-1 xl:w-[190px]'}`}>
		<KpiCard label="Sources" value={`${machineCount}`} helper="live streams" tone="purple" icon={Activity} />
		{#if showScore}
			<KpiCard label={scoreLabel} value={averageScore === null ? '—' : `${Math.round(averageScore)}`} helper={averageScore === null ? 'waiting for armed source' : scoreHelper} tone="purple" icon={Waves} />
		{/if}
	</section>
</div>
