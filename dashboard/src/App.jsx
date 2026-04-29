import React, { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { simulateSICR } from './model';
import './index.css';

const presets = {
  france: {
    b1: 1e-05,
    b2: 1e-09,
    chi: 0.01,
    d11: 0.151,
    d21: 0.217,
    gamma: 0.010,
    C0: 679180,
    n: 4.0,
    eps12: 0.145,
    eps22: 0.428,
    S0: 4000000,
    N_obs_start: 100000,
    duration: 140,
    protest_days: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130] // approx
  },
  iran: {
    b1: 4.0e-06,
    b2: 5.59e-06,
    chi: 0.163,
    d11: 0.393,
    d21: 0.258,
    gamma: 0.010,
    C0: 479260,
    n: 4.0,
    eps12: 0.955,
    eps22: 0.468,
    S0: 6000000,
    N_obs_start: 5000,
    duration: 160,
    protest_days: Array.from({length: 160}, (_, i) => i) // everyday
  }
};

export default function App() {
  const [activePreset, setActivePreset] = useState('france');
  const [params, setParams] = useState(presets.france);

  const handlePreset = (presetName) => {
    setActivePreset(presetName);
    setParams(presets[presetName]);
  };

  const handleParamChange = (e) => {
    const { name, value } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: parseFloat(value)
    }));
  };

  const data = useMemo(() => {
    return simulateSICR(params, [0, params.duration], params.protest_days);
  }, [params]);

  return (
    <div className="app-container">
      <header className="header glass">
        <div className="title-section">
          <h1>SICR Protest Dynamics Model</h1>
          <p>Interactive simulation of demobilization under state repression</p>
        </div>
        <div className="presets-container">
          <button 
            className={`preset-btn ${activePreset === 'france' ? 'active' : ''}`}
            onClick={() => handlePreset('france')}
          >
            France 2023 (Pension Reform)
          </button>
          <button 
            className={`preset-btn ${activePreset === 'iran' ? 'active' : ''}`}
            onClick={() => handlePreset('iran')}
          >
            Iran 2022 (Mahsa Amini)
          </button>
        </div>
      </header>

      <main className="main-content">
        <section className="chart-section glass">
          <h2>Active Protesters over Time</h2>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                <XAxis dataKey="t" stroke="#888" tick={{fill: '#888'}} label={{ value: 'Days', position: 'insideBottom', offset: -10, fill: '#888' }} />
                <YAxis stroke="#888" tick={{fill: '#888'}} label={{ value: 'Protesters (N)', angle: -90, position: 'insideLeft', fill: '#888' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid #334155', borderRadius: '8px', color: '#f1f5f9' }}
                  itemStyle={{ color: '#38bdf8' }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Line type="monotone" dataKey="N" stroke="#38bdf8" strokeWidth={3} dot={false} activeDot={{ r: 8 }} name="Active Protesters (I + C)" />
                <Line type="monotone" dataKey="I" stroke="#a78bfa" strokeWidth={2} dot={false} name="Informed (I)" />
                <Line type="monotone" dataKey="C" stroke="#f472b6" strokeWidth={2} dot={false} name="Committed (C)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="controls-section glass">
          <h2>Model Parameters</h2>
          <div className="sliders-grid">
            
            <div className="slider-group">
              <label>
                <span>Repression Intensity (ε₁₂)</span>
                <span className="value">{params.eps12.toFixed(3)}</span>
              </label>
              <input type="range" name="eps12" min="0" max="2" step="0.01" value={params.eps12} onChange={handleParamChange} />
              <p className="help-text">Effect of police on protesters retiring</p>
            </div>

            <div className="slider-group">
              <label>
                <span>Repression Arrest (ε₂₂)</span>
                <span className="value">{params.eps22.toFixed(3)}</span>
              </label>
              <input type="range" name="eps22" min="0" max="1" step="0.01" value={params.eps22} onChange={handleParamChange} />
              <p className="help-text">Effect of police on committed protesters</p>
            </div>

            <div className="slider-group">
              <label>
                <span>Mobilization Rate (β₁)</span>
                <span className="value">{params.b1.toExponential(2)}</span>
              </label>
              <input type="range" name="b1" min="1e-7" max="1e-4" step="1e-7" value={params.b1} onChange={handleParamChange} />
              <p className="help-text">Rate at which susceptibles join</p>
            </div>

            <div className="slider-group">
              <label>
                <span>Natural Exit Rate (d₁₁)</span>
                <span className="value">{params.d11.toFixed(3)}</span>
              </label>
              <input type="range" name="d11" min="0" max="1" step="0.01" value={params.d11} onChange={handleParamChange} />
              <p className="help-text">Baseline fatigue/exit rate</p>
            </div>

            <div className="slider-group">
              <label>
                <span>Commitment Rate (χ)</span>
                <span className="value">{params.chi.toFixed(3)}</span>
              </label>
              <input type="range" name="chi" min="0" max="1" step="0.01" value={params.chi} onChange={handleParamChange} />
              <p className="help-text">Transition from Informed to Committed</p>
            </div>

            <div className="slider-group">
              <label>
                <span>Density Threshold (C₀)</span>
                <span className="value">{Math.round(params.C0)}</span>
              </label>
              <input type="range" name="C0" min="10000" max="2000000" step="10000" value={params.C0} onChange={handleParamChange} />
              <p className="help-text">Crowd size giving safety in numbers</p>
            </div>

          </div>
        </section>
      </main>
    </div>
  );
}
