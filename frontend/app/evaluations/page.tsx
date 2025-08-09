'use client';
import React, { useEffect, useMemo, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_BASE;

type Dataset = { id: number; name: string; num_items: number };

type Run = { run_id: number; status: string; num_items: number; metrics: string[]; aggregate_results?: Record<string, number> };

export default function EvaluationsPage() {
  const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : new URLSearchParams();
  const preselectedDatasetId = Number(searchParams.get('datasetId') || '');

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [metrics, setMetrics] = useState<Record<string, string>>({});
  const [datasetId, setDatasetId] = useState<number | ''>(preselectedDatasetId || '');
  const [modelProvider, setModelProvider] = useState('litellm');
  const [modelName, setModelName] = useState('gpt-4o-mini');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(["exact_match", "rougeL", "bleu", "answer_relevancy", "correctness", "toxicity"]);
  const [runs, setRuns] = useState<Run[]>([]);

  useEffect(() => {
    (async () => {
      const [dsRes, mRes] = await Promise.all([
        fetch(`${API}/datasets`),
        fetch(`${API}/metrics`),
      ]);
      setDatasets(await dsRes.json());
      setMetrics(await mRes.json());
    })();
  }, []);

  const metricOptions = useMemo(() => Object.entries(metrics), [metrics]);

  const createRun = async () => {
    if (!datasetId) return;
    const res = await fetch(`${API}/evaluations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: `run-${Date.now()}`,
        dataset_id: datasetId,
        model_provider: modelProvider,
        model_name: modelName,
        temperature: 0.0,
        top_p: 1.0,
        max_tokens: 256,
        metrics: selectedMetrics,
      })
    });
    if (res.ok) {
      const r = await res.json();
      window.alert(`Created run ${r.run_id}`);
      await refreshRun(r.run_id);
    }
  };

  const refreshRun = async (runId: number) => {
    const res = await fetch(`${API}/evaluations/${runId}`);
    if (res.ok) {
      const data = await res.json();
      setRuns(prev => {
        const others = prev.filter(p => p.run_id !== runId);
        return [{
          run_id: data.run_id,
          status: data.status,
          num_items: data.num_items,
          metrics: data.metrics,
          aggregate_results: data.aggregate_results
        }, ...others];
      });
    }
  };

  return (
    <div>
      <div className="card">
        <h2>Create Evaluation</h2>
        <label>Dataset</label>
        <select value={datasetId} onChange={e => setDatasetId(Number(e.target.value))}>
          <option value="">Select dataset</option>
          {datasets.map(d => (
            <option key={d.id} value={d.id}>{d.name} ({d.num_items})</option>
          ))}
        </select>
        <label>Model Provider</label>
        <select value={modelProvider} onChange={e => setModelProvider(e.target.value)}>
          <option value="litellm">LiteLLM</option>
          <option value="openai">OpenAI</option>
          <option value="huggingface">HuggingFace</option>
        </select>
        <label>Model Name</label>
        <input value={modelName} onChange={e => setModelName(e.target.value)} />
        <label>Metrics</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {metricOptions.map(([key, label]) => (
            <label key={key} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input type="checkbox" checked={selectedMetrics.includes(key)} onChange={e => {
                if (e.target.checked) setSelectedMetrics(prev => Array.from(new Set([...prev, key])));
                else setSelectedMetrics(prev => prev.filter(m => m !== key));
              }} /> {key}
            </label>
          ))}
        </div>
        <button onClick={createRun} style={{ marginTop: 12 }}>Start</button>
      </div>

      <div className="card">
        <h2>Recent Runs</h2>
        {runs.length === 0 && <div>No runs yet.</div>}
        {runs.map(r => (
          <div key={r.run_id} style={{ borderBottom: '1px solid #eee', padding: '8px 0' }}>
            <div>
              <strong>Run {r.run_id}</strong> — {r.status}
              {r.aggregate_results && (
                <span style={{ marginLeft: 8, color: '#666' }}>
                  {Object.entries(r.aggregate_results).slice(0, 4).map(([k, v]) => `${k}: ${v.toFixed(2)}`).join(' | ')}
                </span>
              )}
            </div>
            <a href={`/evaluations/${r.run_id}`}>View</a>
          </div>
        ))}
      </div>
    </div>
  );
}