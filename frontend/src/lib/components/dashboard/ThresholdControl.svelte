<script lang="ts">
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';

	export let value = 65;

	const min = 20;
	const max = 95;

	$: percentage = ((value - min) / (max - min)) * 100;
</script>

<div class="space-y-5">
	<!-- Header -->
	<div class="flex items-center justify-between gap-4">
		<div class="flex min-w-0 items-center gap-3">
			<div
				class="flex size-10 shrink-0 items-center justify-center rounded-xl
				border border-violet-500/15 bg-violet-500/[0.08]
				text-violet-400"
			>
				<SlidersHorizontal size={18} strokeWidth={1.8} />
			</div>

			<div class="min-w-0">
				<h3 class="text-sm font-medium text-zinc-200">
					Detection threshold
				</h3>

				<p class="mt-0.5 text-xs text-zinc-500">
					Adjust anomaly detection sensitivity
				</p>
			</div>
		</div>

		<!-- Current value -->
		<output
			class="flex min-w-[64px] items-center justify-center rounded-xl
				border border-violet-500/15 bg-violet-500/[0.08]
				px-3 py-2 text-lg font-semibold tabular-nums
				text-violet-300"
		>
			{value}
		</output>
	</div>

	<!-- Slider -->
	<div class="space-y-3">
		<div class="relative flex min-h-11 items-center">
			<input
				bind:value
				type="range"
				{min}
				{max}
				step="1"
				aria-label="Anomaly detection threshold"
				class="threshold-slider w-full"
				style={`--progress: ${percentage}%`}
			/>
		</div>

		<!-- Labels -->
		<div class="flex items-center justify-between">
			<div>
				<span class="text-[11px] font-medium text-zinc-500">
					Sensitive
				</span>

				<p class="mt-0.5 text-[10px] text-zinc-700">
					More alerts
				</p>
			</div>

			<div class="text-right">
				<span class="text-[11px] font-medium text-zinc-500">
					Conservative
				</span>

				<p class="mt-0.5 text-[10px] text-zinc-700">
					Fewer alerts
				</p>
			</div>
		</div>
	</div>

	<!-- Current interpretation -->
	<div
		class="flex items-center justify-between rounded-xl
			border border-white/[0.06] bg-white/[0.025]
			px-3.5 py-3"
	>
		<span class="text-xs text-zinc-500">
			Current sensitivity
		</span>

		<span
			class="text-xs font-medium"
			class:text-orange-300={value < 45}
			class:text-violet-300={value >= 45 && value <= 75}
			class:text-emerald-300={value > 75}
		>
			{value < 45
				? 'High'
				: value <= 75
					? 'Balanced'
					: 'Low'}
		</span>
	</div>
</div>

<style>
	.threshold-slider {
		appearance: none;
		height: 6px;
		border-radius: 999px;
		outline: none;

		background: linear-gradient(
			to right,
			#7c3aed 0%,
			#7c3aed var(--progress),
			rgba(255, 255, 255, 0.08) var(--progress),
			rgba(255, 255, 255, 0.08) 100%
		);
	}

	.threshold-slider::-webkit-slider-thumb {
		appearance: none;

		width: 24px;
		height: 24px;

		border-radius: 999px;
		border: 4px solid #16161c;

		background: #a78bfa;

		box-shadow:
			0 0 0 1px rgba(167, 139, 250, 0.35),
			0 4px 15px rgba(124, 58, 237, 0.35);

		cursor: grab;
	}

	.threshold-slider::-webkit-slider-thumb:active {
		cursor: grabbing;
		transform: scale(1.08);
	}

	.threshold-slider::-moz-range-thumb {
		width: 18px;
		height: 18px;

		border-radius: 999px;
		border: 4px solid #16161c;

		background: #a78bfa;

		box-shadow:
			0 0 0 1px rgba(167, 139, 250, 0.35),
			0 4px 15px rgba(124, 58, 237, 0.35);

		cursor: grab;
	}

	.threshold-slider:focus-visible::-webkit-slider-thumb {
		box-shadow:
			0 0 0 4px rgba(139, 92, 246, 0.2),
			0 4px 15px rgba(124, 58, 237, 0.35);
	}
</style>