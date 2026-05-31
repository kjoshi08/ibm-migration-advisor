import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IBM Cloud Migration Advisor",
  description: "AI-powered cloud migration planning",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {/* IBM Header */}
        <header style={{
          background: '#161616',
          borderBottom: '1px solid #393939',
          padding: '0 2rem',
          height: '48px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {/* IBM Logo */}
            <svg width="40" height="16" viewBox="0 0 40 16" fill="white">
              <path d="M0 0h6v2H0zM0 4h6v2H0zM0 8h6v2H0zM0 12h6v2H0zM8 0h6v2H8zM9 4h4v2H9zM9 8h4v2H9zM8 12h6v2H8zM16 0h6v2h-6zM16 4h6v2h-6zM16 8h6v2h-6zM16 12h6v2h-6zM24 0h6v2h-6zM24 4h2v8h-2zM28 4h2v8h-2zM24 12h6v2h-6zM32 0h8v2h-8zM33 4h2v2h-2zM33 8h2v2h-2zM32 12h8v2h-8z"/>
            </svg>
            <span style={{
              color: 'white',
              fontSize: '14px',
              fontWeight: 400,
              borderLeft: '1px solid #525252',
              paddingLeft: '1rem',
            }}>
              Cloud Migration Advisor
            </span>
          </div>
          <span style={{
            color: '#8d8d8d',
            fontSize: '12px',
          }}>
            AI Engineer — Hybrid Cloud & AI Division
          </span>
        </header>
        {children}
      </body>
    </html>
  );
}
