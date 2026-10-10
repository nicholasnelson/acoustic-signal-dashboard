<script lang="ts">
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { page } from '$app/stores';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Activity from '@lucide/svelte/icons/activity';
	import Gauge from '@lucide/svelte/icons/gauge';
	import Radio from '@lucide/svelte/icons/radio';

	import Topbar from '$lib/components/layout/Topbar.svelte';
	import Panel from '$lib/components/ui/Panel.svelte';
	import KpiCard from '$lib/components/ui/KpiCard.svelte';
	import WaveformChart from '$lib/components/charts/WaveformChart.svelte';
	import SpectrogramChart from '$lib/components/charts/SpectrogramChart.svelte';
	import GaugeChart from '$lib/components/charts/GaugeChart.svelte';
	import EventList from '$lib/components/dashboard/EventList.svelte';
	import { monitoringClient } from '$lib/services/monitoring';
	import type { ClipLabel, Machine, MachineAnalysis } from '$lib/types';

	export let data: { id: string };

	let machines: Machine[] = [];
	let analysis: MachineAnalysis | null = null;
	let label: ClipLabel = 'normal';
	let clips: string[] = [];
	let selectedClip = '';
	let loading = true;
	let error = '';

	$: machine = analysis?.machine ?? machines.find((item) => item.id === data.id) ?? null;
	$: thresholdIndex = analysis?.summary.thresholdIndex ?? machine?.score ?? 0;
	$: signalQuality = analysis?.summary.signalQuality ?? machine?.signalQuality ?? 0;
	$: statusLabel = analysis?.summary.status === 'anomaly' ? 'Detector anomaly' : analysis?.summary.status === 'warning' ? 'Detector warning' : analysis?.summary.status === 'normal' ? 'Within threshold' : 'Ready';
	$: statusClass = analysis?.summary.status === 'anomaly' ? 'bg-rose-500/10 text-rose-400' : analysis?.summary.status === 'warning' ? 'bg-amber-500/10 text-amber-400' : analysis?.summary.status === 'normal' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-violet-500/10 text-violet-300';

	async function loadAnalysis(nextLabel: ClipLabel = label, preferredClip = '', analyse = true) {
		loading = true;
		error = '';
		label = nextLabel;
		try {
			clips = await monitoringClient.getClips(data.id, label, 50);
			if (!clips.length) throw new Error(`No ${label} clips are available for ${data.id}.`);
			selectedClip = preferredClip && clips.includes(preferredClip) ? preferredClip : clips[0];
			if (analyse) {
				analysis = await monitoringClient.getMachineAnalysis(data.id, label, selectedClip);
			} else {
				analysis = null;
			}
		} catch (cause) {
			error = cause instanceof Error ? cause.message : 'Unable to analyse this machine.';
			analysis = null;
		} finally {
			loading = false;
		}
	}

	async function analyseSelected() {
		if (!selectedClip) return;
		loading = true;
		error = '';
		try {
			analysis = await monitoringClient.getMachineAnalysis(data.id, label, selectedClip);
		} catch (cause) {
			error = cause instanceof Error ? cause.message : 'Unable to analyse this clip.';
		} finally {
			loading = false;
		}
	}

	onMount(async () => {
		try {
			machines = await monitoringClient.getMachines();
		} catch {
			machines = [];
		}

		const params = get(page).url.searchParams;
		const requestedLabel: ClipLabel = params.get('label') === 'abnormal' ? 'abnormal' : 'normal';
		const requestedClip = params.get('clip') ?? '';
		// Always analyse the selected/default clip when the machine page opens.
		await loadAnalysis(requestedLabel, requestedClip, true);
	});
</script>

<svelte:head><title>{machine?.name ?? data.id} · Acoustic Monitoring</title></svelte:head>

