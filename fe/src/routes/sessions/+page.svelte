<script lang="ts">
	import { onMount } from 'svelte';

	type Session = {
		id: string;
		user_agent: string;
		sample_rate: number;
		created_at: string;
	};

	let sessions: Session[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			const response = await fetch(`/api/sessions`);
			if (!response.ok) {
				throw new Error(`Failed to fetch sessions: ${response.status}`);
			}
			sessions = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
		}
	});

	const formatDate = (iso: string) => new Date(iso).toLocaleString();
	const truncate = (s: string, n = 80) => (s.length > n ? s.slice(0, n - 1) + '…' : s);
</script>

<div class="min-h-screen bg-gray-50 p-8">
	<div class="mx-auto max-w-4xl">
		<div class="mb-6 flex items-center justify-between">
			<h1 class="text-3xl font-bold text-gray-900">Sessions</h1>
			<a
				class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
				href="/sessions/new"
				>New Recording</a
			>
		</div>

		{#if loading}
			<div class="flex items-center justify-center rounded-lg bg-white p-8 shadow">
				<div class="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"></div>
				<span class="ml-2 text-lg text-gray-600">Loading sessions...</span>
			</div>
		{:else if error}
			<div class="rounded-lg bg-red-50 p-6">
				<p class="text-red-600">Error: {error}</p>
			</div>
		{:else if sessions.length === 0}
			<div class="rounded-lg bg-white p-8 text-center shadow">
				<p class="mb-4 text-gray-600">No sessions yet.</p>
				<a class="text-blue-600 hover:underline" href="/sessions/new">Create your first recording →</a>
			</div>
		{:else}
			<div class="space-y-3">
				{#each sessions as s}
					<a
						class="block rounded-lg bg-white p-5 shadow hover:shadow-md transition"
						href={`/sessions/${s.id}`}
					>
						<div class="flex items-start justify-between">
							<div>
								<div class="flex items-center gap-3">
									<span class="font-semibold text-gray-900">Session</span>
									<span class="font-mono text-sm text-blue-600">{s.id}</span>
								</div>
								<div class="mt-1 text-sm text-gray-600">
									<span>Created: {formatDate(s.created_at)}</span>
								</div>
							</div>
							<div class="grid grid-cols-2 gap-x-6 gap-y-1 text-sm text-gray-700">
								<div><strong>Sample Rate:</strong> {s.sample_rate} Hz</div>
								<div class="col-span-2">
									<strong>User Agent:</strong> {truncate(s.user_agent)}
								</div>
							</div>
						</div>
					</a>
				{/each}
			</div>
		{/if}
	</div>
</div>