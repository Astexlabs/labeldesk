'use client';
import { useEffect, useState } from 'react';
import { getJobs, delJob } from '@/lib/api';

export default function Jobs() {
  const [jobs, setJobs] = useState<any[]>([]);

  const load = async () => setJobs(await getJobs());

  useEffect(() => {
    load();
    const t = setInterval(load, 2000);
    return () => clearInterval(t);
  }, []);

  const rm = async (id: string) => {
    await delJob(id);
    load();
  };

  return (
    <div>
      <h2>jobs</h2>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>id</th><th>status</th><th>progress</th>
              <th>model</th><th>mode</th><th>cost</th><th></th>
            </tr>
          </thead>
          <tbody>
            {jobs.map(j => (
              <tr key={j.id}>
                <td><a href={`/jobs/${j.id}`}>{j.id}</a></td>
                <td><span className={`badge ${j.status}`}>{j.status}</span></td>
                <td>{j.doneFiles}/{j.totalFiles}</td>
                <td>{j.adapter}</td>
                <td>{j.mode}</td>
                <td>${j.costUsd.toFixed(4)}</td>
                <td><button className="ghost" onClick={() => rm(j.id)}>×</button></td>
              </tr>
            ))}
            {!jobs.length && <tr><td colSpan={7}>no jobs yet</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
