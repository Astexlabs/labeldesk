'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getJobs, delJob, ApiErr } from '@/lib/api';
import { Alert, Button, Card, ErrInfo } from '@/components/ui';

export default function Jobs() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [err, setErr] = useState<ErrInfo | null>(null);
  const [ready, setReady] = useState(false);

  const load = async () => {
    try { setJobs(await getJobs()); setErr(null); }
    catch (e: any) { setErr({ title: 'cant load jobs', msg: e.message, hint: (e as ApiErr).hint }); }
    setReady(true);
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 2000);
    return () => clearInterval(t);
  }, []);

  const rm = async (id: string) => {
    try { await delJob(id); load(); }
    catch (e: any) { setErr({ title: 'delete failed', msg: e.message, hint: e.hint }); }
  };

  const pct = (j: any) => j.totalFiles ? Math.round(100 * j.doneFiles / j.totalFiles) : 0;

  return (
    <div>
      <div className="hd">
        <h2>Jobs</h2>
        <p>All labeling runs. Click a row to see full results and errors.</p>
      </div>

      {err && <Alert err={err} onRetry={load} />}

      <Card>
        {!ready ? <div className="mut">loading…</div> : !jobs.length ? (
          <div className="empty">
            <div className="big">No jobs yet</div>
            <div>Start your first run from <Link href="/upload">New labeling</Link></div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Job</th><th>Status</th><th style={{ width: '22%' }}>Progress</th>
                <th>Model</th><th>Mode</th><th>Cost</th><th></th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(j => (
                <tr key={j.id}>
                  <td><Link href={`/jobs/${j.id}`} className="mono">{j.id.slice(0, 10)}</Link></td>
                  <td><span className={`badge ${j.status}`}>{j.status}</span></td>
                  <td>
                    <div className="mut" style={{ fontSize: '0.78rem' }}>{j.doneFiles}/{j.totalFiles}</div>
                    <div className={`bar ${j.status}`}><div style={{ width: `${pct(j)}%` }} /></div>
                  </td>
                  <td>{j.adapter}</td>
                  <td className="mut">{j.mode}</td>
                  <td className="mono">${(j.costUsd || 0).toFixed(4)}</td>
                  <td><Button variant="ghost" size="sm" onClick={() => rm(j.id)} title="delete">×</Button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
