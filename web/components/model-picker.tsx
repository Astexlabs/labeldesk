'use client';
import { useState } from 'react';
import { setConfig } from '@/lib/api';
import { Button, Input } from './ui';

export type Model = {
  name: string; displayName: string; desc: string; modelId: string;
  defaultModelId: string; available: boolean; reason: string;
  needs: 'api_key' | 'host'; configured: boolean;
};

const colors: Record<string, string> = {
  anthropic: '#d97757', openai: '#10a37f', gemini: '#4285f4', ollama: '#000',
};

export function ModelPicker({ models, val, onChange, onRefresh }: {
  models: Model[]; val: string; onChange: (v: string) => void; onRefresh: () => void;
}) {
  const [editKey, setEditKey] = useState('');
  const [editMid, setEditMid] = useState('');
  const [busy, setBusy] = useState(false);

  const sel = models.find(m => m.name === val);

  const saveKey = async (m: Model) => {
    setBusy(true);
    const k = m.needs === 'host' ? 'host' : 'api_key';
    if (editKey) await setConfig(m.name, k, editKey);
    if (editMid && editMid !== m.modelId) await setConfig(m.name, 'model_id', editMid);
    setEditKey(''); setBusy(false);
    onRefresh();
  };

  return (
    <div className="mpick">
      {models.map(m => {
        const on = m.name === val;
        return (
          <div key={m.name}>
            <button type="button" className={`mitem ${on ? 'on' : ''}`}
                    onClick={() => { onChange(m.name); setEditMid(m.modelId); }}>
              <div className="ico" style={{ background: colors[m.name] || '#666' }}>
                {m.displayName[0]}
              </div>
              <div className="bod">
                <div className="nm">
                  {m.displayName}
                  {m.available
                    ? <span className="badge done">ready</span>
                    : <span className="badge failed">{m.reason || 'not set up'}</span>}
                </div>
                <div className="ds">{m.desc}</div>
                <div className="mid">{m.modelId}</div>
              </div>
              <div className="chev">{on ? '−' : '›'}</div>
            </button>
            {on && (
              <div className="mcfg">
                {!m.available && (
                  <div className="row">
                    <Input type={m.needs === 'host' ? 'text' : 'password'}
                           placeholder={m.needs === 'host' ? 'http://localhost:11434' : `${m.name} api key`}
                           value={editKey} onChange={e => setEditKey(e.target.value)} />
                    <Button size="sm" disabled={busy || !editKey}
                            onClick={() => saveKey(m)}>save</Button>
                  </div>
                )}
                <div className="row">
                  <Input placeholder="model id" value={editMid}
                         onChange={e => setEditMid(e.target.value)} />
                  {editMid !== m.modelId && (
                    <Button size="sm" variant="sec" disabled={busy}
                            onClick={() => saveKey(m)}>update</Button>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
      {sel && !sel.available && (
        <div className="mut" style={{ fontSize: '0.8rem', padding: '0 0.25rem' }}>
          {sel.displayName} isnt configured yet — add ur {sel.needs === 'host' ? 'host' : 'api key'} above to use it
        </div>
      )}
    </div>
  );
}
