"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import ProctoringMonitor from "@/components/ProctoringMonitor";

type InterviewStatus = "not_started" | "in_progress" | "completed";

export default function InterviewPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const jobId = searchParams.get("jobId");

  const [status, setStatus] = useState<InterviewStatus>("not_started");
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastFlagType, setLastFlagType] = useState<string>("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
    }
  }, []);

  async function handleStart() {
    setLoading(true);
    setError("");
    try {
      const result = await api.startInterview(jobId ? Number(jobId) : undefined);
      setSessionId(result.session_id);
      setQuestion(result.question);
      setStatus("in_progress");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start interview");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitAnswer() {
    if (!sessionId || !answer.trim()) return;

    setLoading(true);
    setError("");
    try {
      const result = await api.submitAnswer(sessionId, answer);
      setAnswer("");

      if (result.status === "completed") {
        setStatus("completed");
      } else {
        setQuestion(result.question);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit answer");
    } finally {
      setLoading(false);
    }
  }

  function handleProctoringFlag(message: string) {
    let flagType = "unknown";
    if (message.includes("No person")) flagType = "no_person";
    else if (message.includes("Multiple people")) flagType = "multiple_people";
    else if (message.includes("Phone")) flagType = "phone_detected";

    if (flagType === lastFlagType) return;

    setLastFlagType(flagType);

    if (sessionId) {
      api.logFlag(sessionId, flagType, message).catch(() => {});
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <a href="/dashboard" className="text-sm text-blue-600 underline mb-4 inline-block">
          ← Back to dashboard
        </a>
        <h1 className="text-2xl font-semibold mb-6">Mock Interview</h1>

        {error && <p className="text-red-600 mb-4">{error}</p>}

        {status === "not_started" && (
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-700 mb-4">
              {jobId
                ? "This interview will be tailored to the job you selected."
                : "This will be a general practice interview."}
            </p>
            <button
              onClick={handleStart}
              disabled={loading}
              className="bg-black text-white px-4 py-2 rounded disabled:opacity-50"
            >
              {loading ? "Starting..." : "Start Interview"}
            </button>
          </div>
        )}

        {status === "in_progress" && (
          <div className="space-y-4">
            <ProctoringMonitor onFlag={handleProctoringFlag} />

            <div className="bg-white rounded-lg shadow p-6">
              <p className="font-medium mb-4">{question}</p>
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                rows={5}
                placeholder="Type your answer here..."
                className="w-full border rounded px-3 py-2 mb-4"
              />
              <button
                onClick={handleSubmitAnswer}
                disabled={loading || !answer.trim()}
                className="bg-black text-white px-4 py-2 rounded disabled:opacity-50"
              >
                {loading ? "Submitting..." : "Submit Answer"}
              </button>
            </div>
          </div>
        )}

        {status === "completed" && (
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-700 mb-4">
              Interview complete! You can now view your feedback.
            </p>
            <a
              href={`/interview/${sessionId}/feedback`}
              className="bg-black text-white px-4 py-2 rounded inline-block"
            >
              View Feedback
            </a>
          </div>
        )}
      </div>
    </div>
  );
}