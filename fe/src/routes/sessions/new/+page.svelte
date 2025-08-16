<script lang="ts">
	import { onMount } from 'svelte';
	import webgazer, { type GazeData, type GazeListener } from 'webgazer';

	type AppState = 'ready' | 'calibration' | 'exercise' | 'completed';
	let appState: AppState = $state('ready');
	let sessionId: string = $state('');

	let exerciseStartTime: number = $state(0);
	let timeRemaining: number = $state(20);

	type GazeDataPoint = GazeData & { sample_time: number };
	let sessionData = $state<GazeDataPoint[]>([]);

	// TODO -> move these into separate components
	// Calibration state
	type CalibrationPoint = {
		x: number; // percentage of canvas width
		y: number; // percentage of canvas height
		clicks: number;
		completed: boolean;
	};

	let calibrationPoints = $state<CalibrationPoint[]>([
		{ x: 25, y: 50, clicks: 0, completed: false }, // Left
		{ x: 50, y: 50, clicks: 0, completed: false }, // Center
		{ x: 75, y: 50, clicks: 0, completed: false } // Right
	]);

	let canvas: HTMLCanvasElement;

	let ctx: CanvasRenderingContext2D | null = null;

	// Exercise state
	let dotX: number = $state(10); // percentage of canvas width
	let animationId: number;
	let timerInterval: ReturnType<typeof setInterval>;

	onMount(() => {
		sessionId = crypto.randomUUID();
	
		ctx = canvas.getContext('2d');
		// smooth predictions
		webgazer.applyKalmanFilter(true);
		drawCanvas();
	});

	function drawCanvas() {
		if (!ctx) return;

		// Clear canvas
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		if (appState === 'calibration') {
			drawCalibrationPoints();
		} else if (appState === 'exercise') {
			drawMovingDot();
		}

		requestAnimationFrame(drawCanvas);
	}

	function drawCalibrationPoints() {
		if (!ctx) return;

		calibrationPoints.forEach((point) => {
			const x = (point.x / 100) * canvas.width;
			const y = (point.y / 100) * canvas.height;

			ctx.beginPath();
			ctx.arc(x, y, 20, 0, 2 * Math.PI);

			if (point.completed) {
				ctx.fillStyle = '#10B981'; // Green
			} else if (point.clicks >= 1) {
				ctx.fillStyle = '#F59E0B'; // Yellow
			} else {
				ctx.fillStyle = '#EF4444'; // Red
			}

			ctx.fill();
			ctx.strokeStyle = '#374151';
			ctx.lineWidth = 2;
			ctx.stroke();

			// Draw click count
			ctx.fillStyle = '#FFFFFF';
			ctx.font = '14px monospace';
			ctx.textAlign = 'center';
			ctx.fillText(`${point.clicks}/3`, x, y + 5);
		});
	}

	function drawMovingDot() {
		if (!ctx) return;

		const x = (dotX / 100) * canvas.width;
		const y = canvas.height / 2;

		ctx.beginPath();
		ctx.arc(x, y, 15, 0, 2 * Math.PI);
		ctx.fillStyle = '#3B82F6'; // Blue
		ctx.fill();
		ctx.strokeStyle = '#1E40AF';
		ctx.lineWidth = 3;
		ctx.stroke();
	}

	const normalize = (data: GazeData): GazeData => {
		return data;
	};

	const gazeListenerCallback: GazeListener = (data, elapsedTimeMs) => {
		if (data == null || appState !== 'exercise') {
			return;
		}

		const sample_coordinates = normalize(data);
		const sample_time = exerciseStartTime + elapsedTimeMs;

		const sample: GazeDataPoint = { ...sample_coordinates, sample_time };
		sessionData.push(sample);
	};

	function startCalibration() {
		appState = 'calibration';
		webgazer.showPredictionPoints(true).begin();
	}

	function handleCanvasClick(event: MouseEvent) {
		if (appState !== 'calibration') return;

		const rect = canvas.getBoundingClientRect();
		const canvasX = event.clientX - rect.left;
		const canvasY = event.clientY - rect.top;

		// Convert canvas coordinates to percentages
		const clickXPercent = (canvasX / canvas.offsetWidth) * 100;
		const clickYPercent = (canvasY / canvas.offsetHeight) * 100;

		// Find clicked calibration point (within 10% tolerance)
		for (let i = 0; i < calibrationPoints.length; i++) {
			const point = calibrationPoints[i];
			if (
				!point.completed &&
				Math.abs(clickXPercent - point.x) < 10 &&
				Math.abs(clickYPercent - point.y) < 10
			) {
				// Record screen position for WebGazer
				webgazer.recordScreenPosition(event.clientX, event.clientY, 'click');

				point.clicks++;
				if (point.clicks >= 3) {
					point.completed = true;
				}
				calibrationPoints[i] = point;
				break;
			}
		}

		// Check if all points are calibrated
		if (calibrationPoints.every((p) => p.completed)) {
			startExercise();
		}
	}

	function startExercise() {
		appState = 'exercise';
		exerciseStartTime = performance.now();
		webgazer.setGazeListener(gazeListenerCallback);
		startTimer();
		startDotAnimation();
	}

	function startTimer() {
		timerInterval = setInterval(() => {
			timeRemaining--;
			if (timeRemaining <= 0) {
				endExercise();
			}
		}, 1000);
	}

	function startDotAnimation() {
		const animate = () => {
			if (appState !== 'exercise') return;

			// Move dot from 10% to 90% and back over 45 seconds
			const elapsed = (performance.now() - exerciseStartTime) / 1000;
			const progress = elapsed / 45;

			if (progress <= 0.5) {
				// First half: left to right
				dotX = 10 + progress * 2 * 80;
			} else {
				// Second half: right to left
				dotX = 90 - (progress - 0.5) * 2 * 80;
			}

			animationId = requestAnimationFrame(animate);
		};
		animate();
	}

	function endExercise() {
		appState = 'completed';
		clearInterval(timerInterval);
		cancelAnimationFrame(animationId);
		webgazer.end();
		console.log('Session completed. Data:', sessionData);
	}

	function resetSession() {
		appState = 'ready';
		timeRemaining = 45;
		sessionData.length = 0;
		calibrationPoints.forEach((point) => {
			point.clicks = 0;
			point.completed = false;
		});
		webgazer.end();
	}
