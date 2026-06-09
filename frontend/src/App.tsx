// ABOUTME: Root app component - handles auth state and renders nav + routes
// ABOUTME: Shows login screen when unauthenticated; user avatar + logout in nav when logged in

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Route, Routes, NavLink } from "react-router-dom";
import { getMe, logout, type User } from "./api";
import TemplatesPage from "./pages/TemplatesPage";
import TemplatePage from "./pages/TemplatePage";
import SessionsPage from "./pages/SessionsPage";
import SessionPage from "./pages/SessionPage";
import StoresPage from "./pages/StoresPage";
import StorePage from "./pages/StorePage";
import InventoryPage from "./pages/InventoryPage";
import SettingsPage from "./pages/SettingsPage";
import "./App.css";

function UserAvatar({ user }: { user: User }) {
  if (user.picture) {
    return <img src={user.picture} alt={user.name} className="user-avatar" referrerPolicy="no-referrer" />;
  }
  return <span className="user-initial">{user.name.charAt(0).toUpperCase()}</span>;
}

function LoginPage() {
  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-icon">🛒</div>
        <h1>Grocery Manager</h1>
        <p>Sign in to manage your lists, stores, and shopping sessions.</p>
        <a href="/auth/login" className="btn-google">
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </a>
      </div>
    </div>
  );
}

export default function App() {
  const qc = useQueryClient();
  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    retry: false,
  });

  async function handleLogout() {
    await logout();
    qc.clear();
    window.location.href = "/";
  }

  if (isLoading) return <div className="loading">Loading…</div>;
  if (!user) return <LoginPage />;

  return (
    <div className="app">
      <nav className="nav">
        <span className="nav-brand">🛒 Groceries</span>
        <NavLink to="/" end>Sessions</NavLink>
        <NavLink to="/templates">Templates</NavLink>
        <NavLink to="/stores">Stores</NavLink>
        <NavLink to="/inventory">Inventory</NavLink>
        <NavLink to="/settings">Settings</NavLink>
        <button className="nav-user" onClick={handleLogout} title="Sign out">
          <UserAvatar user={user} />
        </button>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<SessionsPage />} />
          <Route path="/sessions/:id" element={<SessionPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/templates/:id" element={<TemplatePage />} />
          <Route path="/stores" element={<StoresPage />} />
          <Route path="/stores/:id" element={<StorePage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}
