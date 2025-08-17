// Shared front-end types

import type { GazeData } from 'webgazer';

export type RecordingSessionState = 'ready' | 'calibration' | 'recording' | 'paused' | 'completed';

export type CalibrationPoint = {
	x: number; // percentage of canvas width
	y: number; // percentage of canvas height
	clicks: number;
	completed: boolean;
};

export type RecordingSample = GazeData & {
	elapsedMs: number;
};

export type RecordingSessionSample = {
	timestamp: string;
	pos: number;
};

export type RecordingSessionData = {
	sample_rate: number;
	recorded_at: string;
	duration: number;
	samples: RecordingSessionSample[];
};