</script>

<div class="flex min-h-screen w-full flex-col pt-10">
	<div class="m-8 text-center">
		<h1 class="text-2xl font-bold text-gray-900">New Session</h1>
		<p class="mt-2 text-sm text-gray-600">
			Session ID: <span class="font-mono text-blue-600">{sessionId}</span>
			<br />
			State: <span class="font-mono text-blue-600">{appState}</span>
		</p>
	</div>

	<div class="m-8 flex flex-1 flex-col items-center justify-center">
		<div class="flex flex-col items-center space-y-8">
			{#if appState === 'exercise'}
				<div class="text-2xl font-bold text-blue-600">
					Time Remaining: {timeRemaining}s
				</div>
			{/if}

			{#if appState === 'calibration'}
				<div class="mb-4 text-lg font-medium text-gray-700">
					Calibration: Click each red circle twice
				</div>
			{/if}

			<canvas
				bind:this={canvas}
				width="1200"
				height="200"
				onclick={handleCanvasClick}
				class="h-auto max-w-full cursor-pointer rounded-3xl border-2 border-gray-300 bg-white shadow-lg"
			></canvas>

			{#if appState === 'ready'}
				<button
					onclick={startCalibration}
					class="rounded-lg bg-blue-500 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-600"
				>
					Start Session
				</button>
			{:else if appState === 'completed'}
				<div class="space-y-4 text-center">
					<div class="text-xl font-bold text-green-600">Session Completed!</div>
					<div class="text-gray-600">Collected {sessionData.length} gaze points</div>
					<button
						onclick={resetSession}
						class="rounded-lg bg-gray-500 px-6 py-3 font-medium text-white transition-colors hover:bg-gray-600"
					>
						Start New Session
					</button>
				</div>
			{/if}
		</div>
	</div>
</div>
