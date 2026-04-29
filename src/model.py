import numpy as np

def sicr_rhs(t, y, params, P):
    """
    RHS for the SICR model.
    y: [S, I, C, R]
    params: [b1, b2, chi, d11, d21, gamma, C0, n, eps12, eps22]
    P: function P(t) that returns the police/repression intensity at time t
    """
    S, I, C, R = y
    b1, b2, chi, d11, d21, gamma, C0, n, eps12, eps22 = params
    
    Pt = P(t)
    omega = (d21 + eps22*Pt) / (1.0 + ((I + C) / C0)**n)
    inflow = S * (b1*I + b2*C)
    
    dS = -inflow + gamma*R
    dI =  inflow - chi*I - (d11 + eps12*Pt)*I
    dC =  chi*I - C*omega
    dR =  (d11 + eps12*Pt)*I + C*omega - gamma*R
    
    return [dS, dI, dC, dR]
