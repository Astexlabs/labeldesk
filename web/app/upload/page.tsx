'use client';
import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { uploadFiles, createJob, getModels } from '@/lib/api';
import { useEffect } from 'react';

export default function Upload() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [models, setModels] = useState<any[]>([]);
  const [model, setModel] = useState('');
  const [mode, setMode] = useState('title');
  const [ctx, setCtx] = useState('');
  const inpRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    getModels().then(m => {
      setModels(m);
      const avail = m.find((x: any) => x.available);
      if (avail) setModel(avail.name);
    });
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    setFiles(e.dataTransfer.files);
  };

  const go = async () => {
    if (!files?.length) return;
    setBusy(true);
    const up = await uploadFiles(files);
    const job = await createJob(up.paths, { model, mode, ctx });
    router.push(`/jobs/${job.jobId}`);
  };

  return (
    <div>
      <h2>upload</h2>
      <div
        className={`dropzone ${drag ? 'drag' : ''}`}
        onClick={() => inpRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
      >
        <input ref={inpRef} type="file" multiple accept="image/*"
               style={{ display: 'none' }}
               onChange={e => setFiles(e.target.files)} />
        {files?.length ? `${files.length} files selected` : 'drop imgs or click'}
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <div className="row">
          <label>model</label>
          <select value={model} onChange={e => setModel(e.target.value)}>
            {models.map(m => (
              <option key={m.name} value={m.name} disabled={!m.available}>
                {m.name} {m.available ? '' : '(unavail)'}
              </option>
            ))}
          </select>
        </div>
        <div className="row">
          <label>mode</label>
          <select value={mode} onChange={e => setMode(e.target.value)}>
            <option>title</option><option>description</option>
            <option>both</option><option>tags</option>
          </select>
        </div>
        <div className="row">
          <label>context</label>
          <input value={ctx} onChange={e => setCtx(e.target.value)}
                 placeholder="e.g. product shots for kitchen store" />
        </div>
        <button onClick={go} disabled={!files?.length || busy}>
          {busy ? 'uploading...' : 'start labeling'}
        </button>
      </div>
    </div>
  );
}
