# HIT401 Acoustic Monitoring Dashboard

Frontend-only SvelteKit prototype for the HIT401 Group 22 acoustic monitoring project.

## Stack

- SvelteKit + Svelte 5 + TypeScript
- pnpm 10.15.0
- Tailwind CSS 4 via `@tailwindcss/vite`
- Apache ECharts 6 for waveform, spectrogram/heatmap, gauges and trend charts
- `@lucide/svelte` for icons
- `clsx` and `tailwind-merge` are included for future component class composition

## Why the charts are not hard-coded

The chart components accept typed arrays as props and pass them to Apache ECharts. Mock signal data lives in `src/lib/data/mock.ts`. When the Python backend is ready, replace the mock arrays with API/WebSocket data without rewriting the chart components.

## Run with pnpm

```bash
pnpm install
pnpm dev
```

If this is copied into an existing directory, remove stale generated files first:

```bat
rmdir /s /q node_modules
rmdir /s /q .svelte-kit
```

Then run `pnpm install` again.

## Important files

- `src/lib/components/charts/EChart.svelte` - reusable ECharts host
- `src/lib/components/charts/WaveformChart.svelte`
- `src/lib/components/charts/SpectrogramChart.svelte`
- `src/lib/components/charts/GaugeChart.svelte`
- `src/lib/components/charts/TrendChart.svelte`
- `src/lib/data/mock.ts` - temporary mock signal data
- `src/lib/services/monitoring.ts` - boundary to replace with Python API/WebSocket integration
- `src/routes` - SvelteKit pages
