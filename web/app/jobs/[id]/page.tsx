'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getJob, ApiErr } from '@/lib/api';
import { Alert, Button, Card, ErrInfo } from '@/components/ui';

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState<any>(null);
  const [err, setErr] = useState<ErrInfo | null>(null);

  useEffect(() => {
    const load = async () => {
      try { setJob(await getJob(id as string)); setErr(null); }
      catch (e: any) { setErr({ title: 'cant load job', msg: e.message, hint: (e as ApiErr).hint }); }
    };
    load();
    const t = setInterval(load, 1500);
    return () => clearInterval(t);
  }, [id]);

  if (err) return <Alert err={err} />;
  if (!job) return <div className="mut">loading…</div>;

  const dl = (data: string, ext: string, mime: string) => {
    const url = URL.createObjectURL(new Blob([data], { type: mime }));
    const a = document.createElement('a');
    a.href = url; a.download = `labeldesk-${job.id}.${ext}`; a.click();
    URL.revokeObjectURL(url);
  };
  const dlJson = () => dl(JSON.stringify(job.results, null, 2), 'json', 'application/json');
  const dlCsv = () => {
    const rows = [['file', 'title', 'desc', 'tags', 'src']];
    Object.entries(job.results || {}).forEach(([p, r]: [string, any]) =>
      rows.push([p, r.title || '', r.desc || '', (r.tags || []).join('|'), r.src || '']));
    const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    dl(csv, 'csv', 'text/csv');
  };

  const pct = job.totalFiles ? Math.round(100 * job.doneFiles / job.totalFiles) : 0;
  const res = Object.entries(job.results || {});

  return (
    <div>
      <div className="hd">
        <h2>Job <span className="mono mut">{job.id}</span></h2>
        <p><Link href="/">← all jobs</Link></p>
      </div>

      {job.error && <Alert err={{
        title: 'Job failed',
        raw: job.error,
        hint: job.error.includes('api') || job.error.includes('key')
          ? 'looks like a model config issue — check ur api key in the upload page model picker'
          : 'check the model is reachable and the input images are valid',
      }} />}

      <Card>
        <div className="grid3">
          <div className="stat">
            <div className="k">status</div>
            <div className="v"><span className={`badge ${job.status}`}>{job.status}</span></div>
          </div>
          <div className="stat">
            <div className="k">progress</div>
            <div className="v">{job.doneFiles} / {job.totalFiles} <span className="mut">({pct}%)</span></div>
            <div className={`bar ${job.status}`}><div style={{ width: `${pct}%` }} /></div>
          </div>
          <div className="stat">
            <div className="k">model</div>
            <div className="v">{job.adapter} <span className="mut">· {job.mode}</span></div>
          </div>
        </div>
        {job.status === 'done' && res.length > 0 && (
          <div style={{ marginTop: '1.25rem', display: 'flex', gap: '0.5rem' }}>
            <Button onClick={dlJson}>Download JSON</Button>
            <Button variant="sec" onClick={dlCsv}>Download CSV</Button>
          </div>
        )}
      </Card>

      <Card>
        <h3>Results</h3>
        {!res.length ? (
          <div className="mut">
            {job.status === 'failed' ? 'no results — see error above' : 'still working…'}
          </div>
        ) : (
          <table>
            <thead><tr><th>File</th><th>Title</th><th>Tags</th><th>Src</th></tr></thead>
            <tbody>
              {res.map(([p, r]: [string, any]) => (
                <tr key={p}>
                  <td className="mono">{p.split('/').pop()}</td>
                  <td>{r.title || <span className="mut">—</span>}</td>
                  <td className="mut" style={{ fontSize: '0.78rem' }}>
                    {(r.tags || []).slice(0, 3).join(', ') || '—'}
                  </td>
                  <td><span className="badge">{r.src}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
