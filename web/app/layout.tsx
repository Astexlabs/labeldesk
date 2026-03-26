import './globals.css';

export const metadata = { title: 'labeldesk', description: 'smart img labeler' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <h1>labeldesk</h1>
          <div className="links">
            <a href="/">jobs</a>
            <a href="/upload">upload</a>
            <a href="/settings">settings</a>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
