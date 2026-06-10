import { useState } from "react";
import { Shirt } from "lucide-react";
import { api } from "../api";

export default function AuthPage({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const payload = mode === "login"
        ? { email: form.email, password: form.password }
        : form;
      const response = await api.post(endpoint, payload);
      onLogin(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="brand">
          <div className="brand-icon"><Shirt size={30} /></div>
          <div>
            <h1>Smart Wardrobe</h1>
            <p>AI closet for your outfit collection</p>
          </div>
        </div>

        <div className="tabs">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
        </div>

        <form onSubmit={submit} className="auth-form">
          {mode === "register" && (
            <label>
              Name
              <input name="name" value={form.name} onChange={update} required />
            </label>
          )}
          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={update} required />
          </label>
          <label>
            Password
            <input name="password" type="password" value={form.password} onChange={update} required minLength={6} />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="primary-btn" disabled={loading}>{loading ? "Loading..." : mode === "login" ? "Login" : "Create account"}</button>
        </form>
      </section>
    </main>
  );
}
