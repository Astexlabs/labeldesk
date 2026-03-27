'use client';
import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { uploadFiles, createJob, getModels, ApiErr } from '@/lib/api';
import { ModelPicker, Model } from '@/components/model-picker';
import { Button, Input, Alert, Seg, ErrInfo } from '@/components/ui';

const modes = [
  { v: 'title', l: 'Title' },
  { v: 'description', l: 'Description' },
  { v: 'both', l: 'Both' },
  { v: 'tags', l: 'Tags' },
];

export default function Upload() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<ErrInfo | null>(null);
  const [models, setModels] = useState<Model[]>([]);
  const [model, setModel] = useState('');
  const [mode, setMode] = useState('title');
  const [ctx, setCtx] = useState('');
  const inpRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const loadModels = () => getModels()
    .then((m: Model[]) => {
      setModels(m);
      if (!model) {
        const pick = m.find(x => x.available) || m[0];
        if (pick) setModel(pick.name);
      }
    })
    .catch((e: ApiErr) => setErr({ title: 'cant load models', msg: e.message, hint: e.hint }));

  useEffect(() => { loadModels(); }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault(); setDrag(false); setFiles(e.dataTransfer.files);
  };

  const go = async () => {
    if (!files?.length) return;
    setBusy(true); setErr(null);
    try {
      const up = await uploadFiles(files);
      const job = await createJob(up.paths, { model, mode, ctx });
      router.push(`/jobs/${job.jobId}`);
    } catch (e: any) {
      setErr({ title: 'couldnt start job', msg: e.message, hint: e.hint, raw: e.hint ? undefined : e.message });
      setBusy(false);
    }
  };

  const sel = models.find(m => m.name === model);
  const ready = files?.length && sel?.available;

  return (
    <div>
      <div className="hd">
        <h2>New labeling</h2>
        <p>Drop images, pick a model, go. Model config saves as you type.</p>
      </div>

      {err && <Alert err={err} onRetry={() => { setErr(null); loadModels(); }} />}

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
        {files?.length ? (
          <><div className="big">{files.length} image{files.length > 1 ? 's' : ''} selected</div>
            <div className="sm">click to change</div></>
        ) : (
          <><div className="big">Drop images here</div>
            <div className="sm">or click to browse · jpg png webp gif</div></>
        )}
      </div>

      <div className="fld" style={{ marginTop: '1.75rem' }}>
        <label>Model</label>
        <ModelPicker models={models} val={model} onChange={setModel} onRefresh={loadModels} />
      </div>

      <div className="fld">
        <label>What to generate</label>
        <Seg opts={modes} val={mode} onChange={setMode} />
      </div>

      <div className="fld">
        <label>Context <span className="mut">(optional)</span></label>
        <Input value={ctx} onChange={e => setCtx(e.target.value)}
               placeholder="e.g. product shots for a kitchen store" />
        <div className="help">a short hint about the collection — makes labels more accurate</div>
      </div>

      <Button onClick={go} disabled={!ready || busy}>
        {busy ? 'Uploading…'
          : !files?.length ? 'Pick images first'
          : !sel?.available ? `Set up ${sel?.displayName || 'model'} first`
          : `Label ${files.length} image${files.length > 1 ? 's' : ''}`}
      </Button>
    </div>
  );
}
