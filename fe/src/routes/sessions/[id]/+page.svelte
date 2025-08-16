<script lang="ts">
	import { page } from '$app/stores';

	$: sessionId = $page.params.id;
</script>

<div class="min-h-screen bg-gray-50 p-8">
	<div class="mx-auto max-w-4xl">
		<h1 class="mb-6 text-3xl font-bold text-gray-900">Session Playback</h1>
		<div class="rounded-lg p-8">
			<p class="mb-4 text-gray-600">
				Session ID: <span class="font-mono text-blue-600">{sessionId}</span>
			</p>
			<p class="text-gray-500">Playback interface will go here</p>
		</div>
	</div>
</div>
