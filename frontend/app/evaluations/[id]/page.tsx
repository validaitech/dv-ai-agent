'use client';
import React, { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_BASE;

type ItemScore = {
  item_index: number;
  input_text: string;
  reference_text?: string | null;
  output_text?: string | null;
  scores: Record<string, number>;
};

type Results = {
  run_id: number;
  metrics: string[];
  aggregate_results: Record<string, number>;
  samples: ItemScore[];
};

export default function RunDetails({ params }: { params: { id: string } }) {
  const runId = params.id;
  const [status, setStatus] = useState<string>('pending');
  const [results, setResults] = useState<Results | null>(null);

  const refresh = async () => {
    const sRes = await fetch(`${API}/evaluations/${runId}`);
    const s = await sRes.json();
    setStatus(s.status);
    if (s.status === 'completed') {
      const rRes = await fetch(`${API}/evaluations/${runId}/results`);
      if (rRes.ok) setResults(await rRes.json());
    }
  };

  useEffect(() => { refresh(); const id = setInterval(refresh, 3000); return () => clearInterval(id); }, []);

  return (
    <div>
      <div className="card">
        <h2>Run {runId}</h2>
        <div>Status: {status}</div>
        {results && (
          <div style={{ marginTop: 12 }}>
            <h3>Aggregate</h3>
            <div>
              {Object.entries(results.aggregate_results).map(([k, v]) => (
                <div key={k}>{k}: {v.toFixed(3)}</div>
              ))}
            </div>
          </div>
        )}
      </div>

      {results && (
        <div className="card">
          <h3>Samples</h3>
          {results.samples.map(s => (
            <div key={s.item_index} style={{ borderBottom: '1px solid #eee', padding: '8px 0' }}>
              <div><strong>Input:</strong> {s.input_text}</div>
              {s.reference_text && <div><strong>Reference:</strong> {s.reference_text}</div>}
              {s.output_text && <div><strong>Output:</strong> {s.output_text}</div>}
              <div style={{ color: '#555' }}>
                {Object.entries(s.scores).map(([k, v]) => (
                  <span key={k} style={{ marginRight: 8 }}>{k}: {v.toFixed(2)}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}