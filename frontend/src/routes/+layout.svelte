<script lang="ts">
  import '../app.css';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import MobileNav from '$lib/components/layout/MobileNav.svelte';
</script>

<Sidebar />
<slot />
<MobileNav />
