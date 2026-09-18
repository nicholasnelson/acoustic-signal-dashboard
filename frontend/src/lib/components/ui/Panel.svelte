<script lang="ts">
	export let title = '';
	export let subtitle = '';
	export let className = '';
	export let contentClass = '';
</script>

<section
	class={`overflow-hidden rounded border border-white/[0.07]
	bg-[#101014]/80 backdrop-blur-xl
	shadow-xl shadow-black/20
	transition-colors duration-200
	hover:border-white/[0.10]
	${className}`}
>
	{#if title || subtitle}
		<header
			class="flex min-h-[68px] items-center justify-between gap-4
			border-b border-white/[0.05] px-5 py-4 sm:px-6"
		>
			<div class="min-w-0">
				{#if title}
					<h2
						class="truncate text-sm font-semibold tracking-tight text-zinc-100"
					>
						{title}
					</h2>
				{/if}

				{#if subtitle}
					<p
						class="mt-1 truncate text-xs leading-relaxed text-zinc-500"
					>
						{subtitle}
					</p>
				{/if}
			</div>

			<div class="shrink-0">
				<slot name="action" />
			</div>
		</header>
	{/if}

	<div class={`p-4 sm:p-5 lg:p-6 ${contentClass}`}>
		<slot />
	</div>
</section>