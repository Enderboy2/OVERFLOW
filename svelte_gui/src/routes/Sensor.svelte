<script>
	import { onMount } from 'svelte';

	// Dummy initial data
	let pressureData = {
		pressure: 1013,
		depth: 10
	};

	let imuData = {
		roll: 30,
		pitch: 15,
		yaw: 45
	};

	// Function to generate random data
	function generateRandomData() {
		pressureData.pressure = Math.floor(Math.random() * 2000) + 800; // Random pressure between 800hPa and 2800hPa
		pressureData.depth = Math.floor(Math.random() * 30); // Random depth between 0m and 30m
		imuData.roll = Math.floor(Math.random() * 360); // Roll between 0 and 360 degrees
		imuData.pitch = Math.floor(Math.random() * 360); // Pitch between 0 and 360 degrees
		imuData.yaw = Math.floor(Math.random() * 360); // Yaw between 0 and 360 degrees
	}

	// Update data every 2 seconds
	onMount(() => {
		const interval = setInterval(generateRandomData, 2000);
		return () => clearInterval(interval);
	});
</script>

<div class="mx-auto max-w-xs rounded-lg bg-black p-4 shadow-md">
	<h1 class="mb-2 text-lg font-bold text-white">Sensor Data</h1>

	<div class="mb-4">
		<h2 class="text-md font-semibold text-gray-300">Pressure Sensor</h2>
		<div class="rounded-lg bg-green-400 p-2">
			<p class="text-sm text-gray-200">
				Pressure: <span class="font-bold">{pressureData.pressure} hPa</span>
			</p>
			<p class="text-sm text-gray-200">
				Depth: <span class="font-bold">{pressureData.depth} m</span>
			</p>
		</div>
	</div>

	<div>
		<h2 class="text-md font-semibold text-gray-300">IMU Data</h2>
		<div class="rounded-lg bg-red-400 p-2">
			<p class="text-sm text-gray-200">Roll: <span class="font-bold">{imuData.roll}°</span></p>
			<p class="text-sm text-gray-200">Pitch: <span class="font-bold">{imuData.pitch}°</span></p>
			<p class="text-sm text-gray-200">Yaw: <span class="font-bold">{imuData.yaw}°</span></p>
		</div>
	</div>
</div>
