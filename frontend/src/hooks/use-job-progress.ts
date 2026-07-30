/**
 * ClipEngine — WebSocket hook for real-time job progress
 */

import { useState, useEffect, useCallback, useRef } from "react";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws";

export interface JobProgress {
  job_id: string;
  video_id: string;
  status: string;
  progress_pct: number;
  current_step: string;
  current_step_detail: string;
  eta_seconds?: number;
}

const STEP_LABELS: Record<string, string> = {
  queued: "Queued",
  researching: "Researching Topic",
  scripting: "Generating Script",
  clipping: "Finding Clips",
  voicing: "Creating Voiceover",
  assembling: "Assembling Video",
  captioning: "Adding Captions",
  thumbnailing: "Generating Thumbnail",
  done: "Complete!",
  failed: "Failed",
  cancelled: "Cancelled",
};

export function useJobProgress(jobId: string | null) {
  const [progress, setProgress] = useState<JobProgress | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!jobId) return;

    const ws = new WebSocket(`${WS_BASE}/jobs/${jobId}`);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "heartbeat") return;

      setProgress(data);

      if (["done", "failed", "cancelled"].includes(data.status)) {
        setIsComplete(true);
        ws.close();
      }
    };

    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setIsConnected(false);

    return () => ws.close();
  }, [jobId]);

  useEffect(() => {
    const cleanup = connect();
    return cleanup;
  }, [connect]);

  const getStepLabel = (step: string) => STEP_LABELS[step] || step;

  return {
    progress,
    isConnected,
    isComplete,
    getStepLabel,
  };
}

export const PIPELINE_STEPS = [
  "researching",
  "scripting",
  "clipping",
  "voicing",
  "assembling",
  "captioning",
  "thumbnailing",
  "done",
];

