'use client';
import { useState, useRef, useEffect } from 'react';
import { Provider, provColors } from '@/lib/types';

export function ModelDropdown({ providers, provider, modelId, onPick }: {
  providers: Provider[];
  provider: string;
  modelId: string;
  onPick: (prov: string, mid: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);

  const cur = providers.find(p => p.name === provider);

  return (
    <div className="mdl-dd" ref={ref}>
      <button type="button" className="mdl-pill" onClick={() => setOpen(!open)}>
        <span className="dot" style={{ background: provColors[provider] || '#666' }} />
        <span className="prov">{cur?.displayName || provider}</span>
        <span className="sep">/</span>
        <span className="mid">{modelId}</span>
        <svg viewBox="0 0 12 12" width="10" height="10">
          <path d="M3 5l3 3 3-3" stroke="currentColor" strokeWidth="1.5" fill="none" />
        </svg>
      </button>

      {open && (
        <div className="mdl-menu">
          {providers.map(p => (
            <div key={p.name} className="mdl-grp">
              <div className="mdl-grp-hd">
                <span className="dot" style={{ background: provColors[p.name] || '#666' }} />
                {p.displayName}
                {!p.available && <span className="tag">not connected</span>}
              </div>
              {p.models.map(m => (
                <button
                  key={m}
                  type="button"
                  className={`mdl-opt ${p.name === provider && m === modelId ? 'on' : ''}`}
                  onClick={() => { onPick(p.name, m); setOpen(false); }}
                >
                  {m}
                  {p.name === provider && m === modelId && <span className="chk">✓</span>}
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
