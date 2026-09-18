<script lang="ts">
  import { page } from '$app/stores';
  import { Bell, Fan, LayoutDashboard, Settings } from '@lucide/svelte';

  const items = [
    { href: '/', label: 'Overview', icon: LayoutDashboard },
    { href: '/machines', label: 'Machines', icon: Fan },
    { href: '/alerts', label: 'Alerts', icon: Bell },
    { href: '/settings', label: 'Settings', icon: Settings }
  ];
</script>

<nav class="fixed inset-x-3 bottom-3 z-40 grid grid-cols-4 rounded-2xl border border-white/10 bg-[#111116]/95 p-1.5 shadow-2xl backdrop-blur-xl lg:hidden">
  {#each items as item}
    {@const active = item.href === '/' ? $page.url.pathname === '/' : $page.url.pathname.startsWith(item.href)}
    <a href={item.href} class={`flex min-h-14 flex-col items-center justify-center gap-1 rounded-xl text-[10px] ${active ? 'bg-violet-600 text-white' : 'text-zinc-500'}`}>
      <svelte:component this={item.icon} size={20} />
      {item.label}
    </a>
  {/each}
</nav>
