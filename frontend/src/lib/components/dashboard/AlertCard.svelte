<script lang="ts">
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import { CircleAlert } from '@lucide/svelte';
	import type { AlertEvent } from '$lib/types';

	export let event: AlertEvent;
</script>

<a href={`/alerts/${encodeURIComponent(event.id)}`} class="group flex min-h-20 items-center gap-3 rounded-xl border border-rose-500/25 bg-rose-500/8 p-3 transition hover:border-rose-500/40 hover:bg-rose-500/10">
	<div class="grid size-11 shrink-0 place-items-center rounded-xl bg-rose-500/12 text-rose-400"><CircleAlert size={22} /></div>
	<div class="min-w-0 flex-1">
		<div class="flex items-center justify-between gap-2"><strong class="truncate text-sm text-zinc-100">{event.title}</strong><time class="shrink-0 text-[11px] text-zinc-600">{event.timestamp}</time></div>
		<p class="mt-1 truncate text-xs text-zinc-400">{event.machineName} · detection score {Math.round(event.scoreIndex)}</p>
	</div>
	<ChevronRight size={17} strokeWidth={1.8} class="shrink-0 text-zinc-700 transition group-hover:translate-x-0.5 group-hover:text-violet-400" />
</a>
