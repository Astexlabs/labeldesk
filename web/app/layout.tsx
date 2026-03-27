'use client';
import './globals.css';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const ico = {
  upload: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>,
  jobs: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h6M9 13h6M9 17h4"/></svg>,
};

const nav = [
  { href: '/upload', lbl: 'New labeling', ico: ico.upload },
  { href: '/', lbl: 'Jobs', ico: ico.jobs },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const isOn = (h: string) =>
    h === '/' ? (path === '/' || path.startsWith('/jobs')) : path.startsWith(h);

  return (
    <html lang="en">
      <head><title>LabelDesk</title></head>
      <body>
        <div className="shell">
          <aside className="side">
            <Link href="/upload" className="brand">
              <span className="logo">LabelDesk</span>
            </Link>
            {nav.map(n => (
              <Link key={n.href} href={n.href} className={`nl ${isOn(n.href) ? 'on' : ''}`}>
                {n.ico}{n.lbl}
              </Link>
            ))}
          </aside>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
