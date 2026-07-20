"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface UserInfo {
  name: string;
  email: string;
}

interface ResumeInfo {
  id: number;
  file_name: string;
  uploaded_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [resumes, setResumes] = useState<ResumeInfo[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    async function fetchData() {
      try {
        const [userData, resumeData] = await Promise.all([api.getMe(), api.listResumes()]);
        setUser(userData);
        setResumes(resumeData);
      } catch {
        router.push("/login");
      }
    }

    fetchData();
  }, [router]);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");

    try {
      await api.uploadResume(file);
      const updatedResumes = await api.listResumes();
      setResumes(updatedResumes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  if (!user) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-semibold mb-1 text-black">Welcome, {user.name}</h1>
        <p className="text-gray-600 mb-2">{user.email}</p>
        <a
          href="/interview"
          className="text-sm bg-black text-white px-3 py-1.5 rounded inline-block mb-6"
        >
          Start a Practice Interview
        </a>

        <div className="bg-white rounded-lg shadow p-6 mb-6 text-black">
          <h2 className="font-semibold mb-3">Upload a resume</h2>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            disabled={uploading}
          />
          {uploading && <p className="text-gray-500 text-sm mt-2">Uploading...</p>}
          {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
        </div>

        <div className="bg-white rounded-lg shadow p-6 text-black">
          <h2 className="font-semibold mb-3">Your resumes</h2>
          {resumes.length === 0 ? (
            <p className="text-gray-500 text-sm">No resumes uploaded yet.</p>
          ) : (
            <ul className="space-y-2">
              {resumes.map((resume) => (
                <li key={resume.id} className="flex justify-between items-center border-b pb-2">
                  <span>{resume.file_name}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-gray-400 text-sm">
                      {new Date(resume.uploaded_at).toLocaleDateString()}
                    </span>
                    <a
                      href={`/jobs/matches/${resume.id}`}
                      className="text-sm text-blue-600 underline"
                    >
                      View Matches
                    </a>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}