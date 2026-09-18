<script lang="ts">
	import type { Component } from 'svelte';

	export let label = '';
	export let value = '';
	export let helper = '';
	export let icon: Component | undefined;

	export let tone: 'purple' | 'green' | 'orange' | 'red' = 'purple';

	const tones = {
		purple: {
			icon: 'text-violet-400',
			iconBg: 'bg-violet-500/[0.08]',
			iconBorder: 'border-violet-500/15',
			helper: 'text-violet-400'
		},

		green: {
			icon: 'text-emerald-400',
			iconBg: 'bg-emerald-500/[0.08]',
			iconBorder: 'border-emerald-500/15',
			helper: 'text-emerald-400'
		},

		orange: {
			icon: 'text-orange-400',
			iconBg: 'bg-orange-500/[0.08]',
			iconBorder: 'border-orange-500/15',
			helper: 'text-orange-400'
		},

		red: {
			icon: 'text-red-400',
			iconBg: 'bg-red-500/[0.08]',
			iconBorder: 'border-red-500/15',
			helper: 'text-red-400'
		}
	};

	$: style = tones[tone];
</script>

<div
	class="flex min-h-[92px] items-center gap-3 rounded
	border border-white/[0.08]
	bg-[#101014]/85 px-4 py-3
	shadow-xl shadow-black/15
	backdrop-blur-xl
	transition-colors hover:border-white/[0.12]"
>
	{#if icon}
		<div
			class={`hidden h-10 w-10 shrink-0 items-center justify-center rounded-xl
			border sm:flex ${style.iconBg} ${style.iconBorder} ${style.icon}`}
		>
			<svelte:component
				this={icon}
				size={19}
				strokeWidth={1.8}
			/>
		</div>
	{/if}

	<div class="min-w-0">
		<p
			class="truncate text-[10px] font-medium uppercase tracking-[0.09em]
			text-zinc-500 sm:text-[11px]"
		>
			{label}
		</p>

		<div class="mt-1 flex items-baseline gap-1.5">
			<span
				class="text-xl font-semibold tracking-tight text-zinc-100 sm:text-2xl"
			>
				{value}
			</span>

			{#if helper}
				<span
					class={`text-[11px] font-medium sm:text-xs ${style.helper}`}
				>
					{helper}
				</span>
			{/if}
		</div>
	</div>
</div>