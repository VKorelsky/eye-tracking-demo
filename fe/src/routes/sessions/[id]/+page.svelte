<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';

	let sessionId = page.params.id;
	
	let sessionData: any = $state(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			const response = await fetch(`/api/sessions/${sessionId}`);
			if (!response.ok) {
				throw new Error(`Failed to fetch session: ${response.status}`);
			}
			sessionData = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
		}
	});
</script>

<div class="min-h-screen bg-gray-50 p-8">
	<div class="mx-auto max-w-4xl">
		<h1 class="mb-6 text-3xl font-bold text-gray-900">Session Details</h1>

		{#if loading}
			<div class="flex items-center justify-center p-8">
				<div
					class="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"
				></div>
				<span class="ml-2 text-lg text-gray-600">Loading session...</span>
			</div>
		{:else if error}
			<div class="rounded-lg bg-red-50 p-8">
				<p class="text-red-600">Error: {error}</p>
				<a href="/sessions" class="mt-4 inline-block text-blue-600 hover:underline"
					>← Back to Sessions</a
				>
			</div>
		{:else if sessionData}
			<div class="space-y-6">
				<div class="rounded-lg bg-white p-6 shadow">
					<h2 class="mb-4 text-xl font-semibold text-gray-900">Session Information</h2>
					<div class="grid grid-cols-2 gap-4 text-sm">
						<div>
							<strong>Session ID:</strong> <span class="font-mono text-blue-600">{sessionId}</span>
						</div>
						<div><strong>Created:</strong> {new Date(sessionData.created_at).toLocaleString()}</div>
						<div><strong>Accuracy:</strong> {sessionData.accuracy}%</div>
						<div><strong>Sample Rate:</strong> {sessionData.sample_rate} Hz</div>
						<div class="col-span-2"><strong>User Agent:</strong> {sessionData.user_agent}</div>
					</div>
				</div>

				<div class="rounded-lg bg-white p-6 shadow">
					<h2 class="mb-4 text-xl font-semibold text-gray-900">Recording Summary</h2>
					<p class="text-gray-600">Session successfully saved with all eye tracking data.</p>
				</div>

				<a href="/sessions" class="inline-block text-blue-600 hover:underline">← Back to Sessions</a
				>
			</div>
		{/if}
	</div>
</div>
