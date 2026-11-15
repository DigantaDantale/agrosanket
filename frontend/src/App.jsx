import { useState } from "react";

export default function App() {
  const [form, setForm] = useState({
    n: 90, p: 42, k: 43, temperature: 20.8,
    humidity: 82, ph: 6.5, rainfall: 202,
  });
  const [result, setResult] = useState(null);

  const set = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async () => {
    const body = {
      N: Number(form.n), P: Number(form.p), K: Number(form.k),
      temperature: Number(form.temperature), humidity: Number(form.humidity),
      ph: Number(form.ph), rainfall: Number(form.rainfall),
    };
    try {
      const res = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setResult(await res.json());
    } catch (err) {
      setResult({ error: "Could not reach the backend. Is it running?" });
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: "0 auto", padding: 16, textAlign: "left" }}>
      <h1>AgroSanket</h1>

      {["n", "p", "k", "temperature", "humidity", "ph", "rainfall"].map(f => (
        <div key={f}>
          <label>{f.toUpperCase()}</label>
          <input name={f} type="number" step="any" value={form[f]} onChange={set} />
        </div>
      ))}

      <button onClick={submit} style={{ marginTop: 16, width: "100%" }}>Get recommendation</button>

      {result && <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}