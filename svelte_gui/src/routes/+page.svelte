<script>
	import { onMount } from 'svelte';
	import Camera from './Camera.svelte';
	import Sensor from './Sensor.svelte';
	import Timer from './timer.svelte';

	let cameraFeedsLeft = [
		{
			id: 1,
			url: 'http://192.168.137.47:8080/?action=stream'
		},
		{
			id: 2,
			url: 'http://192.168.137.47:8081/?action=stream'
		},
		{ id: 3, url: 'http://192.168.137.47:8082/?action=stream' }
	];

	let cameraFeedsRight = [
		{ id: 4, url: 'http://192.168.137.47:8083/?action=stream' },
		{ id: 5, url: 'http://192.168.137.47:8084/?action=stream' },
		{ id: 6, url: 'http://192.168.137.47:8085/?action=stream' }
	];

	let primaryCamera = 1;
	let primaryCameraFeeds = [cameraFeedsLeft.find((feed) => feed.id === 1),cameraFeedsLeft.find((feed) => feed.id === 2),cameraFeedsLeft.find((feed) => feed.id === 3)];
	let secondaryCameras = [null, null]; // Placeholder for secondary cameras (2 and 3)

	let cameraStates = new Array(cameraFeedsLeft.length + cameraFeedsRight.length).fill('offline');
	let statusMessage = '';
	let showContent = false;

	const checkTimeout = 5000;

	onMount(() => {
		setTimeout(() => (showContent = true), 500);

		cameraFeedsLeft.forEach((feed, index) => {
			const img = new Image();
			let resolved = false;

			img.onload = () => {
				if (!resolved) {
					resolved = true;
					cameraStates[index] = 'online';
					updateStatus();
				}
			};

			img.onerror = () => {
				if (!resolved) {
					resolved = true;
					cameraStates[index] = 'offline';
					updateStatus();
				}
			};

			setTimeout(() => {
				if (!resolved) {
					resolved = true;
					cameraStates[index] = 'offline';
					updateStatus();
				}
			}, checkTimeout);

			img.src = feed.url;
		});
	});

	function updateStatus() {
		statusMessage = cameraStates.every((state) => state === 'online')
			? 'All cameras are online'
			: cameraStates.every((state) => state === 'offline')
				? 'All cameras are offline'
				: 'Some cameras are offline';
	}

	function setPrimaryCamera(id, position) {
		if (position === 1) {
			primaryCamera = id;
			primaryCameraFeeds[0] =
				cameraFeedsLeft.find((feed) => feed.id === id) ||
				cameraFeedsRight.find((feed) => feed.id === id);
		} else if (position === 2 || position === 3) {
			secondaryCameras[position - 2] =
				cameraFeedsLeft.find((feed) => feed.id === id) ||
				cameraFeedsRight.find((feed) => feed.id === id);
		}else if (position === 4){
			primaryCameraFeeds[1] = cameraFeedsLeft.find((feed) => feed.id === id) ||
			cameraFeedsRight.find((feed) => feed.id === id);
		}else if (position === 5){
			primaryCameraFeeds[2] = cameraFeedsLeft.find((feed) => feed.id === id) ||
			cameraFeedsRight.find((feed) => feed.id === id);
		}
	}
</script>

