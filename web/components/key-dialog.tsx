'use client';
import { useState } from 'react';
import { setConfig } from '@/lib/api';
import { Provider, provColors } from '@/lib/types';
import { Button, Input } from './ui';

export function KeyDialog({ provider, onDone, onCancel }: {
  provider: Provider; onDone: () => void; onCancel: () => void;
}) {
  const need = provider.creds.filter(c => provider.missing.includes(c.key));
  const [vals, setVals] = useState<Record<string, string>>(
    Object.fromEntries(need.map(c => [c.key, c.default || '']))
  );
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const canSave = need.every(c => vals[c.key]?.trim());

  const save = async () => {
    setBusy(true); setErr('');
    try {
      for (const c of need) {
        await setConfig(provider.name, c.key, vals[c.key].trim());
      }
      onDone();
    } catch (e: any) {
      setErr(e.message || 'save failed');
      setBusy(false);
    }
  };

  return (
    <div className="dlg-back" onClick={onCancel}>
      <div className="dlg" onClick={e => e.stopPropagation()}>
        <div className="dlg-hd">
          <div className="ico" style={{ background: provColors[provider.name] || '#666' }}>
            {provider.displayName[0]}
          </div>
          <div>
            <div className="dlg-t">Connect {provider.displayName}</div>
            <div className="dlg-s">{provider.desc}</div>
          </div>
        </div>

        <div className="dlg-bd">
          {need.map(c => (
            <div key={c.key} className="fld">
              <label>{c.label}</label>
              <Input
                type={c.secret ? 'password' : 'text'}
                autoFocus={c === need[0]}
                placeholder={c.default || c.label}
                value={vals[c.key]}
                onChange={e => setVals({ ...vals, [c.key]: e.target.value })}
                onKeyDown={e => e.key === 'Enter' && canSave && save()}
              />
              {c.hint && <div className="help">{c.hint}</div>}
            </div>
          ))}
          {err && <div className="dlg-err">{err}</div>}
          <div className="dlg-note">
            Saved to <code>~/.labeldesk/credentials.toml</code> with owner-only permissions.
          </div>
        </div>

        <div className="dlg-ft">
          <Button variant="ghost" onClick={onCancel}>Cancel</Button>
          <Button disabled={!canSave || busy} onClick={save}>
            {busy ? 'Saving…' : 'Save & use'}
          </Button>
        </div>
      </div>
    </div>
  );
}
