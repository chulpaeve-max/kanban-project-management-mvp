"use client";

import { useState, type FormEvent } from "react";
import { login } from "@/lib/auth";

type LoginFormProps = {
  onLoginSuccess: () => void;
};

export const LoginForm = ({ onLoginSuccess }: LoginFormProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(username, password);
      onLoginSuccess();
    } catch (err) {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <h1 className="font-display text-3xl font-semibold text-[var(--navy-dark)]">
            Kanban Studio
          </h1>
          <p className="mt-3 text-sm text-[var(--gray-text)]">
            Sign in to access your board
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-semibold text-[var(--navy-dark)]"
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                required
                autoFocus
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-semibold text-[var(--navy-dark)]"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                required
              />
            </div>

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-full bg-[var(--secondary-purple)] px-6 py-3 text-sm font-semibold uppercase tracking-wide text-white transition hover:brightness-110 disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-[var(--gray-text)]">
            Demo credentials: user / password
          </p>
        </div>
      </div>
    </div>
  );
};
