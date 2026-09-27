import { FormEvent, useState } from "react";
import { login } from "../services/api";

export function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState("operator");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setLoading(true);
    try { await login(username, password); onLogin(); } catch (err) { setError(err instanceof Error ? err.message : "Login failed"); } finally { setLoading(false); }
  }

  return <main className="login-shell"><section className="login-art"><div className="brand-mark">OK<span>•</span>DRIVER</div><div><p className="eyebrow">MOBILITY INTELLIGENCE / 01</p><h1>See the road<br /><em>before it moves.</em></h1><p className="login-intro">A live operations console for safer streets, faster response, and every vehicle that matters.</p></div><div className="login-foot">SYSTEM STATUS <span>●</span> ALL SERVICES READY</div></section><section className="login-panel"><div className="login-form-wrap"><p className="eyebrow">OPERATOR ACCESS</p><h2>Welcome back.</h2><p className="muted">Sign in to your monitoring workspace.</p><form onSubmit={submit}><label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label><label>Password<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" /></label>{error && <p className="form-error">{error}</p>}<button className="primary-button" disabled={loading}>{loading ? "AUTHENTICATING..." : "ENTER OPERATIONS"}<span>↗</span></button></form><p className="login-note">Access is secured with JWT authentication and role-based permissions.</p></div></section></main>;
}
