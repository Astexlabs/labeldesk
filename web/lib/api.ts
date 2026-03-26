const BASE = process.env.NEXT_PUBLIC_API || '';

export async function getModels() {
  const r = await fetch(`${BASE}/api/models`);
  return r.json();
}

export async function getJobs() {
  const r = await fetch(`${BASE}/api/jobs`);
  return r.json();
}

export async function getJob(id: string) {
  const r = await fetch(`${BASE}/api/jobs/${id}`);
  return r.json();
}

export async function getConfig() {
  const r = await fetch(`${BASE}/api/config`);
  return r.json();
}

export async function setConfig(section: string, key: string, value: string) {
  const r = await fetch(`${BASE}/api/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ section, key, value }),
  });
  return r.json();
}

export async function uploadFiles(files: FileList) {
  const fd = new FormData();
  Array.from(files).forEach(f => fd.append('files', f));
  const r = await fetch(`${BASE}/api/upload`, { method: 'POST', body: fd });
  return r.json();
}

export async function createJob(paths: string[], opts: any = {}) {
  const r = await fetch(`${BASE}/api/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ paths, ...opts }),
  });
  return r.json();
}

export async function delJob(id: string) {
  await fetch(`${BASE}/api/jobs/${id}`, { method: 'DELETE' });
}
