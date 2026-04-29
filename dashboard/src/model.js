export function simulateSICR(params, t_span, protest_days) {
  const { b1, b2, chi, d11, d21, gamma, C0, n, eps12, eps22, S0, N_obs_start } = params;
  
  // y = [S, I, C, R]
  const y0 = [S0, Math.max(1, N_obs_start * 0.1), Math.max(1, N_obs_start * 0.9), 0];
  
  // Protest days indicator (smoothed)
  function P(t) {
    let val = 0.0;
    for (const pd of protest_days) {
      val += 0.5 * (Math.tanh(10 * (t - (pd - 0.5))) - Math.tanh(10 * (t - (pd + 0.5))));
    }
    return Math.min(1.0, val);
  }

  // RHS
  function rhs(t, y) {
    const [S, I, C, R] = y;
    const Pt = P(t);
    const denominator = 1.0 + Math.pow((I + C) / C0, n);
    const omega = (d21 + eps22 * Pt) / denominator;
    
    const inflow = S * (b1 * I + b2 * C);
    
    const dS = -inflow + gamma * R;
    const dI = inflow - chi * I - (d11 + eps12 * Pt) * I;
    const dC = chi * I - C * omega;
    const dR = (d11 + eps12 * Pt) * I + C * omega - gamma * R;
    
    return [dS, dI, dC, dR];
  }

  // RK4 solver
  const dt = 0.5; // step size
  const steps = Math.ceil((t_span[1] - t_span[0]) / dt);
  
  const history = [];
  let y = [...y0];
  let t = t_span[0];
  
  history.push({ t, S: y[0], I: y[1], C: y[2], R: y[3], N: y[1] + y[2] });
  
  for (let i = 0; i < steps; i++) {
    const k1 = rhs(t, y);
    const k2 = rhs(t + dt/2, y.map((v, idx) => v + k1[idx]*dt/2));
    const k3 = rhs(t + dt/2, y.map((v, idx) => v + k2[idx]*dt/2));
    const k4 = rhs(t + dt, y.map((v, idx) => v + k3[idx]*dt));
    
    y = y.map((v, idx) => Math.max(0, v + (dt/6) * (k1[idx] + 2*k2[idx] + 2*k3[idx] + k4[idx])));
    t += dt;
    
    if (i % 2 === 0) { // store every 1 unit of time
      history.push({ t, S: y[0], I: y[1], C: y[2], R: y[3], N: y[1] + y[2] });
    }
  }
  
  return history;
}
