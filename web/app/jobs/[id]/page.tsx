'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getJob } from '@/lib/api';

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState<any>(null);

  useEffect(() => {
    const load = async () => setJob(await getJob(id as string));
    load();
    const t = setInterval(load, 1500);
    return () => clearInterval(t);
  }, [id]);

  if (!job) return <div>loading...</div>;

  const dlJson = () => {
    const blob = new Blob([JSON.stringify(job.results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `labeldesk-${job.id}.json`; a.click();
  };

  const dlCsv = () => {
    const rows = [['file', 'title', 'desc', 'tags', 'src']];
    Object.entries(job.results).forEach(([p, r]: [string, any]) => {
      rows.push([p, r.title, r.desc, (r.tags || []).join('|'), r.src]);
    });
    const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `labeldesk-${job.id}.csv`; a.click();
  };

  return (
    <div>
      <h2>job {job.id}</h2>
      <div className="card">
        <div className="grid">
          <div>status: <span className={`badge ${job.status}`}>{job.status}</span></div>
          <div>progress: {job.doneFiles}/{job.totalFiles}</div>
          <div>model: {job.adapter}</div>
        </div>
        {job.error && <div style={{ color: '#ff3864' }}>error: {job.error}</div>}
        {job.status === 'done' && (
          <div style={{ marginTop: '1rem' }}>
            <button onClick={dlJson}>download json</button>{' '}
            <button onClick={dlCsv} className="ghost">download csv</button>
          </div>
        )}
      </div>

      <div className="card">
        <table>
          <thead><tr><th>file</th><th>title</th><th>src</th></tr></thead>
          <tbody>
            {Object.entries(job.results || {}).map(([p, r]: [string, any]) => (
              <tr key={p}>
                <td>{p.split('/').pop()}</td>
                <td>{r.title}</td>
                <td><span className="badge">{r.src}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
