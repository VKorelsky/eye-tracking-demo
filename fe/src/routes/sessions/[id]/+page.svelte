<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { page } from '$app/state';
	import TimeSeriesChart from '$lib/components/TimeSeriesChart.svelte';
	import type { RecordingSessionSample } from '$lib/types';

	let sessionId = page.params.id;

	let sessionData: any = $state(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let samples: RecordingSessionSample[] = $state([]);

	onMount(async () => {
		try {
			const response = await fetch(`/api/sessions/${sessionId}`);
			if (!response.ok) {
				throw new Error(`Failed to fetch session: ${response.status}`);
			}
			sessionData = await response.json();

			const rawSamples: RecordingSessionSample[] = sessionData?.samples ?? [];
			samples = rawSamples;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
		}
	});
</script>

<div class="min-h-screen bg-gray-50 p-8">
	<div class="mx-auto max-w-6xl">
		<div class="mb-6 flex items-center gap-4">
			<a href="/sessions" class="flex items-center gap-2 text-blue-600 hover:text-blue-800">
				<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 19l-7-7 7-7"
					/>
				</svg>
				Back to Sessions
			</a>
		</div>
		<h1 class="mb-8 text-3xl font-bold text-gray-900">Session {sessionId}</h1>

		{#if loading}
			<p class="text-gray-600">Loading session data...</p>
		{:else if error}
			<p class="text-red-600">Error: {error}</p>
		{:else if sessionData}
			<div class="mb-6 rounded-lg bg-white p-6 shadow-md">
				<h2 class="mb-4 text-xl font-semibold">Session Summary</h2>
				<div class="mb-6 space-y-4">
					<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
						<div class="rounded-lg bg-gray-50 p-4">
							<div class="text-sm text-gray-600">Sample Rate</div>
							<div class="text-2xl font-bold text-gray-900">{sessionData.sample_rate} Hz</div>
						</div>
						<div class="rounded-lg bg-gray-50 p-4">
							<div class="text-sm text-gray-600">Total Samples</div>
							<div class="text-2xl font-bold text-gray-900">{samples.length}</div>
						</div>
						<div class="rounded-lg bg-gray-50 p-4">
							<div class="text-sm text-gray-600">Session duration (including pauses)</div>
							<div class="text-2xl font-bold text-gray-900">
								<!-- assumes seconds -->
								{sessionData.duration}s
							</div>
						</div>
					</div>
					<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
						<div class="rounded-lg bg-gray-50 p-4">
							<div class="text-sm text-gray-600">Recorded At</div>
							<div class="text-sm font-medium text-gray-900">
								{new Date(sessionData.created_at).toLocaleString()}
							</div>
						</div>
						<div class="rounded-lg bg-gray-50 p-4">
							<div class="text-sm text-gray-600">User Agent</div>
							<div
								class="truncate text-sm font-medium text-gray-900"
								title={sessionData.user_agent}
							>
								{sessionData.user_agent}
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="mb-6 rounded-lg bg-white p-6 shadow-md">
				<div class="mb-4 flex items-center justify-between">
					<h2 class="text-xl font-semibold">Eye Tracking Data</h2>
					{#if samples.length > 0}
						<a
							href={`/api/sessions/${sessionId}/export`}
							download={`session_${sessionId}.csv`}
							class="rounded bg-gray-800 px-3 py-1 text-sm text-white transition-colors hover:bg-black"
						>
							Export data as CSV
						</a>
					{/if}
				</div>
				{#if samples.length > 0}
					<TimeSeriesChart data={samples} />
				{:else}
					<p class="text-gray-600">No tracking data available for this session.</p>
				{/if}
			</div>
		{/if}
	</div>
</div>
