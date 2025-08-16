// WebGazer.js TypeScript Declaration File

declare module 'webgazer' {
	// Core Data Types
	export interface GazeData {
		x: number;
		y: number;
	}

	export interface Eye {
		patch: ImageData;
		imagex: number;
		imagey: number;
		width: number;
		height: number;
	}

	export interface Eyes {
		left: Eye;
		right: Eye;
	}

	// Callback Types
	export type GazeListener = (data: GazeData | null, elapsedTimeMs: number) => void;
	export type OnFailCallback = (error?: any) => void;

	// Tracker and Regression Types
	export type TrackerType = 'TFFacemesh';
	export type RegressionType = 'ridge' | 'weightedRidge' | 'threadedRidge';
	export type EventType = 'click' | 'move';
	export type TrackEyeType = 'left' | 'right' | 'both';

	// Camera Constraints
	export interface CameraConstraints {
		video: {
			width: { min: number; ideal: number; max: number };
			height: { min: number; ideal: number; max: number };
			facingMode: string;
		};
	}

	// Parameters Configuration
	export interface WebGazerParams {
		moveTickSize: number;
		videoContainerId: string;
		videoElementId: string;
		videoElementCanvasId: string;
		faceOverlayId: string;
		faceFeedbackBoxId: string;
		gazeDotId: string;
		videoViewerWidth: number;
		videoViewerHeight: number;
		faceFeedbackBoxRatio: number;
		showVideo: boolean;
		mirrorVideo: boolean;
		showFaceOverlay: boolean;
		showFaceFeedbackBox: boolean;
		showGazeDot: boolean;
		camConstraints: CameraConstraints;
		dataTimestep: number;
		showVideoPreview: boolean;
		applyKalmanFilter: boolean;
		saveDataAcrossSessions: boolean;
		storingPoints: boolean;
		trackEye: TrackEyeType;
		getEventTypes(): EventType[];
	}

	// DataWindow Class
	export interface DataWindow<T = any> {
		new (windowSize: number, data?: T[]): DataWindow<T>;
		push(entry: T): void;
		get(ind: number): T;
		getTrueIndex(ind: number): number;
		addAll(data: T[]): void;
	}

	// DebugBox Class
	export interface DebugBox {
		new (interval?: number): DebugBox;
		set(key: string, value: any): void;
		inc(key: string, incBy?: number, init?: number): void;
		addButton(name: string, func: () => void): void;
		show(name: string, func: () => void): void;
	}

	// Utility Functions
	export interface WebGazerUtil {
		Eye: {
			new (patch: ImageData, imagex: number, imagey: number, width: number, height: number): Eye;
		};
		DataWindow: DataWindow;
		DebugBox: DebugBox;

		// Image Processing
		getEyeFeats(eyes: Eyes): number[];
		grayscale(pixels: Uint8ClampedArray, width: number, height: number): Uint8ClampedArray;
		equalizeHistogram(src: number[], step?: number, dst?: number[]): number[];
		threshold(data: number[], threshold: number): number[];
		resizeEye(eye: Eye, resizeWidth: number, resizeHeight: number): ImageData;

		// Data Processing
		correlation(data1: number[], data2: number[]): number;
		bound(prediction: GazeData): GazeData;
	}

	// Main WebGazer Interface
	export interface WebGazer {
		// Core Control Methods
		begin(onFail?: OnFailCallback): WebGazer;
		isReady(): boolean;
		pause(): WebGazer;
		resume(): Promise<WebGazer>;
		end(): WebGazer;
		stopVideo(): WebGazer;

		// Prediction & Data Methods
		getCurrentPrediction(regIndex?: number): GazeData | null;
		setGazeListener(listener: GazeListener): WebGazer;
		clearGazeListener(): WebGazer;
		recordScreenPosition(x: number, y: number, eventType: EventType): void;
		storePoints(x: number, y: number, k: number): void;
		getStoredPoints(): any[];
		clearData(): Promise<WebGazer>;

		// Configuration Methods
		setTracker(name: TrackerType): WebGazer;
		setRegression(name: RegressionType): WebGazer;
		addTrackerModule(name: string, constructor: any): WebGazer;
		addRegressionModule(name: string, constructor: any): WebGazer;
		addRegression(name: string): WebGazer;

		// Display & UI Methods
		showVideoPreview(val: boolean): WebGazer;
		showVideo(val: boolean): WebGazer;
		showFaceOverlay(val: boolean): WebGazer;
		showFaceFeedbackBox(val: boolean): WebGazer;
		showPredictionPoints(val: boolean): WebGazer;

		// Settings Methods
		saveDataAcrossSessions(val: boolean): WebGazer;
		applyKalmanFilter(val: boolean): WebGazer;
		setCameraConstraints(constraints: CameraConstraints): Promise<WebGazer>;
		setStaticVideo(videoLoc: string): WebGazer;
		setVideoViewerSize(w: number, h: number): WebGazer;
		setVideoElementCanvas(canvas: HTMLCanvasElement): WebGazer;

		// Event Handling Methods
		addMouseEventListeners(): WebGazer;
		removeMouseEventListeners(): WebGazer;

		// Utility Methods
		detectCompatibility(): { supportsUserMedia: boolean; supportsCanvas: boolean };
		computeValidationBoxSize(): { top: number; left: number; width: number; height: number };
		getTracker(): any;
		getRegression(): any;
		getVideoElementCanvas(): HTMLCanvasElement | null;
		getVideoPreviewToCameraResolutionRatio(): { x: number; y: number };

		// Properties
		params: WebGazerParams;
		util: WebGazerUtil;
		tracker: {
			TFFaceMesh: any;
		};
		reg: {
			RidgeReg: any;
			RidgeWeightedReg: any;
			RidgeRegThreaded: any;
		};
	}

	const webgazer: WebGazer;
	export default webgazer;
}
