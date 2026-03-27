'use client';
import { useEffect, useState } from 'react';
import { getProviders, setConfig } from '@/lib/api';
import { Provider, provColors } from '@/lib/types';
import { Alert, Button, Input, ErrInfo } from '@/components/ui';

const tabs = ['All', 'Connected', 'Not set up'];

export default function Settings() {
  const [provs, setProvs] = useState<Provider[]>([]);
  const [tab, setTab] = useState(0);
  const [q, setQ] = useState('');
  const [edit, setEdit] = useState<Provider | null>(null);
  const [err, setErr] = useState<ErrInfo | null>(null);

  const load = async () => {
    try { setProvs(await getProviders()); setErr(null); }
    catch (e: any) { setErr({ title: 'cant load', msg: e.message, hint: e.hint }); }
  };

  useEffect(() => { load(); }, []);

  const shown = provs
    .filter(p => tab === 0 || (tab === 1) === p.available)
    .filter(p => !q || p.displayName.toLowerCase().includes(q.toLowerCase())
                    || p.name.includes(q.toLowerCase()));

  return (
    <div className="settings">
      <div className="set-hd">
        <div>
          <h1>Providers</h1>
          <p className="sub">Connect an AI backend to power labeling</p>
        </div>
        <input className="set-search" placeholder="Search providers"
               value={q} onChange={e => setQ(e.target.value)} />
      </div>

      {err && <Alert err={err} onRetry={load} />}

      <div className="set-tabs">
        {tabs.map((t, i) => (
          <button key={t} className={i === tab ? 'on' : ''}
                  onClick={() => setTab(i)}>{t}</button>
        ))}
      </div>

      <div className="prov-grid">
        {shown.map(p => (
          <button key={p.name} className="prov-row" onClick={() => setEdit(p)}>
            <div className="ico" style={{ background: provColors[p.name] || '#666' }}>
              {p.displayName[0]}
            </div>
            <div className="bd">
              <div className="nm">
                {p.displayName}
                {p.isDefault && <span className="pill">default</span>}
              </div>
              <div className="ds">{p.desc}</div>
            </div>
            <div className="end">
              {p.available
                ? <span className="stat ok">Connected</span>
                : <span className="stat">Set up</span>}
              <span className="chev">›</span>
            </div>
          </button>
        ))}
        {!shown.length && <div className="empty">No providers match</div>}
      </div>

      {edit && (
        <ProvDialog provider={edit}
                    onClose={() => { setEdit(null); load(); }} />
      )}
    </div>
  );
}

function ProvDialog({ provider, onClose }: { provider: Provider; onClose: () => void }) {
  const [vals, setVals] = useState<Record<string, string>>(
    Object.fromEntries(provider.creds.map(c => [c.key, c.default || '']))
  );
  const [mid, setMid] = useState(provider.modelId);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');

  const save = async (mkDefault = false) => {
    setBusy(true); setMsg('');
    try {
      for (const c of provider.creds) {
        if (vals[c.key]?.trim()) await setConfig(provider.name, c.key, vals[c.key].trim());
      }
      if (mid !== provider.modelId) await setConfig(provider.name, 'model_id', mid);
      if (mkDefault) await setConfig('default', 'model', provider.name);
      onClose();
    } catch (e: any) {
      setMsg(e.message); setBusy(false);
    }
  };

  return (
    <div className="dlg-back" onClick={onClose}>
      <div className="dlg" onClick={e => e.stopPropagation()}>
        <div className="dlg-hd">
          <div className="ico" style={{ background: provColors[provider.name] || '#666' }}>
            {provider.displayName[0]}
          </div>
          <div>
            <div className="dlg-t">{provider.displayName}</div>
            <div className="dlg-s">{provider.desc}</div>
          </div>
        </div>

        <div className="dlg-bd">
          {provider.creds.map(c => (
            <div key={c.key} className="fld">
              <label>{c.label}</label>
              <Input
                type={c.secret ? 'password' : 'text'}
                placeholder={provider.available ? '•••••••• (saved)' : c.default || c.label}
                value={vals[c.key]}
                onChange={e => setVals({ ...vals, [c.key]: e.target.value })}
              />
              {c.hint && <div className="help">{c.hint}</div>}
            </div>
          ))}
          <div className="fld">
            <label>Model</label>
            <select value={mid} onChange={e => setMid(e.target.value)}>
              {provider.models.map(m => <option key={m} value={m}>{m}</option>)}
              {!provider.models.includes(mid) && <option value={mid}>{mid}</option>}
            </select>
          </div>
          {msg && <div className="dlg-err">{msg}</div>}
          <div className="dlg-note">
            Keys go to <code>~/.labeldesk/credentials.toml</code> (owner-only, mode 600).
          </div>
        </div>

        <div className="dlg-ft">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          {!provider.isDefault && (
            <Button variant="sec" disabled={busy} onClick={() => save(true)}>
              Save & make default
            </Button>
          )}
          <Button disabled={busy} onClick={() => save()}>
            {busy ? 'Saving…' : 'Save'}
          </Button>
        </div>
      </div>
    </div>
  );
}
