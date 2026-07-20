"use client";

import { useEffect, useRef, useState } from "react";
import * as tf from "@tensorflow/tfjs";
import * as cocoSsd from "@tensorflow-models/coco-ssd";

interface ProctoringMonitorProps {
  onFlag: (message: string) => void;
}

export default function ProctoringMonitor({ onFlag }: ProctoringMonitorProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const modelRef = useRef<cocoSsd.ObjectDetection | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [lastFlag, setLastFlag] = useState<string>("");

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;
    let stream: MediaStream;

    async function setup() {
      try {
        await tf.ready();
        modelRef.current = await cocoSsd.load();

        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        setStatus("ready");

        intervalId = setInterval(runDetection, 1500);
      } catch (err) {
        console.error(err);
        setStatus("error");
      }
    }

    async function runDetection() {
      if (!videoRef.current || !modelRef.current) return;

      const predictions = await modelRef.current.detect(videoRef.current);
      const people = predictions.filter((p) => p.class === "person");
      const phones = predictions.filter((p) => p.class === "cell phone");

      if (people.length === 0) {
        flag("No person detected in frame");
      } else if (people.length > 1) {
        flag("Multiple people detected in frame");
      } else if (phones.length > 0) {
        flag("Phone detected in frame");
      }
    }

    function flag(message: string) {
      setLastFlag(message);
      onFlag(message);
    }

    setup();

    return () => {
      if (intervalId) clearInterval(intervalId);
      if (stream) stream.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return (
    <div className="border rounded-lg overflow-hidden bg-black relative">
      <video ref={videoRef} autoPlay muted playsInline className="w-full h-48 object-cover" />
      <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs px-2 py-1">
        {status === "loading" && "Loading proctoring model..."}
        {status === "ready" && !lastFlag && "Monitoring active"}
        {status === "ready" && lastFlag && `⚠ ${lastFlag}`}
        {status === "error" && "Camera access denied or unavailable"}
      </div>
    </div>
  );
}