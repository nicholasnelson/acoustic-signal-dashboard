<script lang="ts">
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';
	import BrainCircuit from '@lucide/svelte/icons/brain-circuit';

	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import ThresholdControl from '$lib/components/dashboard/ThresholdControl.svelte';

	import { machines } from '$lib/data/mock';

	let threshold = 65;
	let detector = 'mahalanobis';

	const averageScore = Math.round(
		machines.reduce((sum, item) => sum + item.score, 0) / machines.length
	);

	const signalQuality = Math.round(
		machines.reduce((sum, item) => sum + item.signalQuality, 0) / machines.length
	);
</script>

<svelte:head>
	<title>Settings · Acoustic Monitoring</title>
</svelte:head>

<Sidebar />

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar
			machineCount={machines.length}
			{averageScore}
			{signalQuality}
		/>

		<!-- Page heading -->
		<section class="pt-1">
			<h2 class="text-xl font-semibold tracking-tight text-zinc-100">
				Research controls
			</h2>

			<p class="mt-1 text-xs text-zinc-500">
				Configure anomaly detection behaviour for the monitoring prototype.
			</p>
		</section>

		<!-- Settings -->
		<section class="grid gap-3 xl:grid-cols-2">
			<Panel
				title="Detection threshold"
				subtitle="Control how sensitive anomaly detection should be"
			>
				<ThresholdControl bind:value={threshold} />
			</Panel>

			<Panel
				title="Detector method"
				subtitle="Select the anomaly detection approach"
			>
				<div class="space-y-4">
					<div class="flex items-center gap-3">
						<div class="flex size-10 items-center justify-center rounded bg-violet-500/10 text-violet-400">
							<BrainCircuit size={19} strokeWidth={1.8} />
						</div>

						<div>
							<p class="text-sm font-medium text-zinc-200">Active detector</p>
							<p class="mt-0.5 text-xs text-zinc-500">Method used to calculate anomaly scores</p>
						</div>
					</div>

					<select
						id="detector"
						bind:value={detector}
						class="min-h-12 w-full rounded border border-white/10 bg-[#15151b] px-4 text-sm text-zinc-100 outline-none focus:border-violet-500/50"
					>
						<option value="rule">Rule-based threshold</option>
						<option value="mahalanobis">Mahalanobis distance</option>
						<option value="autoencoder">Deep autoencoder</option>
					</select>

					<div class="border-t border-white/10 pt-4">
						<p class="text-xs leading-5 text-zinc-500">
							This control currently updates the frontend only. Later it can be connected to the Python backend.
						</p>
					</div>
				</div>
			</Panel>
		</section>

		<!-- Current configuration -->
		<Panel title="Current configuration" subtitle="Active research monitoring settings">
			<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded border border-white/10 bg-white/[0.02] p-4">
					<div class="flex items-center gap-2 text-xs text-zinc-500">
						<SlidersHorizontal size={15} />
						Threshold
					</div>

					<p class="mt-3 text-xl font-semibold text-zinc-100">
						{threshold}
						<span class="text-xs font-normal text-zinc-600">/100</span>
					</p>
				</div>

				<div class="rounded border border-white/10 bg-white/[0.02] p-4">
					<p class="text-xs text-zinc-500">Detector</p>

					<p class="mt-3 text-sm font-medium capitalize text-zinc-100">
						{detector === 'mahalanobis'
							? 'Mahalanobis distance'
							: detector === 'autoencoder'
								? 'Deep autoencoder'
								: 'Rule-based threshold'}
					</p>
				</div>

				<div class="rounded border border-white/10 bg-white/[0.02] p-4 sm:col-span-2 lg:col-span-1">
					<p class="text-xs text-zinc-500">Data source</p>

					<div class="mt-3 flex items-center gap-2">
						<span class="size-1.5 rounded-full bg-violet-400"></span>
						<p class="text-sm font-medium text-zinc-100">MIMII Fan</p>
					</div>
				</div>
			</div>
		</Panel>
	</div>
</main>