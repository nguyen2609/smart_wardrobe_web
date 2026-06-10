import { useState } from "react";
import AuthPage from "./pages/AuthPage.jsx";
import WardrobePage from "./pages/WardrobePage.jsx";

export default function App() {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("smartWardrobeUser");
    return raw ? JSON.parse(raw) : null;
  });

  const handleLogin = (data) => {
    localStorage.setItem("smartWardrobeToken", data.access_token);
    localStorage.setItem("smartWardrobeUser", JSON.stringify(data.user));
    setUser(data.user);
  };

  const handleLogout = () => {
    localStorage.removeItem("smartWardrobeToken");
    localStorage.removeItem("smartWardrobeUser");
    setUser(null);
  };

  return user ? (
    <WardrobePage user={user} onLogout={handleLogout} />
  ) : (
    <AuthPage onLogin={handleLogin} />
  );
}
