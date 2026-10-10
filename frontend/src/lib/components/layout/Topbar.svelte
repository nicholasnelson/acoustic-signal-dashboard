<script lang="ts">
	import { onMount } from 'svelte';
	import Activity from '@lucide/svelte/icons/activity';
	import Waves from '@lucide/svelte/icons/waves';

	import KpiCard from '$lib/components/ui/KpiCard.svelte';
	import { monitoringClient } from '$lib/services/monitoring';

	export let machineCount = 0;
	export let averageScore = 0;
	export let signalQuality = 0;
	export let scoreLabel = 'Detection score';
	export let scoreHelper = '';
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
			<h1 class="truncate text-lg font-semibold tracking-tight text-zinc-50 sm:text-xl">
				Acoustic Monitoring
			</h1>
			<p class="mt-1 truncate text-xs text-zinc-500 sm:text-[13px]">
				MIMII fan monitoring dashboard
			</p>
			<div class="mt-2 flex items-center gap-2 text-[11px]">
				<span
					class="size-1.5 rounded-full"
					class:bg-zinc-500={backendState === 'checking'}
					class:bg-emerald-400={backendState === 'online'}
					class:bg-rose-400={backendState === 'offline'}
				></span>
				<span
					class:text-zinc-500={backendState === 'checking'}
					class:text-emerald-400={backendState === 'online'}
					class:text-rose-400={backendState === 'offline'}
				>
					{#if backendState === 'checking'}
						Checking backend
					{:else if backendState === 'online'}
						Backend connected{backendVersion ? ` · v${backendVersion}` : ''}
					{:else}
						Backend unavailable
					{/if}
				</span>
			</div>
		</div>
	</section>

	<section class={`grid gap-2.5 ${showScore ? 'grid-cols-2 xl:w-[390px]' : 'grid-cols-1 xl:w-[190px]'}`}>
		<KpiCard label="Machines" value={`${machineCount}`} helper="MIMII sources" tone="purple" icon={Activity} />
		{#if showScore}
			<KpiCard label={scoreLabel} value={`${Math.round(averageScore)}`} helper={scoreHelper} tone="purple" icon={Waves} />
		{/if}
	</section>
</div>
