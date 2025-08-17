<script lang="ts">
	import { goto } from '$app/navigation';
	import RecordingCanvas from '$lib/components/TrackingCanvas.svelte';
	import type { RecordingSessionData } from '$lib/types';

	let saveError: string | null = $state(null);

	async function handleEnd(payload: RecordingSessionData) {
		saveError = null;
		try {			
			const response = await fetch('/api/sessions', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});
			if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
			const result = await response.json();
			goto(`/sessions/${result.id}`);
		} catch (error) {
			saveError = error instanceof Error ? error.message : 'Failed to save session.';
		}
	}

	function startNewRecording() {
		// this will overwrite existing data, works for the poc
		window.location.reload();
	}
</script>

<div class="flex min-h-screen w-full flex-col pt-10">
	<div class="m-8 text-center">
		<h1 class="text-2xl font-bold text-gray-900">New Session</h1>
	</div>

	{#if saveError}
		<div
			class="mx-auto mb-4 w-full max-w-3xl rounded-md border border-red-200 bg-red-50 p-4 text-red-700"
		>
			<div class="flex items-center justify-between">
				<div>
					<strong class="font-semibold">Save failed:</strong>
					{saveError}
				</div>
				<button
					onclick={startNewRecording}
					class="rounded-md bg-red-600 px-3 py-1 text-sm font-medium text-white hover:bg-red-700"
				>
					Abandon this session and start a new one
				</button>
			</div>
		</div>
	{/if}

	<div class="m-8 flex flex-1 flex-col items-center justify-center">
		<RecordingCanvas onend={handleEnd} />
	</div>
</div>
