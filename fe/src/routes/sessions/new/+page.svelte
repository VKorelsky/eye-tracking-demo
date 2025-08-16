<script lang="ts">
	import { onMount } from 'svelte';
	import webgazer, { type GazeData, type GazeListener } from 'webgazer';

	let recording: boolean = $state(false);
	let recordingStartTime: number = $state(performance.now());
	let sessionId: string = $state('');

	type GazeDataPoint = GazeData & { sample_time: number };
	let sessionData = $state<GazeDataPoint[]>([]);

	onMount(() => {
		sessionId = crypto.randomUUID();
		console.log(sessionId);
		webgazer.showPredictionPoints(true)
	});

	const normalize = (data: GazeData): GazeData => {
		return data;
	};

	const gazeListenerCallback: GazeListener = (data, elapsedTimeMs) => {
		if (data == null) {
			return;
		}

		const sample_coordinates = normalize(data);
		const sample_time = recordingStartTime + elapsedTimeMs;

		const sample: GazeDataPoint = { ...sample_coordinates, sample_time };

		sessionData.push(sample);
	};

	function startSession() {
		recording = true;
		webgazer.setGazeListener(gazeListenerCallback).begin();
		recordingStartTime = performance.now();
		console.log('hello world');
	}

	function stopSession() {
		recording = false;
		webgazer.end();
		console.log('hello world');
		console.log(sessionData);
	}
</script>

<div class="flex min-h-screen w-full flex-col pt-10">
	<div class="m-8 text-center">
		<h1 class="text-2xl font-bold text-gray-900">New Session</h1>
		<p class="mt-2 text-sm text-gray-600">
			Session ID: <span class="font-mono text-blue-600">{sessionId}</span>
			<br />
			Recording?: <span class="font-mono text-blue-600">{recording}</span>
		</p>
	</div>

	<div class="m-8 flex flex-1 flex-col items-center justify-center">
		<!-- this should eventually be it's own component -->
		<div class="flex flex-col items-center space-y-8">
			<!-- TODO, make this responsive. Also make it it's own component -->
			<canvas
				width="1200"
				height="200"
				class="rounded-3xl border-2 border-gray-300 bg-white shadow-lg {!recording
					? 'opacity-50'
					: ''}"
			></canvas>

			<button
				onclick={recording? stopSession: startSession}
				class="rounded-lg bg-green-500 px-6 py-3 font-medium text-white transition-colors hover:bg-green-600"
			>
				{recording? "Stop Session" : "Start Session"}
			</button>
		</div>
	</div>
</div>
