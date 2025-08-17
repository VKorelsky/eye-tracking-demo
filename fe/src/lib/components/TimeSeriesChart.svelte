<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import uPlot from 'uplot';
	import 'uplot/dist/uPlot.min.css';

	import type { RecordingSessionSample } from '$lib/types';

	interface Props {
		data: RecordingSessionSample[];
	}

	let { data }: Props = $props();

	let containerWidth = $state(0);

	let chartContainer: HTMLDivElement;
	let chart: uPlot | null = null;
	let chartData: uPlot.AlignedData | null = null;
	let originalScales: { x: [number, number]; y: [number, number] } | null = null;

	function resetZoom() {
		if (chart && originalScales) {
			chart.setScale('x', { min: originalScales.x[0], max: originalScales.x[1] });
			chart.setScale('y', { min: originalScales.y[0], max: originalScales.y[1] });
		}
	}

	function updateSize() {
		if (chart && containerWidth > 0) {
			chart.setSize({ width: containerWidth - 40, height: 400 });
		}
	}

	function createChart() {
		if (data.length === 0 || containerWidth === 0) return;

		chart?.destroy();

		const baseMs = new Date(data[0].timestamp).getTime();
		const times = data.map((d) => (new Date(d.timestamp).getTime() - baseMs) / 1000);
		const positions = data.map((d) => d.pos);
		chartData = [times, positions];

		originalScales = {
			x: [Math.min(...times), Math.max(...times)],
			y: [Math.min(...positions), Math.max(...positions)]
		};

		const opts: uPlot.Options = {
			width: containerWidth - 40,
			height: 400,
			cursor: {
				drag: { x: true, y: true }
			},
			series: [
				{ label: 'Time (s)' },
				{
					label: 'Position',
					stroke: '#3b82f6',
					width: 2,
					points: { size: 4, fill: '#3b82f6' }
				}
			],
			axes: [{ label: 'Time (seconds)' }, { label: 'Position' }],
			scales: {
				x: { time: false }
			}
		};

		chart = new uPlot(opts, chartData, chartContainer);
	}

	onMount(() => {
		const resizeObserver = new ResizeObserver((entries) => {
			const newWidth = entries[0].contentRect.width;
			if (newWidth !== containerWidth) {
				containerWidth = newWidth;
				if (chart) {
					updateSize();
				}
			}
		});

		resizeObserver.observe(chartContainer.parentElement!);

		return () => resizeObserver.disconnect();
	});

	onDestroy(() => {
		if (chart) {
			chart.destroy();
		}
	});

	$effect(() => {
		if (data.length > 0 && containerWidth > 0) {
			if (chart) {
				const baseMs = new Date(data[0].timestamp).getTime();
				const times = data.map((d) => (new Date(d.timestamp).getTime() - baseMs) / 1000);
				const positions = data.map((d) => d.pos);
				chartData = [times, positions];
				chart.setData(chartData);
			} else {
				createChart();
			}
		}
	});
</script>

<div class="w-full">
	<div class="mb-4 flex flex-wrap items-center gap-4">
		<button
			onclick={resetZoom}
			class="rounded bg-blue-500 px-3 py-1 text-sm text-white transition-colors hover:bg-blue-600"
		>
			Reset Zoom
		</button>
	</div>
	<div class="w-full overflow-x-auto">
		<div bind:this={chartContainer} class="min-w-0"></div>
	</div>
</div>
