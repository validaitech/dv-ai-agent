import React from 'react';
import './globals.css';

export const metadata = {
  title: 'LLM Checks',
  description: 'Evaluate LLM outputs',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div style={{ maxWidth: 1000, margin: '0 auto', padding: 20 }}>
          <h1>LLM Checks</h1>
          <nav style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
            <a href="/">Datasets</a>
            <a href="/evaluations">Evaluations</a>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}