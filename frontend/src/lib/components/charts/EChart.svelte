<script lang="ts">
  import { onMount } from 'svelte';
  import type { EChartsOption, EChartsType } from 'echarts';

  export let option: EChartsOption;
  export let height = '100%';
  export let minHeight = '240px';

  let host: HTMLDivElement;
  let chart: EChartsType | undefined;
  let resizeObserver: ResizeObserver | undefined;
  let visibilityObserver: IntersectionObserver | undefined;
  let destroyed = false;
  let visible = false;
  let initializing = false;
  let optionFrame = 0;
  let resizeFrame = 0;
  let pendingOption: EChartsOption | undefined;
  let lastAppliedOption: EChartsOption | undefined;
  let lastWidth = 0;
  let lastHeight = 0;

  async function ensureChart() {
    if (destroyed || chart || initializing || !visible || !host) return;
    initializing = true;

    try {
      const echarts = await import('echarts');
      if (destroyed || !visible || !host) return;

      chart = echarts.init(host, undefined, {
        renderer: 'canvas',
        useDirtyRect: true,
        devicePixelRatio: Math.min(window.devicePixelRatio || 1, 1.5)
      });

      const rect = host.getBoundingClientRect();
      lastWidth = Math.round(rect.width);
      lastHeight = Math.round(rect.height);

      resizeObserver = new ResizeObserver((entries) => {
        if (!visible || !chart) return;
        const entry = entries[0];
        if (!entry) return;
        scheduleResize(entry.contentRect.width, entry.contentRect.height);
      });
      resizeObserver.observe(host);

      scheduleOption(option);
    } finally {
      initializing = false;
    }
  }

  function scheduleOption(next: EChartsOption) {
    if (destroyed || !visible || !chart || chart.isDisposed() || next === lastAppliedOption) return;
    pendingOption = next;
    if (optionFrame) return;

    optionFrame = requestAnimationFrame(() => {
      optionFrame = 0;
      const nextOption = pendingOption;
      pendingOption = undefined;
      if (!nextOption || destroyed || !visible || !chart || chart.isDisposed()) return;

      chart.setOption(nextOption, {
        notMerge: false,
        lazyUpdate: true,
        silent: true
      });
      lastAppliedOption = nextOption;
    });
  }

  function scheduleResize(width: number, height: number) {
    const w = Math.round(width);
    const h = Math.round(height);
    if (w <= 0 || h <= 0 || (w === lastWidth && h === lastHeight)) return;
    lastWidth = w;
    lastHeight = h;
    if (resizeFrame) return;

    resizeFrame = requestAnimationFrame(() => {
      resizeFrame = 0;
      if (destroyed || !visible || !chart || chart.isDisposed()) return;
      chart.resize({ width: lastWidth, height: lastHeight, silent: true });
    });
  }

  onMount(() => {
    destroyed = false;

    visibilityObserver = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (!entry) return;
        visible = entry.isIntersecting;

        if (visible) {
          void ensureChart().then(() => {
            if (chart && !chart.isDisposed()) {
              const rect = host.getBoundingClientRect();
              scheduleResize(rect.width, rect.height);
              scheduleOption(option);
            }
          });
        } else {
          if (optionFrame) cancelAnimationFrame(optionFrame);
          optionFrame = 0;
          pendingOption = undefined;
        }
      },
      { rootMargin: '120px 0px' }
    );

    visibilityObserver.observe(host);

    return () => {
      destroyed = true;
      visible = false;
      visibilityObserver?.disconnect();
      resizeObserver?.disconnect();
      if (optionFrame) cancelAnimationFrame(optionFrame);
      if (resizeFrame) cancelAnimationFrame(resizeFrame);
      optionFrame = 0;
      resizeFrame = 0;
      pendingOption = undefined;
      lastAppliedOption = undefined;
      if (chart && !chart.isDisposed()) chart.dispose();
      chart = undefined;
    };
  });

  $: if (visible && chart && option) scheduleOption(option);
</script>

<div bind:this={host} class="w-full" style:height style:min-height={minHeight}></div>
