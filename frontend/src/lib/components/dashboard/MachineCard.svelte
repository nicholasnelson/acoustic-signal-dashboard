<script lang="ts">
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Fan from '@lucide/svelte/icons/fan';
	import type { Machine } from '$lib/types';

	export let machine: Machine;

	$: statusLabel = machine.status === 'anomaly' ? 'Alert' : machine.status === 'normal' ? 'Normal' : machine.status === 'calibrating' ? 'Calibrating' : 'Offline';
	$: statusClass = machine.status === 'anomaly' ? 'text-rose-400 bg-rose-500/10' : machine.status === 'normal' ? 'text-emerald-400 bg-emerald-500/10' : machine.status === 'calibrating' ? 'text-violet-300 bg-violet-500/10' : 'text-zinc-500 bg-zinc-500/10';
	$: borderClass = machine.status === 'anomaly' ? 'border-rose-500/25 hover:border-rose-500/45' : 'border-white/10 hover:border-violet-500/30';
	$: progressClass = machine.status === 'anomaly' ? '[&::-webkit-progress-value]:bg-rose-500 [&::-moz-progress-bar]:bg-rose-500' : '[&::-webkit-progress-value]:bg-violet-500 [&::-moz-progress-bar]:bg-violet-500';
</script>

<a href={`/machines/${machine.id}`} class={`group rounded border bg-[#101014]/90 p-3.5 transition hover:bg-white/[0.03] ${borderClass}`}>
	<div class="flex items-start justify-between gap-3">
		<div class="flex min-w-0 items-center gap-3">
			<div class="flex size-9 shrink-0 items-center justify-center rounded bg-violet-600 text-white"><Fan size={18} strokeWidth={1.8} /></div>
			<div class="min-w-0"><h3 class="truncate text-sm font-medium text-zinc-100">{machine.name}</h3><p class="mt-0.5 truncate text-[11px] text-zinc-500">{machine.id}</p></div>
		</div>
		<div class="flex items-center gap-2">
			<div class={`flex items-center gap-1.5 rounded px-2 py-1 text-[10px] font-medium ${statusClass}`}><span class="size-1.5 rounded-full bg-current"></span>{statusLabel}</div>
			<ChevronRight size={16} strokeWidth={1.8} class="shrink-0 text-zinc-700 group-hover:text-violet-400" />
		</div>
	</div>

	<div class="mt-3 flex items-end justify-between gap-4">
		<div>
			<p class="text-[10px] uppercase tracking-wide text-zinc-600">{machine.status === 'calibrating' ? 'Calibration' : 'Detection score'}</p>
			<div class="mt-0.5 flex items-baseline gap-1.5">
				<span class={`text-xl font-semibold ${machine.status === 'anomaly' ? 'text-rose-400' : 'text-zinc-100'}`}>
					{machine.status === 'calibrating' ? `${Math.round((machine.calibrationProgress ?? 0) * 100)}%` : machine.score === null ? '—' : Math.round(machine.score)}
				</span>
				{#if machine.score !== null}<span class="text-[10px] text-zinc-600">alert at 100</span>{/if}
			</div>
		</div>
		<div class="text-right"><p class="text-[10px] text-zinc-600">Last update</p><p class="mt-0.5 text-[11px] font-medium text-zinc-300">{machine.lastUpdate ? new Date(machine.lastUpdate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Waiting'}</p></div>
	</div>

	<progress value={machine.status === 'calibrating' ? (machine.calibrationProgress ?? 0) * 100 : machine.score === null ? 0 : Math.min(machine.score, 100)} max="100" aria-label={`${machine.name} monitoring progress`} class={`mt-2.5 h-1 w-full appearance-none overflow-hidden rounded bg-zinc-800 [&::-webkit-progress-bar]:bg-zinc-800 [&::-webkit-progress-value]:rounded [&::-moz-progress-bar]:rounded ${progressClass}`} />
</a>
