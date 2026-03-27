import { ReactNode, ButtonHTMLAttributes, InputHTMLAttributes } from 'react';

type BtnProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'default' | 'sec' | 'ghost';
  size?: 'default' | 'sm';
};

export function Button({ variant = 'default', size = 'default', className = '', ...p }: BtnProps) {
  const cls = ['btn', variant !== 'default' && variant, size !== 'default' && size, className]
    .filter(Boolean).join(' ');
  return <button className={cls} {...p} />;
}

export function Input(p: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...p} className={`inp ${p.className || ''}`} />;
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`card ${className}`}>{children}</div>;
}

export type ErrInfo = { title: string; msg?: string; hint?: string; raw?: string };

export function Alert({ err, onRetry }: { err: ErrInfo; onRetry?: () => void }) {
  return (
    <div className="alert err" role="alert">
      <div className="t">⚠ {err.title}</div>
      {err.msg && <div className="d">{err.msg}</div>}
      {err.raw && <pre>{err.raw}</pre>}
      {err.hint && <div className="hint">💡 {err.hint}</div>}
      {onRetry && <div style={{ marginTop: '0.75rem' }}>
        <Button size="sm" variant="sec" onClick={onRetry}>try again</Button>
      </div>}
    </div>
  );
}

export function Seg({ opts, val, onChange }: {
  opts: { v: string; l: string }[]; val: string; onChange: (v: string) => void;
}) {
  return (
    <div className="seg">
      {opts.map(o => (
        <button key={o.v} type="button" className={val === o.v ? 'on' : ''}
                onClick={() => onChange(o.v)}>{o.l}</button>
      ))}
    </div>
  );
}
