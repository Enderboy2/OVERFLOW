<script>
	let timer = 900; // Timer starts at 15 minutes (900 seconds)
	let isRunning = false;
	let interval;

	function startTimer() {
		if (isRunning) return; // Prevent multiple intervals
		isRunning = true;
		interval = setInterval(() => {
			if (timer > 0) {
				timer--; // Decrement the timer
			} else {
				clearInterval(interval); // Stop the interval when the timer reaches 0
				isRunning = false;
			}
		}, 1000);
	}

	function pauseTimer() {
		clearInterval(interval); // Pause the timer by clearing the interval
		isRunning = false;
	}

	function resetTimer() {
		clearInterval(interval); // Clear the interval
		timer = 900; // Reset to 15 minutes
		isRunning = false;
	}

	$: progress = ((900 - timer) / 900) * 100; // Calculate progress percentage
	$: formattedTime = `${String(Math.floor(timer / 60)).padStart(2, '0')}:${String(timer % 60).padStart(2, '0')}`;
</script>

<div class="flex flex-col items-center justify-center gap-1 p-4">
	<h1 class="text-lg font-bold">engz ya 3ars</h1>
	<h2 class="font-mono text-5xl">{formattedTime}</h2>

	<div class="h-4 w-full rounded-full bg-gray-200">
		<div
			class="h-4 rounded-full bg-red-500 transition-all duration-200"
			style="width: {progress}%"
		></div>
	</div>

	<div class="mt-4 flex gap-2">
		<button on:click={startTimer} class="rounded-md bg-red-500 p-2 text-white hover:bg-green-500">
			Start
		</button>
		<button on:click={pauseTimer} class="rounded-md bg-blue-500 p-2 text-white hover:bg-yellow-500">
			Pause
		</button>
		<button on:click={resetTimer} class="rounded-md bg-gray-400 p-2 text-white hover:bg-red-500">
			Reset
		</button>
	</div>
</div>
