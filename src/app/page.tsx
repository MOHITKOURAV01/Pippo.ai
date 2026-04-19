"use client";

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Metadata {
  parties?: string;
  effective_date?: string;
  governing_law?: string;
  jurisdiction?: string;
  termination_notice?: string;
  [key: string]: any;
}

interface AnalysisItem {
  clause: string;
  is_risky: boolean;
  confidence: number;
}

interface Summary {
  total_clauses: number;
  risky_clauses: number;
  safe_ratio: number;
}

interface AnalysisResult {
  filename: string;
  metadata: Metadata;
  analysis: AnalysisItem[];
  summary: Summary;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      handleUpload(e.target.files[0]);
    }
  };

  const handleUpload = async (uploadedFile: File) => {
    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="main-container">
      {/* ─────────────────────────────────────────────────────────────
          MAIN LAYOUT (SAME AS ORIGINAL app.py)
      ───────────────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '48px' }}>
        
        {/* LEFT COLUMN */}
        <div>
          <div style={{ marginTop: '8vh' }}></div>
          <div className="fade-in">
            <div className="h-title">
                <span style={{ color: '#58A6FF', textShadow: '0 0 40px rgba(88,166,255,0.2)' }}>Bharat&apos;s Precision.</span><br />
                <span style={{ color: '#E6EDF3' }}>Global Ambition.</span><br />
                <span style={{ color: '#E91E63', textShadow: '0 0 30px rgba(233,30,99,0.2)' }}>Intelligent</span>
                <span style={{ color: '#E91E63', fontWeight: 800 }}> World.</span>
            </div>
          </div>
          <p className="hero-subtitle fade-in">
            Architecture matters. While regular trackers skim the surface, Pippo AI is engineered
            for the deep nuances of Bharat&apos;s legal landscape. 🇮🇳
          </p>

          <span className="label-mono">Uplink Terminal</span>
          <div 
            className="upload-zone"
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              accept=".pdf" 
              style={{ display: 'none' }} 
            />
            {loading ? (
              <div style={{ padding: '20px' }}>
                <div className="label-mono" style={{ marginBottom: '10px' }}>Analyzing...</div>
                <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                  <motion.div 
                    initial={{ x: '-100%' }}
                    animate={{ x: '100%' }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                    style={{ width: '40%', height: '100%', background: 'var(--brand-blue)' }}
                  />
                </div>
              </div>
            ) : file ? (
                <div className="risk-tag risk-low" style={{ margin: '0 auto' }}>✓ UPLINK SUCCESSFUL</div>
            ) : (
                <p style={{ opacity: 0.5 }}>Upload a contract PDF for analysis</p>
            )}
          </div>
          {error && <p style={{ color: 'var(--brand-red)', marginTop: '10px' }}>{error}</p>}
        </div>

        {/* RIGHT COLUMN (IMAGE) */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <img 
            src="/whisk.png" 
            alt="Pippo Brand" 
            style={{ maxWidth:'100%', width:'min(750px, 100%)', height:'auto', filter:'drop-shadow(0 0 40px rgba(88,166,255,0.08))', marginTop: '12vh' }}
          />
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────────
          ANALYSIS RESULTS (SAME AS ORIGINAL app.py)
      ───────────────────────────────────────────────────────────── */}
      {results && (
        <div className="fade-in" style={{ marginTop: '40px' }}>
            <span className="label-mono">Contract DNA</span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
                {Object.entries(results.metadata).map(([key, value]) => (
                    <div key={key} className="bento-card">
                        <span className="label-mono" style={{ fontSize: '0.5rem' }}>{key.replace(/_/g, ' ')}</span>
                        <p style={{ fontSize: '0.85rem', fontWeight: 600, color: '#58A6FF' }}>{value as string}</p>
                    </div>
                ))}
            </div>

            <span className="label-mono">Risk Analytics</span>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
                <div className="glass-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px' }}>
                    {/* Placeholder for Donut Chart which was plotly in original */}
                    <div style={{ textAlign: 'center' }}>
                        <div className="stat-value">{results.summary.risky_clauses}</div>
                        <div className="stat-label">Risky Clauses</div>
                    </div>
                </div>
                <div className="glass-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <div className="stat-value">{results.summary.safe_ratio}%</div>
                    <p className="stat-label">SAFE RATIO</p>
                </div>
            </div>

            <span className="label-mono">Clause Audit</span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {results.analysis.map((item, i) => {
                    const riskClass = item.is_risky ? "risk-high" : "risk-low";
                    return (
                        <div key={i} className="glass-container">
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span className={`risk-tag ${riskClass}`}>C-{i+1}</span>
                                <span className="label-mono">{Math.round(item.confidence * 100)}% CONF</span>
                            </div>
                            <div style={{ marginTop:'10px', color:'#C9D1D9' }}>{item.clause}</div>
                        </div>
                    );
                })}
            </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          FOOTER & NAVBAR (SAME AS ORIGINAL app.py)
      ───────────────────────────────────────────────────────────── */}
      <div className="pippo-footer">
          <span className="label-mono">PIPPO AI</span>
          <span className="label-mono" style={{ opacity: 0.2 }}>SYSTEM NOMINAL // V2.1.0</span>
      </div>

      <div className="pippo-navbar">
          <div className="nav-brand">
              <div className="pippo-logo">Pippo</div>
              <span className="badge">AI LEGAL</span>
          </div>
          <div className="nav-right">
              <div className="nav-status">
                  <span className="status-dot"></span>
                  <span>SECURE ACCESS</span>
              </div>
          </div>
      </div>
    </main>
  );
}
