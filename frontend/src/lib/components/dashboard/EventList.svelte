<script lang="ts">
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import type { AlertEvent } from '$lib/types';
	export let events: AlertEvent[] = [];
</script>

<div class="space-y-1">
	{#each events as event}
		<a
			href={`/alerts/${encodeURIComponent(event.id)}`}
			class="group grid min-h-16 grid-cols-[12px_1fr_auto_18px] items-center gap-3 rounded-xl px-2 py-2 transition hover:bg-white/[0.025]"
		>
			<span class={`size-2.5 rounded-full ${event.severity === 'critical' ? 'bg-rose-500' : event.severity === 'warning' ? 'bg-amber-500' : 'bg-violet-500'}`}></span>
			<div class="min-w-0">
				<div class="truncate text-sm text-zinc-200">{event.machineName}</div>
				<div class="truncate text-xs text-zinc-500">{event.title}</div>
			</div>
			<div class="text-xs text-zinc-600">{event.timestamp}</div>
			<ChevronRight size={15} class="text-zinc-700 group-hover:text-violet-400" />
		</a>
	{/each}
</div>
