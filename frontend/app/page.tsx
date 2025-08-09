'use client';
import React, { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_BASE;

type Dataset = { id: number; name: string; description?: string | null; num_items: number };

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState<string>('dataset');
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const res = await fetch(`${API}/datasets`);
    const data = await res.json();
    setDatasets(data);
  };

  useEffect(() => { load(); }, []);

  const upload = async () => {
    if (!file) return;
    setBusy(true);
    const form = new FormData();
    form.append('file', file);
    form.append('name', name);
    const res = await fetch(`${API}/datasets`, { method: 'POST', body: form });
    if (res.ok) {
      setFile(null);
      setName('dataset');
      await load();
    }
    setBusy(false);
  };

  return (
    <div>
      <div className="card">
        <h2>Upload Dataset</h2>
        <label>Name</label>
        <input value={name} onChange={e => setName(e.target.value)} />
        <label>File (.jsonl or .csv)</label>
        <input type="file" accept=".jsonl,.json,.csv" onChange={e => setFile(e.target.files?.[0] || null)} />
        <button onClick={upload} disabled={busy || !file} style={{ marginTop: 8 }}>Upload</button>
      </div>
      <div className="card">
        <h2>Datasets</h2>
        {datasets.length === 0 && <div>No datasets.</div>}
        {datasets.map(d => (
          <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #eee' }}>
            <div>
              <strong>{d.name}</strong>
              <div style={{ color: '#666' }}>{d.num_items} items</div>
            </div>
            <a href={`/evaluations?datasetId=${d.id}`}>Evaluate</a>
          </div>
        ))}
      </div>
    </div>
  );
}