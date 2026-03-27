'use client';
import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { uploadFiles, createJob, getProviders, setConfig } from '@/lib/api';
import { Provider } from '@/lib/types';
import { ModelDropdown } from '@/components/model-dropdown';
import { KeyDialog } from '@/components/key-dialog';
import { Alert, ErrInfo } from '@/components/ui';

export default function Upload() {
  const [files, setFiles] = useState<File[]>([]);
  const [ctx, setCtx] = useState('');
  const [provs, setProvs] = useState<Provider[]>([]);
  const [prov, setProv] = useState('');
  const [mid, setMid] = useState('');
  const [askKey, setAskKey] = useState<Provider | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<ErrInfo | null>(null);
  const inpRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const load = async () => {
    try {
      const ps: Provider[] = await getProviders();
      setProvs(ps);
      if (!prov) {
        const d = ps.find(p => p.isDefault) || ps.find(p => p.available) || ps[0];
        if (d) { setProv(d.name); setMid(d.modelId); }
      }
    } catch (e: any) {
      setErr({ title: 'cant reach api', msg: e.message, hint: e.hint });
    }
  };

  useEffect(() => { load(); }, []);

  const pick = (p: string, m: string) => {
    setProv(p); setMid(m);
    const pr = provs.find(x => x.name === p);
    if (pr && !pr.available) setAskKey(pr);
  };

  const addFiles = (fl: FileList | null) => {
    if (!fl) return;
    setFiles(f => [...f, ...Array.from(fl).filter(x => x.type.startsWith('image/'))]);
  };

  const go = async () => {
    if (!files.length) { inpRef.current?.click(); return; }
    const pr = provs.find(p => p.name === prov);
    if (pr && !pr.available) { setAskKey(pr); return; }
    setBusy(true); setErr(null);
    try {
      const dt = new DataTransfer();
      files.forEach(f => dt.items.add(f));
      const up = await uploadFiles(dt.files);
      if (mid) await setConfig(prov, 'model_id', mid);
      const job = await createJob(up.paths, { model: prov, ctx });
      router.push(`/jobs/${job.jobId}`);
    } catch (e: any) {
      setErr({ title: 'couldnt start', msg: e.message, hint: e.hint });
      setBusy(false);
    }
  };

  return (
    <div className="upl"
         onDragOver={e => e.preventDefault()}
         onDrop={e => { e.preventDefault(); addFiles(e.dataTransfer.files); }}>

      <h1 className="upl-h">Label images</h1>

      {err && <Alert err={err} onRetry={() => { setErr(null); load(); }} />}

      <div className="composer">
        <button type="button" className="c-attach" title="Add images"
                onClick={() => inpRef.current?.click()}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="9" cy="9" r="2"/><path d="M21 15l-5-5L5 21"/>
          </svg>
        </button>

        <input
          className="c-inp"
          placeholder={files.length
            ? `${files.length} image${files.length > 1 ? 's' : ''} · add context (optional)`
            : 'Drop images or click the icon, then describe the collection…'}
          value={ctx}
          onChange={e => setCtx(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && go()}
        />

        <ModelDropdown providers={provs} provider={prov} modelId={mid} onPick={pick} />

        <button type="button" className="c-go" disabled={busy}
                onClick={go} title={files.length ? 'Run labeling' : 'Pick images'}>
          {busy ? (
            <svg className="spin" viewBox="0 0 24 24" width="18" height="18">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3"
                      fill="none" strokeDasharray="50" strokeLinecap="round"/>
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M12 4l8 8-8 8V4z"/>
            </svg>
          )}
        </button>

        <input ref={inpRef} type="file" multiple accept="image/*"
               style={{ display: 'none' }}
               onChange={e => addFiles(e.target.files)} />
      </div>

      {files.length > 0 && (
        <div className="thumbs">
          {files.map((f, i) => (
            <div key={i} className="thumb">
              <img src={URL.createObjectURL(f)} alt="" />
              <button onClick={() => setFiles(fs => fs.filter((_, j) => j !== i))}>×</button>
            </div>
          ))}
        </div>
      )}

      {askKey && (
        <KeyDialog
          provider={askKey}
          onCancel={() => setAskKey(null)}
          onDone={() => { setAskKey(null); load(); }}
        />
      )}
    </div>
  );
}
