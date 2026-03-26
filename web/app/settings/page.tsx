'use client';
import { useEffect, useState } from 'react';
import { getConfig, setConfig, getModels } from '@/lib/api';

export default function Settings() {
  const [cfg, setCfgState] = useState<any>({});
  const [models, setModels] = useState<any[]>([]);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    getConfig().then(setCfgState);
    getModels().then(setModels);
  }, []);

  const save = async (sec: string, key: string, val: string) => {
    await setConfig(sec, key, val);
    setMsg(`saved ${sec}.${key}`);
    setTimeout(() => setMsg(''), 2000);
    getConfig().then(setCfgState);
  };

  const Field = ({ sec, k, type = 'text' }: any) => {
    const [v, setV] = useState(cfg[sec]?.[k] || '');
    useEffect(() => setV(cfg[sec]?.[k] || ''), [cfg]);
    return (
      <div className="row">
        <label>{sec}.{k}</label>
        <input type={type} value={v} onChange={e => setV(e.target.value)}
               onBlur={() => save(sec, k, v)} />
      </div>
    );
  };

  return (
    <div>
      <h2>settings {msg && <span style={{ color: '#00ff9f', fontSize: '0.8rem' }}>{msg}</span>}</h2>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>defaults</h3>
        <div className="row">
          <label>default.model</label>
          <select value={cfg.default?.model || ''}
                  onChange={e => save('default', 'model', e.target.value)}>
            {models.map(m => <option key={m.name} value={m.name}>{m.name}</option>)}
          </select>
        </div>
        <Field sec="default" k="batch_size" />
        <Field sec="default" k="web_port" />
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>api keys</h3>
        <Field sec="anthropic" k="api_key" type="password" />
        <Field sec="anthropic" k="model_id" />
        <Field sec="openai" k="api_key" type="password" />
        <Field sec="openai" k="model_id" />
        <Field sec="gemini" k="api_key" type="password" />
        <Field sec="gemini" k="model_id" />
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>ollama</h3>
        <Field sec="ollama" k="host" />
        <Field sec="ollama" k="model_id" />
      </div>
    </div>
  );
}