<main class="flex min-h-screen flex-col items-center justify-center bg-black text-white">
	<!-- <div class="fixed left-0 top-0 flex w-full justify-center">
		<h1 class="mb-4 text-4xl font-bold transition-all" style="transition-duration: 1s;">
			OVERFLOW
		</h1>
		<p class="mb-4 text-lg font-medium transition-all" style="transition-duration: 1s;">
			{statusMessage}
		</p>
	</div> -->

	<div class="flex w-screen">
		<!-- Left cameras -->
		<div class="flex w-80 flex-col gap-6 px-4 opacity-0 hover:opacity-100 transition duration-300 absolute left-1">
			{#each cameraFeedsLeft as feed, i}
				<div
					class="group relative"
					on:mouseover={() => (hoveredCamera = feed.id)}
					on:mouseleave={() => (hoveredCamera = null)}
				>
					<Camera {feed} {cameraStates} />
					<div
						class="absolute bottom-0 right-0 hidden gap-1 bg-transparent p-2 transition-all duration-200 group-hover:block"
					>
						<button
							class="rounded-md bg-red-500 p-3 transition-all duration-200 hover:bg-opacity-50"
							on:click={() => setPrimaryCamera(feed.id, 1)}>1</button
						>
						<button
							class="rounded-md bg-red-500 p-3 transition-all duration-200 hover:bg-opacity-50"
							on:click={() => setPrimaryCamera(feed.id, 2)}>2</button
						>
						<button
							class="rounded-md bg-red-500 p-3 transition-all duration-200 hover:bg-opacity-50"
							on:click={() => setPrimaryCamera(feed.id, 3)}>3</button
						>
					</div>
				</div>
			{/each}
			<Sensor />
		</div>

		<!-- Primary and secondary cameras -->
		<!-- Primary and secondary cameras -->
<div class="flex w-screen flex-col items-center justify-center gap-4">
    <!-- Top Row: 3 Cameras -->
    <div class="flex min-h-[60vh] w-full gap-4">
        <!-- Primary Camera 1 -->
        
        <!-- Primary Camera 2 -->
        <div class="aspect-video w-1/3">
            <img class="h-full w-full aspect-video" src={primaryCameraFeeds[1].url} alt="Primary Camera 2" />
        </div>
		<div class="aspect-video w-1/3">
            <img class="h-full w-full aspect-video" src={primaryCameraFeeds[0].url} alt="Primary Camera 1" />
        </div>
        <!-- Primary Camera 3 -->
        <div class="aspect-video w-1/3">
            <img class="h-full w-full aspect-video" src={primaryCameraFeeds[2].url} alt="Primary Camera 3" />
        </div>
    </div>

    <!-- Bottom Row: 2 Cameras -->
    <div class="flex justify-center gap-4">
        {#each secondaryCameras as camera, index}
            {#if camera}
                <div class="aspect-video w-1/2">
                    <img class="h-[40vh] w-auto aspect-video" src={camera.url} alt={`Secondary Camera ${index + 1}`} />
                </div>
            {:else}
                <div class="flex aspect-video w-1/2 items-center justify-center bg-gray-700 text-gray-400">
                    Empty Slot
                </div>
            {/if}
        {/each}
    </div>
</div>

		<!-- Right cameras -->
		<div class="flex w-80 flex-col gap-6 px-4 opacity-0 hover:opacity-100 transition duration-300">
			{#each cameraFeedsRight as feed, i}
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<!-- svelte-ignore a11y_mouse_events_have_key_events -->
				<div
					class="group relative"
					on:mouseover={() => (hoveredCamera = feed.id)}
					on:mouseleave={() => (hoveredCamera = null)}
				>
					<Camera {feed} {cameraStates} />
					<div
						class="absolute bottom-0 right-0 hidden gap-1 bg-transparent p-2 transition-all duration-200 group-hover:block"
					>
						<button
							class="rounded-md bg-red-500 p-3 transition-all duration-200 hover:bg-opacity-50"
							on:click={() => setPrimaryCamera(feed.id, 1)}>1</button
						>
						<button
							class="rounded-md bg-red-500 p-3 transition-all duration-200 hover:bg-opacity-50"
							on:click={() => setPrimaryCamera(feed.id, 2)}>2</button
						>
						<button
							class="rounded-md bg-red-500 p-3 transition-all duration-200 hover:bg-opacity-50"
							on:click={() => setPrimaryCamera(feed.id, 3)}>3</button
						>
						<button
						class="rounded-md bg-red-500 p-3 transition-all duration-200 hover:bg-opacity-50"
						on:click={() => setPrimaryCamera(feed.id, 4)}>4</button
						>
						<button
							class="rounded-md bg-red-500 p-3 transition-all duration-200 hover:bg-opacity-50"
							on:click={() => setPrimaryCamera(feed.id, 5)}>5</button
						>

					</div>
				</div>
			{/each}
			<Timer />
		</div>
	</div>
</main>
