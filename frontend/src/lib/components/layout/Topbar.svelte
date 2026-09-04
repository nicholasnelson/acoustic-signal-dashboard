<script lang="ts">
	import Activity from '@lucide/svelte/icons/activity';
	import ShieldCheck from '@lucide/svelte/icons/shield-check';
	import Waves from '@lucide/svelte/icons/waves';
	import Radio from '@lucide/svelte/icons/radio';

	import KpiCard from '$lib/components/ui/KpiCard.svelte';

	export let machineCount = 4;
	export let averageScore = 0;
	export let signalQuality = 0;
</script>

<div class="flex flex-col gap-3 xl:flex-row xl:items-stretch xl:justify-between">
	<!-- Main title card -->
	<section
		class="flex min-h-[92px] flex-1 items-center justify-between gap-4
		
	 px-5 py-4
		shadow-xl shadow-black/20 backdrop-blur-xl
		sm:px-6"
	>
		<div class="flex min-w-0 items-center gap-4">
		

			<div class="min-w-0">
				<div class="flex items-center gap-3">
					<h1
						class="truncate text-lg font-semibold tracking-tight text-zinc-50
						sm:text-xl"
					>
						Acoustic Monitoring
					</h1>
				</div>

				<p class="mt-1 truncate text-xs text-zinc-500 sm:text-[13px]">
					MIMII research prototype · simulated live stream
				</p>
			</div>
		</div>

		<!-- Live indicator -->
		
	</section>

	<!-- KPI group -->
	<section
		class="grid grid-cols-3 gap-2.5
		xl:w-[540px]"
	>
		<KpiCard
			label="Machines"
			value={`${machineCount}`}
			helper="online"
			tone="purple"
			icon={Activity}
		/>

		<KpiCard
			label="Avg. score"
			value={`${averageScore}`}
			helper="/100"
			tone="purple"
			icon={Waves}
		/>

		<KpiCard
			label="Signal quality"
			value={`${signalQuality}%`}
			helper="good"
			tone="green"
			icon={ShieldCheck}
		/>
	</section>
</div>