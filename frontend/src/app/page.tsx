"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";
import { isAuthenticated, logout } from "@/lib/auth";

export default function Home() {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setAuthenticated(isAuthenticated());
    setLoading(false);
  }, []);

  const handleLoginSuccess = () => {
    setAuthenticated(true);
  };

  const handleLogout = async () => {
    await logout();
    setAuthenticated(false);
  };

  if (loading) {
    return null;
  }

  if (!authenticated) {
    return <LoginForm onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div>
      <div className="fixed right-6 top-6 z-50">
        <button
          onClick={handleLogout}
          className="rounded-full border border-[var(--stroke)] bg-white px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] shadow-sm transition hover:border-[var(--navy-dark)] hover:text-[var(--navy-dark)]"
        >
          Logout
        </button>
      </div>
      <KanbanBoard />
    </div>
  );
}
