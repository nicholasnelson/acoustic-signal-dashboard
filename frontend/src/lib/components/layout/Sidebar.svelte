<script lang="ts">
	import { page } from '$app/state';

	import Activity from '@lucide/svelte/icons/activity';
	import LayoutDashboard from '@lucide/svelte/icons/layout-dashboard';
	import Fan from '@lucide/svelte/icons/fan';
	import Bell from '@lucide/svelte/icons/bell';
	import Settings from '@lucide/svelte/icons/settings';

	const items = [
		{
			href: '/',
			label: 'Overview',
			icon: LayoutDashboard
		},
		{
			href: '/machines',
			label: 'Machines',
			icon: Fan
		},
		{
			href: '/alerts',
			label: 'Alerts',
			icon: Bell
		},
		{
			href: '/settings',
			label: 'Settings',
			icon: Settings
		}
	];

	function isActive(href: string) {
		if (href === '/') {
			return page.url.pathname === '/';
		}

		return page.url.pathname.startsWith(href);
	}
</script>

<div
	class="fixed left-5 top-1/2 z-40 hidden -translate-y-1/2 flex-col items-center gap-3 lg:flex"
>
	<!-- App icon -->


	<!-- Floating navigation -->
	<nav
		class="flex flex-col gap-1.5 rounded border border-white/10
		bg-[#101014]/90 p-2 shadow-2xl shadow-black/30 backdrop-blur-xl"
		aria-label="Main navigation"
	>
		{#each items as item}
			{@const Icon = item.icon}
			{@const active = isActive(item.href)}

			<a
				href={item.href}
				aria-current={active ? 'page' : undefined}
				aria-label={item.label}
				class={[
					'group relative flex h-14 w-14 items-center justify-center rounded transition-all duration-200',
					'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500',
					active
						? 'bg-violet-600 text-white shadow-lg shadow-violet-950/40'
						: 'text-zinc-500 hover:bg-white/[0.06] hover:text-zinc-100'
				]}
			>
				<Icon
					size={22}
					strokeWidth={active ? 2 : 1.8}
				/>

				<!-- Tooltip -->
				<div
					class="pointer-events-none absolute left-[calc(100%+12px)] whitespace-nowrap
					rounded-lg border border-white/10 bg-[#15151a] px-3 py-2
					text-xs font-medium text-zinc-200 opacity-0 shadow-xl
					transition-all duration-150 group-hover:translate-x-1 group-hover:opacity-100"
				>
					{item.label}
				</div>

				<!-- Active dot -->
				{#if active}
					<span
						class="absolute -right-[11px] h-5.5 w-1.5 rounded  bg-violet-400"
					></span>
				{/if}
			</a>
		{/each}
	</nav>
</div>