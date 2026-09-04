<script lang="ts">
  import { AlertTriangle, CircleAlert, Info } from '@lucide/svelte';
  import type { AlertEvent } from '$lib/types';
  export let event: AlertEvent;

  $: critical = event.severity === 'critical';
  $: warning = event.severity === 'warning';
  $: Icon = critical ? CircleAlert : warning ? AlertTriangle : Info;
</script>

<article class={`flex min-h-20 items-center gap-3 rounded-xl border p-3 ${critical ? 'border-rose-500/25 bg-rose-500/8' : warning ? 'border-amber-500/25 bg-amber-500/8' : 'border-white/8 bg-white/[0.025]'}`}>
  <div class={`grid size-11 shrink-0 place-items-center rounded-xl ${critical ? 'bg-rose-500/12 text-rose-400' : warning ? 'bg-amber-500/12 text-amber-400' : 'bg-violet-500/12 text-violet-400'}`}>
    <svelte:component this={Icon} size={22} />
  </div>
  <div class="min-w-0 flex-1">
    <div class="flex items-center justify-between gap-2">
      <strong class="truncate text-sm text-zinc-100">{event.title}</strong>
      <time class="shrink-0 text-[11px] text-zinc-600">{event.timestamp}</time>
    </div>
    <p class="mt-1 truncate text-xs text-zinc-400">{event.machineName} · score {event.score}/100</p>
  </div>
</article>
