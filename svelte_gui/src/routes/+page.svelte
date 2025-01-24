<script>
	let joystickData = {};

	const connectToWebSocket = () => {
		const socket = new WebSocket('ws://localhost:8765');

		socket.onopen = () => {
			console.log('Connected to joystick WebSocket');
		};

		socket.onmessage = (event) => {
			joystickData = JSON.parse(event.data);
		};

		socket.onerror = (error) => {
			console.error('WebSocket error:', error);
		};

		socket.onclose = () => {
			console.log('WebSocket connection closed, attempting to reconnect...');
			setTimeout(connectToWebSocket, 5000); // Reconnect after 5 seconds
		};
	};

	connectToWebSocket();
</script>

<div>
	<h1>Joystick Data</h1>
	<pre>{JSON.stringify(joystickData, null, 2)}</pre>
</div>
