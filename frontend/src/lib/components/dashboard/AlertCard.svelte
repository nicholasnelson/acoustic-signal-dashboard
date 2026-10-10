<script lang="ts">
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import { AlertTriangle, CircleAlert, Info } from '@lucide/svelte';
	import type { AlertEvent } from '$lib/types';

	export let event: AlertEvent;
	$: critical = event.severity === 'critical';
	$: warning = event.severity === 'warning';
	$: Icon = critical ? CircleAlert : warning ? AlertTriangle : Info;
</script>

<a
	href={`/alerts/${encodeURIComponent(event.id)}`}
	class={`group flex min-h-20 items-center gap-3 rounded-xl border p-3 transition ${critical ? 'border-rose-500/25 bg-rose-500/8 hover:border-rose-500/40 hover:bg-rose-500/10' : warning ? 'border-amber-500/25 bg-amber-500/8 hover:border-amber-500/40 hover:bg-amber-500/10' : 'border-white/8 bg-white/[0.025] hover:border-violet-500/25 hover:bg-white/[0.04]'}`}
>
	<div class={`grid size-11 shrink-0 place-items-center rounded-xl ${critical ? 'bg-rose-500/12 text-rose-400' : warning ? 'bg-amber-500/12 text-amber-400' : 'bg-violet-500/12 text-violet-400'}`}>
		<svelte:component this={Icon} size={22} />
	</div>
	<div class="min-w-0 flex-1">
		<div class="flex items-center justify-between gap-2">
			<strong class="truncate text-sm text-zinc-100">{event.title}</strong>
			<time class="shrink-0 text-[11px] text-zinc-600">{event.timestamp}</time>
		</div>
		<p class="mt-1 truncate text-xs text-zinc-400">
			{event.machineName} · threshold index {Math.round(event.scoreIndex)}
		</p>
	</div>
	<ChevronRight size={17} strokeWidth={1.8} class="shrink-0 text-zinc-700 transition group-hover:translate-x-0.5 group-hover:text-violet-400" />
</a>
