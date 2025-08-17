<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import webgazer, { type GazeData, type GazeListener } from 'webgazer';

	// todo move into library method
	const normalize = (gazeX: number, canvasLeft: number, canvasWidth: number): number => {
		const canvasRelativeX = gazeX - canvasLeft;
		const normalizedPos = (canvasRelativeX / canvasWidth) * 2 - 1;
		return Math.max(-1, Math.min(1, normalizedPos));
	};

	type AppState = 'ready' | 'calibration' | 'recording' | 'paused' | 'saving' | 'completed';
	let appState: AppState = $state('ready');
	let isRecording = $state(false);

	let exerciseStartTime: number = $state(0);

	type RecordingSample = GazeData & { elapsedMs: number; valid: boolean };
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
			startRecording();
		}
	}

	// recording logic
	const gazeListenerCallback: GazeListener = (data, elapsedTimeMs) => {
		if (data && appState === 'recording' && isRecording) {
			sessionData.push({ x: data.x, y: data.y, elapsedMs: elapsedTimeMs, valid: true });
		}
	};

	function handleKeydown(event: KeyboardEvent) {
		if (event.code === 'Space' && (appState === 'recording' || appState === 'paused')) {
			event.preventDefault();
			toggleRecording();
		}
	}

	function startRecording() {
		appState = 'recording';
		isRecording = true;
		exerciseStartTime = performance.now();

		webgazer.params.moveTickSize = 10;
		webgazer.params.dataTimestep = 10;
		webgazer.params.applyKalmanFilter = true;
		webgazer.params.showFaceOverlay = false;
		webgazer.params.showFaceFeedbackBox = false;

		webgazer.showPredictionPoints(true);
		webgazer.showVideo(false);

		webgazer.removeMouseEventListeners().setGazeListener(gazeListenerCallback);
	}

	function toggleRecording() {
		if (appState === 'recording') {
			appState = 'paused';
			isRecording = false;
			webgazer.pause()
		} else if (appState === 'paused') {
			appState = 'recording';
			isRecording = true;
			webgazer.resume();
		}
	}

	async function persistSession() {
		if (sessionData.length === 0) return;

		appState = 'saving';

		try {
			const rect = canvas.getBoundingClientRect();
			const samples = sessionData.map((sample) => ({
				timestamp: new Date(exerciseStartTime + sample.elapsedMs).toISOString(),
				pos: normalize(sample.x, rect.left, canvas.offsetWidth)
			}));

			// TODO sample rate
			const sessionData_api = {
				accuracy: 80,
				sample_rate: 100,
				samples: samples
			};

			const response = await fetch('/api/sessions', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(sessionData_api)
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const result = await response.json();
			webgazer.end();
			goto(`/sessions/${result.id}`);
		} catch (error) {
			console.error('Failed to save session:', error);
			appState = 'recording';
		}
	}

	function resetSession() {
		appState = 'ready';
		isRecording = false;
		sessionData.length = 0;
		calibrationPoints.forEach((point) => {
			point.clicks = 0;
			point.completed = false;
		});
		webgazer.end();
	}
</script>

<svelte:window onkeydown={handleKeydown} />
<div class="flex min-h-screen w-full flex-col pt-10">
	<div class="m-8 text-center">
		<h1 class="text-2xl font-bold text-gray-900">New Session</h1>
		<p class="mt-2 text-sm text-gray-600">
			State: <span class="font-mono text-blue-600">{appState}</span>
		</p>
	</div>

	<div class="m-8 flex flex-1 flex-col items-center justify-center">
		<div class="flex flex-col items-center space-y-8">
			{#if appState === 'recording'}
				<div class="text-2xl font-bold text-blue-600">Recording... Press SPACEBAR to stop</div>
			{:else if appState === 'paused'}
				<div class="text-2xl font-bold text-orange-600">Recording Paused</div>
			{:else if appState === 'saving'}
				<div class="text-2xl font-bold text-green-600">Saving Session...</div>
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
			{:else if appState === 'recording' || appState === 'paused'}
				<div class="flex space-x-4">
					<button
						onclick={toggleRecording}
						class="rounded-lg px-6 py-3 font-medium text-white transition-colors {appState ===
						'recording'
							? 'bg-orange-500 hover:bg-orange-600'
							: 'bg-blue-500 hover:bg-blue-600'}"
					>
						{appState === 'recording' ? 'Pause Recording' : 'Resume Recording'}
					</button>
					<button
						onclick={persistSession}
						disabled={sessionData.length === 0}
						class="rounded-lg bg-green-500 px-6 py-3 font-medium text-white transition-colors hover:bg-green-600 disabled:cursor-not-allowed disabled:bg-gray-400"
					>
						Save Session ({sessionData.length} samples)
					</button>
				</div>
			{:else if appState === 'saving'}
				<div class="flex items-center space-x-2">
					<div
						class="h-6 w-6 animate-spin rounded-full border-2 border-green-500 border-t-transparent"
					></div>
					<span class="text-lg font-medium text-green-600">Saving...</span>
				</div>
			{/if}
		</div>
	</div>
</div>
