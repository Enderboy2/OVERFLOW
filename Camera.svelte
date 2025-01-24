<script>
	export let feed;
	export let cameraStates;
	export let setPrimaryCamera;
</script>

{#if feed?.id}
	<div
		class="animate-fadeIn relative flex aspect-video items-center justify-center overflow-hidden rounded-md border border-white bg-black text-white shadow-md"
		style="animation-delay: {feed.id * 0.2}s; animation-duration: 1s;"
	>
		<img
			src={feed.url}
			class="absolute inset-0 h-full w-full object-cover"
			on:click={() => setPrimaryCamera(feed.id)}
		/>
		<!-- Indicator -->
		<span
			class={`absolute left-2 top-2 h-4 w-4 rounded-full ${
				cameraStates[feed.id - 1] === 'online'
					? 'animate-pulse bg-green-500'
					: 'animate-pulse bg-red-500'
			}`}
		></span>
		<!-- Placeholder text if camera is offline -->
		{#if cameraStates[feed.id - 1] === 'offline'}
			<span class="text-lg font-bold text-red-500">Camera {feed.id} Offline</span>
		{/if}
	</div>
{/if}
