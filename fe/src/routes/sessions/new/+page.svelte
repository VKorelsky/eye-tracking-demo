<script lang="ts">
	import { onMount } from 'svelte';
	
	let sessionId = '';
	
	onMount(() => {
		sessionId = crypto.randomUUID();
	});
</script>

<div class="min-h-screen bg-gray-50 p-8">
	<div class="max-w-4xl mx-auto">
		<h1 class="text-3xl font-bold text-gray-900 mb-6">New Session</h1>
		<div class="p-8 rounded-lg">
			<p class="text-gray-600 mb-4">Session ID: <span class="font-mono text-blue-600">{sessionId}</span></p>
			<p class="text-gray-500">Recording interface will go here</p>
		</div>
	</div>
</div>