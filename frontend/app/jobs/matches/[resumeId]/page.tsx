"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { api } from "@/lib/api";

interface JobMatch {
  id: number;
  title: string;
  company: string;
  description: string;
  location: string | null;
  match_explanation: string;
}

export default function JobMatchesPage() {
  const router = useRouter();
  const params = useParams();
  const resumeId = Number(params.resumeId);

  const [matches, setMatches] = useState<JobMatch[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    api
      .getJobMatches(resumeId)
      .then(setMatches)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load matches"));
  }, [resumeId]);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <a href="/dashboard" className="text-sm text-blue-600 underline mb-4 inline-block">
          ← Back to dashboard
        </a>
        <h1 className="text-2xl font-semibold mb-6 text-gray-700">Job Matches</h1>

        {error && <p className="text-red-600">{error}</p>}

        {!matches && !error && <p className="text-gray-500">Finding your best matches...</p>}

        {matches && matches.length === 0 && (
          <p className="text-gray-500">No matches found.</p>
        )}

        <div className="space-y-4">
          {matches?.map((job) => (
            <div key={job.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h2 className="font-semibold text-lg text-green-500">{job.title}</h2>
                  <p className="text-gray-600 text-sm">
                    {job.company} {job.location && `· ${job.location}`}
                  </p>
                </div>
              </div>
              <p className="text-gray-700 text-sm mb-3">{job.description}</p>
              <div className="bg-blue-50 border border-blue-100 rounded p-3 mb-3">
                <p className="text-sm text-blue-900">
                  <span className="font-medium">Why this matches: </span>
                  {job.match_explanation}
                </p>
              </div>
              <a
                href={`/interview?jobId=${job.id}`}
                className="text-sm bg-black text-white px-3 py-1.5 rounded inline-block"
              >
                Practice Interview for this role
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}