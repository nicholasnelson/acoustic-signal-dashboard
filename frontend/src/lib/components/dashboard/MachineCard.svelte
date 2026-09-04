<script lang="ts">
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Fan from '@lucide/svelte/icons/fan';

	import type { Machine } from '$lib/types';

	export let machine: Machine;

	$: statusLabel =
		machine.status === 'anomaly'
			? 'Anomaly'
			: machine.status === 'warning'
				? 'Warning'
				: 'Normal';

	$: statusClass =
		machine.status === 'anomaly'
			? 'text-rose-400 bg-rose-500/10'
			: machine.status === 'warning'
				? 'text-amber-400 bg-amber-500/10'
				: 'text-emerald-400 bg-emerald-500/10';

	$: progressClass =
		machine.status === 'anomaly'
			? '[&::-webkit-progress-value]:bg-rose-500 [&::-moz-progress-bar]:bg-rose-500'
			: machine.status === 'warning'
				? '[&::-webkit-progress-value]:bg-amber-500 [&::-moz-progress-bar]:bg-amber-500'
				: '[&::-webkit-progress-value]:bg-violet-500 [&::-moz-progress-bar]:bg-violet-500';
</script>

<a
	href={`/machines/${machine.id}`}
	class="
		group
		flex
		min-h-[165px]
		flex-col
		justify-between
		rounded
		border
		border-white/10
		bg-[#101014]/90
		p-4
		hover:border-violet-500/30
		hover:bg-white/[0.03]
	"
>
	<!-- Machine header -->
	<div class="flex items-start justify-between gap-3">
		<div class="flex min-w-0 items-center gap-3">
			<div
				class="
					flex
					size-10
					shrink-0
					items-center
					justify-center
					rounded
					bg-violet-600
					text-white
				"
			>
				<Fan size={20} strokeWidth={1.8} />
			</div>

			<div class="min-w-0">
				<h3 class="truncate text-sm font-medium text-zinc-100">
					{machine.name}
				</h3>

				<p class="mt-0.5 truncate text-xs text-zinc-500">
					{machine.type}
				</p>
			</div>
		</div>

		<ChevronRight
			size={18}
			strokeWidth={1.8}
			class="mt-1 shrink-0 text-zinc-600 group-hover:text-violet-400"
		/>
	</div>

	<!-- Score -->
	<div class="mt-5">
		<div class="flex items-end justify-between gap-4">
			<div>
				<p class="text-[11px] uppercase tracking-wide text-zinc-600">
					Anomaly score
				</p>

				<div class="mt-1 flex items-baseline gap-1">
					<span class="text-2xl font-semibold text-zinc-100">
						{machine.score}
					</span>

					<span class="text-xs text-zinc-600">
						/100
					</span>
				</div>
			</div>

			<div
				class={`
					flex
					items-center
					gap-1.5
					rounded
					px-2
					py-1
					text-[11px]
					font-medium
					${statusClass}
				`}
			>
				<span class="size-1.5 rounded-full bg-current"></span>

				{statusLabel}
			</div>
		</div>

		<!-- Score bar -->
		<progress
			value={machine.score}
			max="100"
			aria-label={`${machine.name} anomaly score`}
			class={`
				mt-3
				h-1.5
				w-full
				appearance-none
				overflow-hidden
				rounded
				bg-zinc-800

				[&::-webkit-progress-bar]:bg-zinc-800
				[&::-webkit-progress-value]:rounded
				[&::-moz-progress-bar]:rounded

				${progressClass}
			`}
		/>
	</div>

	<!-- Bottom -->
	<div
		class="
			mt-4
			flex
			items-center
			justify-between
			border-t
			border-white/10
			pt-3
		"
	>
		<span class="text-xs text-zinc-500">
			Signal quality
		</span>

		<div class="flex items-center gap-2">
			<span
				class="size-1.5 rounded-full"
				class:bg-emerald-400={machine.signalQuality >= 80}
				class:bg-amber-400={machine.signalQuality >= 60 && machine.signalQuality < 80}
				class:bg-rose-400={machine.signalQuality < 60}
			></span>

			<span class="text-xs font-medium text-zinc-300">
				{machine.signalQuality}%
			</span>
		</div>
	</div>
</a>