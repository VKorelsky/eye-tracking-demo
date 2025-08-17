<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import webgazer, { type GazeListener } from 'webgazer';
	import type {
		RecordingSessionState,
		CalibrationPoint,
		RecordingSample,
		RecordingSessionData
	} from '$lib/types';

	let recordingState: RecordingSessionState = $state('ready');

	const { onend = () => {} } = $props<{ onend?: (payload: RecordingSessionData) => void }>();

	let canvas: HTMLCanvasElement | null = null;
	let ctx: CanvasRenderingContext2D | null = null;

	let isRecording = $state(false);
	let sessionData = $state<RecordingSample[]>([]);
	let error = $state<string | null>(null);

	let recordingSessionStartTime: number = $state(performance.now());
	// There may be pauses along the way, and we need to take them into account as we compute the effective sampling rate
	let lastRecordingStartTime: number = $state(performance.now());

	let sampleRates = $state<number[]>([]);

	const normalizeRecordingCoordinates = (
		gazeX: number,
		canvasLeft: number,
		canvasWidth: number
	): number => {
		const canvasRelativeX = gazeX - canvasLeft;
		const normalizedPos = (canvasRelativeX / canvasWidth) * 2 - 1;
		return Math.max(-1, Math.min(1, normalizedPos));
	};

	const computeSampleRateSinceLastPause = (): number => {
		// Take each data point that was recorded since the last pause, and compute the sample rate of thoses
		const startElapsedMs = Math.max(0, lastRecordingStartTime - recordingSessionStartTime);
		const segmentSamples = sessionData.filter((s) => s.elapsedMs >= startElapsedMs);
		if (segmentSamples.length === 0) return 0;

		const lastElapsed = segmentSamples[segmentSamples.length - 1].elapsedMs;
		const durationMs = lastElapsed - startElapsedMs;
		if (durationMs <= 0) return 0;

		return segmentSamples.length / (durationMs / 1000);
	};

	let calibrationPoints = $state<CalibrationPoint[]>([
		{ x: 25, y: 50, clicks: 0, completed: false },
		{ x: 50, y: 50, clicks: 0, completed: false },
		{ x: 75, y: 50, clicks: 0, completed: false }
	]);

	onMount(async () => {
		if (!canvas) return;
		ctx = canvas.getContext('2d');
		drawCanvas();

		// Request camera permission at the start
		try {
			await navigator.mediaDevices.getUserMedia({ video: true });
			const permissions = await navigator.permissions.query({ name: 'camera' as PermissionName });
			if (permissions.state === 'denied') {
				error = 'Camera access denied. Please allow camera access to use eye tracking.';
				return;
			}
		} catch (e) {
			error = 'Camera access denied. Please allow camera access to use eye tracking.';
			console.error(error);
			return;
		}
	});

	function drawCanvas() {
		if (!ctx || !canvas) return;
		ctx.clearRect(0, 0, canvas.width, canvas.height);
		if (recordingState === 'calibration' && webgazer.isReady()) {
			drawCalibrationPoints();
		}
		requestAnimationFrame(drawCanvas);
	}

	// Calibration logic
	function startCalibration() {
		recordingState = 'calibration';
		webgazer.params.moveTickSize = 5;
		webgazer.params.dataTimestep = 5;

		webgazer.showPredictionPoints(true).begin();
	}

	function drawCalibrationPoints() {
		if (!ctx || !canvas) return;
		const activePoint = calibrationPoints.find((p) => !p.completed);
		if (!activePoint) return;
		const x = (activePoint.x / 100) * canvas.width;
		const y = (activePoint.y / 100) * canvas.height;
		ctx.beginPath();
		ctx.arc(x, y, 20, 0, 2 * Math.PI);
		ctx.fillStyle =
			activePoint.clicks >= 4 ? '#F59E0B' : activePoint.clicks >= 1 ? '#FCA5A5' : '#EF4444';
		ctx.fill();
		ctx.strokeStyle = '#374151';
		ctx.lineWidth = 2;
		ctx.stroke();
		ctx.fillStyle = '#FFFFFF';
		ctx.font = '14px monospace';
		ctx.textAlign = 'center';
		ctx.fillText(`${activePoint.clicks}/5`, x, y + 5);
	}

	function handleCanvasClick(event: MouseEvent) {
		if (!canvas || recordingState !== 'calibration') return;

		const rect = canvas.getBoundingClientRect();

		const canvasX = event.clientX - rect.left;
		const canvasY = event.clientY - rect.top;
		const clickXPercent = (canvasX / canvas.offsetWidth) * 100;
		const clickYPercent = (canvasY / canvas.offsetHeight) * 100;

		const activePointIndex = calibrationPoints.findIndex((p) => !p.completed);
		if (activePointIndex === -1) return;
		const activePoint = calibrationPoints[activePointIndex];

		if (
			Math.abs(clickXPercent - activePoint.x) < 10 &&
			Math.abs(clickYPercent - activePoint.y) < 10
		) {
			webgazer.recordScreenPosition(event.clientX, event.clientY, 'click');
			activePoint.clicks++;
			if (activePoint.clicks >= 5) activePoint.completed = true;
			calibrationPoints[activePointIndex] = activePoint;
		}

		// if we are done calibrating start the recording
		if (calibrationPoints.every((p) => p.completed)) {
			startRecording();
		}
	}

	// Recording logic
	function startRecording() {
		recordingState = 'recording';
		isRecording = true;

		recordingSessionStartTime = performance.now();
		lastRecordingStartTime = recordingSessionStartTime;

		// smooth predictions and set samples to be taken every 20ms (ideally)
		webgazer.params.dataTimestep = 20;
		webgazer.params.applyKalmanFilter = true;

		// remove the self video view while recording
		webgazer.params.showFaceOverlay = false;
		webgazer.params.showFaceFeedbackBox = false;
		webgazer.showVideo(false);
		webgazer.showPredictionPoints(true);

		// the webgazer library takes into account the cursor position as it assumes the gaze follows it
		// while we are recording gaze movements from left to right, we disable this.
		webgazer.removeMouseEventListeners().setGazeListener(gazeListenerCallback);
	}

	function toggleRecording() {
		if (recordingState === 'recording') {
			recordingState = 'paused';
			isRecording = false;
			sampleRates = [...sampleRates, computeSampleRateSinceLastPause()];

			webgazer.pause();
		} else if (recordingState === 'paused') {
			recordingState = 'recording';
			isRecording = true;
			lastRecordingStartTime = performance.now();

			webgazer.resume();
		}
	}

	const gazeListenerCallback: GazeListener = (data, elapsedTimeMs) => {
		if (data && recordingState === 'recording' && isRecording) {
			sessionData.push({ x: data.x, y: data.y, elapsedMs: elapsedTimeMs });
		}
	};

	// Process data and send it up the tree
	function completeSession() {
		if (!canvas) return;

		webgazer.end();

		// normalize data
		const rect = canvas.getBoundingClientRect();

		const samples = sessionData.map((sample) => ({
			timestamp: new Date(
				performance.timeOrigin + recordingSessionStartTime + sample.elapsedMs
			).toISOString(),
			pos: normalizeRecordingCoordinates(sample.x, rect.left, canvas!.offsetWidth)
		}));

		const recordingEndTime = performance.now();
		const recordingStartDate = new Date(
			performance.timeOrigin + recordingSessionStartTime
		).toISOString();

		const averageSampleRate = sampleRates.reduce((acc, rate) => acc + rate, 0) / sampleRates.length;

		onend({
			sample_rate: averageSampleRate,
			recorded_at: recordingStartDate,
			// record the duration in seconds
			duration: (recordingEndTime - recordingSessionStartTime) / 1000,
			samples
		});

		recordingState = 'completed';
	}

	onDestroy(() => {
		if (recordingState !== 'ready' && recordingState !== 'completed') {
			webgazer.end();
		}
	});
