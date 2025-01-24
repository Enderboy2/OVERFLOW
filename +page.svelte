<script>
	import { onMount } from 'svelte';
	import Camera from './Camera.svelte';
	import Sensor from './Sensor.svelte';
	import Timer from './timer.svelte';

	let cameraFeedsLeft = [
		{
			id: 1,
			url: 'http://camera1-url.com'
		},
		{ id: 2, url: 'http://camera2-url.com' },
		{ id: 3, url: 'http://camera3-url.com' }
	];

	let cameraFeedsRight = [
		{ id: 4, url: 'http://camera4-url.com' },
		{ id: 5, url: 'http://camera5-url.com' },
		{ id: 6, url: 'http://camera6-url.com' }
	];
	let primaryCamera = 1;
	let primaryCameraFeed = cameraFeedsLeft.find((feed) => feed.id === 1);

	let cameraStates = new Array(cameraFeedsLeft.length + cameraFeedsRight.length).fill('offline'); // Default to offline
	let statusMessage = '';
	let allOnline = false;
	let allOffline = false;
	let showContent = false; // Control the opening animation

	const checkTimeout = 5000; // Time to wait before marking as offline

	onMount(() => {
		setTimeout(() => (showContent = true), 500); // Opening animation trigger

		cameraFeedsLeft.forEach((feed, index) => {
			const img = new Image();
			let resolved = false;

			// Handle successful load
			img.onload = () => {
				if (!resolved) {
					resolved = true;
					cameraStates[index] = 'online';
					updateStatus();
				}
			};

			// Handle error
			img.onerror = () => {
				if (!resolved) {
					resolved = true;
					cameraStates[index] = 'offline';
					updateStatus();
				}
			};

			// Fallback in case neither event fires
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
		allOnline = cameraStates.every((state) => state === 'online');
		allOffline = cameraStates.every((state) => state === 'offline');

		if (allOnline) {
			statusMessage = 'All cameras are online';
		} else if (allOffline) {
			statusMessage = 'All cameras are offline';
		} else {
			statusMessage = 'Some cameras are offline';
		}
	}

	function setPrimaryCamera(pc) {
		primaryCamera = pc;
		if (pc <= 3) {
			primaryCameraFeed = cameraFeedsLeft.find((feed) => feed.id === pc);
		} else {
			primaryCameraFeed = cameraFeedsRight.find((feed) => feed.id === pc);
		}

		console.log(primaryCameraFeed);
	}
</script>

{#if primaryCameraFeed.id}
	<main class="flex min-h-screen flex-col items-center justify-center bg-black text-white">
		<h1
			class={`mb-1 text-4xl font-bold transition-all ${
				showContent ? 'translate-y-0 opacity-100' : '-translate-y-6 opacity-0'
			}`}
			style="transition-duration: 1s;"
		>
			OVERFLOW
		</h1>
		<button class="mb-4 rounded-md bg-green-400 px-3 py-1">Start</button>
		<p
			class={`mb-6 text-lg font-medium transition-all ${
				showContent
					? allOnline
						? 'translate-y-0 text-green-600 opacity-100'
						: allOffline
							? 'translate-y-0 text-red-600 opacity-100'
							: 'translate-y-0 text-yellow-600 opacity-100'
					: 'translate-y-6 opacity-0'
			}`}
			style="transition-duration: 1s;"
		>
			{statusMessage}
		</p>

		{#key cameraStates}
			<div class="flex w-screen">
				<div
					class={`flex w-80 max-w-screen-lg flex-col gap-6 px-4 transition-opacity duration-1000 ${
						showContent ? 'opacity-100' : 'opacity-0'
					}`}
				>
					{#each cameraFeedsLeft as feed, i}
						<Camera {feed} {i} {cameraStates} {setPrimaryCamera} />
					{/each}
					<div>
						<Sensor />
					</div>
				</div>

				<div class="flex aspect-video w-full items-center justify-center">
					{#key primaryCameraFeed}
						<img
							class="h-full w-full"
							src={primaryCameraFeed.url}
							alt={'Camera' + primaryCameraFeed.id}
						/>
					{/key}
				</div>

				<div
					class={`flex w-80 max-w-screen-lg flex-col gap-6 px-4 transition-opacity duration-1000 ${
						showContent ? 'opacity-100' : 'opacity-0'
					}`}
				>
					{#each cameraFeedsRight as feed, i}
						<Camera {feed} {cameraStates} {setPrimaryCamera} />
					{/each}
					<div>
						<Timer />
					</div>
				</div>
			</div>
		{/key}
	</main>
{/if}
