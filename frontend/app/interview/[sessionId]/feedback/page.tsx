"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { api } from "@/lib/api";

interface FeedbackData {
  communication_score: number;
  technical_score: number;
  structure_score: number;
  summary: string;
  suggestions: string;
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium">{label}</span>
        <span>{score}/10</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-black h-2 rounded-full"
          style={{ width: `${score * 10}%` }}
        />
      </div>
    </div>
  );
}

export default function FeedbackPage() {
  const router = useRouter();
  const params = useParams();
  const sessionId = Number(params.sessionId);

  const [feedback, setFeedback] = useState<FeedbackData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    api
      .generateFeedback(sessionId)
      .then(setFeedback)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to generate feedback"));
  }, [sessionId]);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <a href="/dashboard" className="text-sm text-blue-600 underline mb-4 inline-block">
          ← Back to dashboard
        </a>
        <h1 className="text-2xl font-semibold mb-6 text-blue-700">Interview Feedback</h1>

        {error && <p className="text-red-600">{error}</p>}

        {!feedback && !error && (
          <p className="text-gray-700">Analyzing your interview...</p>
        )}

        {feedback && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow p-6 text-gray-600">
              <h2 className="font-semibold mb-4 text-gray-500">Scores</h2>
              <ScoreBar label="Communication" score={feedback.communication_score} />
              <ScoreBar label="Technical Depth" score={feedback.technical_score} />
              <ScoreBar label="Structure" score={feedback.structure_score} />
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="font-semibold mb-2 text-gray-600">Summary</h2>
              <p className="text-gray-700 text-sm">{feedback.summary}</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="font-semibold mb-2 text-gray-600">Suggestions</h2>
              <p className="text-gray-700 text-sm">{feedback.suggestions}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}