</script>

<svelte:window
	onkeydown={(e) => {
		if (e.code === 'Space' && (recordingState === 'recording' || recordingState === 'paused')) {
			e.preventDefault();
			toggleRecording();
		}
	}}
/>

<div class="flex flex-col items-center space-y-8">
	{#if recordingState === 'recording'}
		<div class="text-2xl font-bold text-blue-600">Recording... Press SPACEBAR to stop</div>
	{:else if recordingState === 'paused'}
		<div class="text-2xl font-bold text-orange-600">Recording Paused</div>
	{:else if recordingState === 'completed'}
		<div class="text-2xl font-bold text-green-600">Completed</div>
	{/if}

	{#if recordingState === 'calibration'}
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

	{#if error}
		<div class="mt-2 text-sm text-red-600">{error}</div>
	{:else if recordingState === 'ready'}
		<button
			onclick={startCalibration}
			class="rounded-lg bg-blue-500 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-600"
			>Start Session</button
		>
	{:else if recordingState === 'recording' || recordingState === 'paused'}
		<div class="flex space-x-4">
			<button
				onclick={toggleRecording}
				class="rounded-lg px-6 py-3 font-medium text-white transition-colors {recordingState ===
				'recording'
					? 'bg-orange-500 hover:bg-orange-600'
					: 'bg-blue-500 hover:bg-blue-600'}"
			>
				{recordingState === 'recording' ? 'Pause Recording' : 'Resume Recording'}
			</button>
			<button
				onclick={completeSession}
				disabled={sessionData.length === 0}
				class="rounded-lg bg-green-500 px-6 py-3 font-medium text-white transition-colors hover:bg-green-600 disabled:cursor-not-allowed disabled:bg-gray-400"
			>
				Save Session ({sessionData.length} samples)
			</button>
		</div>
	{/if}
</div>