<main class="min-h-screen bg-[#09090d] px-3 pb-24 pt-3 sm:px-5 sm:pt-5 lg:pl-[108px] lg:pr-6 lg:pb-8">
	<div class="mx-auto max-w-[1700px] space-y-4">
		<Topbar machineCount={machines.length} averageScore={thresholdIndex} {signalQuality} scoreLabel="Detection score" />

		<div class="flex flex-col gap-4 pt-1">
			<a href="/machines" class="flex w-fit items-center gap-2 text-sm text-zinc-500 hover:text-zinc-200"><ArrowLeft size={17} />Back to machines</a>

			<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
				<div>
					<div class="flex flex-wrap items-center gap-2">
						<h2 class="text-xl font-semibold text-zinc-100">{machine?.name ?? data.id}</h2>
						<div class={`flex items-center gap-1.5 rounded px-2 py-1 text-[11px] font-medium ${statusClass}`}><span class="size-1.5 rounded-full bg-current"></span>{statusLabel}</div>
					</div>
					<p class="mt-1 text-xs text-zinc-500">MIMII Fan · recording analysis and alert review</p>
				</div>

				<div class="flex flex-wrap items-center gap-2">
					<button type="button" on:click={() => loadAnalysis('normal')} class={`rounded border px-3 py-2 text-xs font-medium ${label === 'normal' ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' : 'border-white/10 text-zinc-400 hover:bg-white/[0.04]'}`}>Normal replay</button>
					<button type="button" on:click={() => loadAnalysis('abnormal')} class={`rounded border px-3 py-2 text-xs font-medium ${label === 'abnormal' ? 'border-rose-500/30 bg-rose-500/10 text-rose-300' : 'border-white/10 text-zinc-400 hover:bg-white/[0.04]'}`}>Abnormal replay</button>
				</div>
			</div>
		</div>

		{#if machines.length > 1}
			<section class="flex flex-wrap items-center gap-2 rounded border border-white/10 bg-[#101014]/90 p-3">
				<span class="mr-1 text-xs text-zinc-600">Quick switch</span>
				{#each machines as item}
					<a href={`/machines/${item.id}`} class={`rounded border px-3 py-2 text-xs font-medium transition ${item.id === data.id ? 'border-violet-500/30 bg-violet-500/10 text-violet-300' : 'border-white/10 text-zinc-500 hover:bg-white/[0.04] hover:text-zinc-200'}`}>{item.name}</a>
				{/each}
			</section>
		{/if}

		{#if error}
			<div class="rounded border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">{error}<p class="mt-1 text-xs text-rose-300/70">Expected dataset path: data/6_dB/fan/{data.id}/{label}/*.wav</p></div>
		{/if}

		<Panel title="Replay selection" subtitle="Choose a dataset recording to analyse">
			<div class="mb-3 flex items-center gap-2 text-xs text-emerald-400">
				<span class="size-1.5 rounded-full bg-emerald-400"></span>
				Auto-analysis enabled — opening the page, switching Normal/Abnormal, or changing the clip runs analysis automatically.
			</div>
			<div class="flex flex-col gap-3 sm:flex-row sm:items-end">
				<label class="flex-1 text-xs text-zinc-500">Clip
					<select bind:value={selectedClip} on:change={analyseSelected} class="mt-2 min-h-11 w-full rounded border border-white/10 bg-[#15151b] px-3 text-sm text-zinc-200 outline-none focus:border-violet-500/50">
						{#each clips as clip}<option value={clip}>{clip}</option>{/each}
					</select>
				</label>
				<button type="button" on:click={analyseSelected} disabled={loading || !selectedClip} class="min-h-11 rounded bg-violet-600 px-5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50">{loading ? 'Analysing…' : 'Re-analyse clip'}</button>
			</div>
			<div class="mt-4 grid gap-2 border-t border-white/10 pt-4 text-xs sm:grid-cols-3">
				<div><span class="text-zinc-600">Normal clips</span><span class="ml-2 font-medium text-zinc-300">{machine?.normalClips ?? 0}</span></div>
				<div><span class="text-zinc-600">Abnormal clips</span><span class="ml-2 font-medium text-zinc-300">{machine?.abnormalClips ?? 0}</span></div>
				<div><span class="text-zinc-600">Current label</span><span class="ml-2 font-medium capitalize text-zinc-300">{label}</span></div>
			</div>
		</Panel>

		{#if analysis}
			<section class="grid gap-3 sm:grid-cols-3">
				<KpiCard label="Detection score" value={`${Math.round(analysis.summary.thresholdIndex)}`} helper="alert at 100" tone={analysis.summary.status === 'anomaly' ? 'red' : analysis.summary.status === 'warning' ? 'orange' : 'purple'} icon={Gauge} />
				<KpiCard label="RMS amplitude" value={analysis.summary.rms.toFixed(4)} helper="" tone="purple" icon={Activity} />
				<KpiCard label="Dominant frequency" value={analysis.summary.dominantFrequencyKHz.toFixed(2)} helper="kHz" tone="purple" icon={Radio} />
			</section>

			<section class="grid gap-3 xl:grid-cols-[280px_minmax(0,1fr)]">
				<Panel title="Alert level" subtitle="Shows how the selected recording compares with normal operation">
					<GaugeChart value={analysis.summary.thresholdIndex} threshold={100} label="Detection score" height="250px" />
					<div class="border-t border-white/10 pt-3 text-xs text-zinc-500">{analysis.summary.anomalousWindows}/{analysis.summary.totalWindows} windows triggered an alert.</div>
				</Panel>

				<Panel title="Waveform" subtitle={`${analysis.clip.name} · ${analysis.clip.sampleRate} Hz · channel 0`}>
					<div slot="action" class="flex items-center gap-2 rounded bg-violet-500/10 px-2.5 py-1.5 text-[10px] font-medium uppercase text-violet-300"><span class="size-1.5 rounded-full bg-violet-400"></span>Replay</div>
					<WaveformChart points={analysis.waveform} height="300px" />
				</Panel>
			</section>

			<section class="grid gap-3 xl:grid-cols-[minmax(0,1.5fr)_340px]">
				<Panel title="Frequency activity" subtitle="Frequency energy across the recording">
					<SpectrogramChart points={analysis.spectrogram} height="340px" />
				</Panel>

				<Panel title="Machine events" subtitle="Click an event to inspect its alert details">
					{#if analysis.events.length}<EventList events={analysis.events} />{:else}<div class="flex min-h-40 items-center justify-center"><p class="text-sm text-zinc-500">No threshold exceedances in this clip.</p></div>{/if}
				</Panel>
			</section>
		{:else if loading}
			<div class="rounded border border-white/10 bg-[#101014]/90 p-6 text-sm text-zinc-500">Analysing the selected recording…</div>
		{:else if selectedClip}
			<div class="rounded border border-white/10 bg-[#101014]/90 p-6 text-sm text-zinc-500">The selected clip will be analysed automatically.</div>
		{/if}
	</div>
</main>
