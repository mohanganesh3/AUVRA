// Simple fetch-based backend health checker (no axios)
// Returns { ok: boolean, latencyMs: number|null, data?: object, error?: string }

export async function checkBackendHealth(baseUrl) {
  const url = `${baseUrl.replace(/\/$/, '')}/health`;
  const start = Date.now();
  try {
    const res = await fetch(url, { method: 'GET' });
    const latency = Date.now() - start;
    if (!res.ok) {
      return { ok: false, latencyMs: latency, error: `HTTP ${res.status}` };
    }
    const data = await res.json();
    return { ok: true, latencyMs: latency, data };
  } catch (e) {
    return { ok: false, latencyMs: null, error: e.message };
  }
}
