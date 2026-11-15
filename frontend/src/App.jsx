import { useState } from "react";

export default function App() {
  const [form, setForm] = useState({
    n: 90, p: 42, k: 43, temperature: 20.8,
    humidity: 82, ph: 6.5, rainfall: 202,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const set = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async () => {
    setLoading(true);
    setResult(null);
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
      setResult({ success: false, error: "Could not reach the backend. Is it running?" });
    }
    setLoading(false);
  };

  const labels = {
    n: "Nitrogen (N)", p: "Phosphorus (P)", k: "Potassium (K)",
    temperature: "Temperature (°C)", humidity: "Humidity (%)",
    ph: "Soil pH", rainfall: "Rainfall (mm)",
  };

  return (
    <div style={{ maxWidth: 480, margin: "0 auto", padding: 16, textAlign: "left" }}>
      <h1>AgroSanket</h1>

      {Object.keys(labels).map((f) => (
        <div key={f} style={{ marginBottom: 8 }}>
          <label style={{ display: "block" }}>{labels[f]}</label>
          <input
            name={f} type="number" step="any"
            value={form[f]} onChange={set}
            style={{ width: "100%", padding: 6 }}
          />
        </div>
      ))}

      <button onClick={submit} disabled={loading} style={{ marginTop: 12, width: "100%", padding: 10 }}>
        {loading ? "Checking..." : "Get recommendation"}
      </button>

      {result && result.success === false && (
        <p style={{ color: "red", marginTop: 16 }}>{result.error || "Something went wrong."}</p>
      )}

      {result && result.success && (
        <div style={{ marginTop: 16 }}>
          <h2>Recommended: {result.recommended_crop}</h2>
          {result.top_recommendations.map((c, i) => (
            <div key={c.crop} style={{ border: "1px solid #ccc", borderRadius: 8, padding: 12, marginTop: 10 }}>
              <strong>{i + 1}. {c.crop}</strong>
              <div style={{ background: "#eee", borderRadius: 4, height: 10, marginTop: 6 }}>
                <div style={{ width: `${c.probability}%`, background: "#2e7d32", height: 10, borderRadius: 4 }} />
              </div>
              <small>{c.probability}% match</small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}