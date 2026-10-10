<script lang="ts">
  import { onMount } from 'svelte';
  import type { EChartsOption, EChartsType } from 'echarts';

  export let option: EChartsOption;
  export let height = '100%';
  export let minHeight = '240px';

  let host: HTMLDivElement;
  let chart: EChartsType | undefined;
  let observer: ResizeObserver | undefined;

  onMount(async () => {
    const echarts = await import('echarts');
    chart = echarts.init(host, undefined, { renderer: 'canvas' });
    chart.setOption(option, { notMerge: true });

    observer = new ResizeObserver(() => chart?.resize());
    observer.observe(host);

    return () => {
      observer?.disconnect();
      chart?.dispose();
    };
  });

  $: if (chart && option) {
    chart.setOption(option, { notMerge: true });
  }
</script>

<div bind:this={host} class="w-full" style:height style:min-height={minHeight}></div>
