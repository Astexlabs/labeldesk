const BASE = process.env.NEXT_PUBLIC_API || '';

export class ApiErr extends Error {
  status: number; hint?: string; field?: string;
  constructor(msg: string, status: number, hint?: string, field?: string) {
    super(msg); this.status = status; this.hint = hint; this.field = field;
  }
}

const hints: Record<number, string> = {
  0: 'is the labeldesk api running? try: labeldesk web',
  404: 'this resource doesnt exist or was deleted',
  500: 'server hit a snag — check terminal logs',
};

async function req(path: string, init?: RequestInit) {
  let r: Response;
  try {
    r = await fetch(`${BASE}${path}`, init);
  } catch (e: any) {
    throw new ApiErr(`cant reach server: ${e.message}`, 0, hints[0]);
  }
  let body: any = null;
  try { body = await r.json(); } catch {}
  if (!r.ok) {
    const d = body?.detail;
    if (d && typeof d === 'object')
      throw new ApiErr(d.msg || `${r.status}`, r.status, d.hint, d.field);
    const msg = d || body?.error || `${r.status} ${r.statusText}`;
    throw new ApiErr(String(msg), r.status, hints[r.status]);
  }
  return body;
}

export const getModels = () => req('/api/models');
export const getProviders = () => req('/api/providers');
export const getJobs = () => req('/api/jobs');
export const getJob = (id: string) => req(`/api/jobs/${id}`);
export const getConfig = () => req('/api/config');

export const setConfig = (section: string, key: string, value: string) =>
  req('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ section, key, value }),
  });

export function uploadFiles(files: FileList) {
  const fd = new FormData();
  Array.from(files).forEach(f => fd.append('files', f));
  return req('/api/upload', { method: 'POST', body: fd });
}

export const createJob = (paths: string[], opts: any = {}) =>
  req('/api/jobs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ paths, ...opts }),
  });

export const delJob = (id: string) =>
  req(`/api/jobs/${id}`, { method: 'DELETE' });
