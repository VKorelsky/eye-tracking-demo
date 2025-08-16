<script lang="ts">
	import { onMount } from 'svelte';
	import webgazer, { type GazeData, type GazeListener } from 'webgazer';

	// const normalize = (gazeX: number, canvasLeft: number, canvasWidth: number): number => {
	// 	const canvasRelativeX = gazeX - canvasLeft;
	// 	const normalizedPos = (canvasRelativeX / canvasWidth) * 2 - 1;
	// 	return Math.max(-1, Math.min(1, normalizedPos));
	// };

	// do this processing prior to uploading to server
	// const rect = canvas.getBoundingClientRect();
	// const pos = normalize(data.x, rect.left, canvas.offsetWidth);
	// const sample_time = exerciseStartTime + elapsedTimeMs;

	// const sample: GazeDataPoint = { pos, sample_time };
	// sessionData.push(sample);

	type AppState = 'ready' | 'calibration' | 'exercise' | 'completed';
	let appState: AppState = $state('ready');

	let exerciseStartTime: number = $state(0);
	let timeRemaining: number = $state(10);

	type RecordingSample = GazeData & { elapsedMs: number };
	let sessionData = $state<RecordingSample[]>([]);

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
	let timerInterval: ReturnType<typeof setInterval>;

	onMount(() => {
		ctx = canvas.getContext('2d');
		drawCanvas();
	});

	function drawCanvas() {
		if (!ctx) return;

		ctx!.clearRect(0, 0, canvas.width, canvas.height);

		if (appState === 'calibration') {
			drawCalibrationPoints();
		}

		requestAnimationFrame(drawCanvas);
	}

	function drawCalibrationPoints() {
		if (!ctx) return;

		// Find the first non-completed point
		const activePoint = calibrationPoints.find((p) => !p.completed);
		if (!activePoint) return;

		const x = (activePoint.x / 100) * canvas.width;
		const y = (activePoint.y / 100) * canvas.height;

		ctx!.beginPath();
		ctx!.arc(x, y, 20, 0, 2 * Math.PI);

		if (activePoint.clicks >= 4) {
			ctx!.fillStyle = '#F59E0B'; // Yellow (almost done)
		} else if (activePoint.clicks >= 1) {
			ctx!.fillStyle = '#FCA5A5'; // Light red (progress)
		} else {
			ctx!.fillStyle = '#EF4444'; // Red (start)
		}

		ctx!.fill();
		ctx!.strokeStyle = '#374151';
		ctx!.lineWidth = 2;
		ctx!.stroke();

		// Draw click count
		ctx!.fillStyle = '#FFFFFF';
		ctx!.font = '14px monospace';
		ctx!.textAlign = 'center';
		ctx!.fillText(`${activePoint.clicks}/5`, x, y + 5);
	}

	const gazeListenerCallback: GazeListener = (data, elapsedTimeMs) => {
		if (data && appState === 'exercise') {
			sessionData.push({ x: data.x, y: data.y, elapsedMs: elapsedTimeMs });
		}
	};

	function startCalibration() {
		appState = 'calibration';

		webgazer.params.moveTickSize = 5;
		webgazer.params.dataTimestep = 5;
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

		// Find the currently active point (first non-completed)
		const activePointIndex = calibrationPoints.findIndex((p) => !p.completed);
		if (activePointIndex === -1) return; // All points completed

		const activePoint = calibrationPoints[activePointIndex];

		// Check if click is within tolerance of active point
		if (
			Math.abs(clickXPercent - activePoint.x) < 10 &&
			Math.abs(clickYPercent - activePoint.y) < 10
		) {
			// Add data point to web gazer training
			webgazer.recordScreenPosition(event.clientX, event.clientY, 'click');

			activePoint.clicks++;
			if (activePoint.clicks >= 5) {
				activePoint.completed = true;
			}
			calibrationPoints[activePointIndex] = activePoint;
		}

		// Check if all points are calibrated
		if (calibrationPoints.every((p) => p.completed)) {
			startExercise();
		}
	}

	function startTimer() {
		timerInterval = setInterval(() => {
			timeRemaining--;
			if (timeRemaining <= 0) {
				endExercise();
			}
		}, 1000);
	}

	function endExercise() {
		appState = 'completed';
		clearInterval(timerInterval);
		webgazer.end();
		console.log('Session completed. Normalized gaze data:', sessionData);
	}

	function startExercise() {
		appState = 'exercise';
		exerciseStartTime = performance.now();
		webgazer.removeMouseEventListeners().setGazeListener(gazeListenerCallback);
		startTimer();
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
					Calibration: Click the red circle 5 times
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
					<div class="text-gray-600">
						Collected {sessionData.length} gaze points over {10} seconds
					</div>
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
