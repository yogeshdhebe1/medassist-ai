import React, { useEffect, useRef } from "react";
import { AlertCircle } from "lucide-react";

/* ---------------------------------------------------------------
   DESIGN SYSTEM — "Pulse Line"
   Ink/paper base with a vital-teal brand color and a coral accent
   reserved for risk/alerts. The signature motif is an animated
   heartbeat line: it draws itself once in the hero, then returns
   as the actual shape of every AI risk result in the product
   (calm & flat for low risk, one spike for medium, sharp repeated
   spikes for high) instead of a generic radial gauge.
------------------------------------------------------------------*/
export const C = {
  ink: "#1E1B3A",
  paper: "#F7F6FB",
  paperDim: "#EEECF7",
  vital: "#5A4FCF",
  vitalDeep: "#4338A8",
  pulse: "#D6336C",
  amber: "#C98A2E",
  mist: "#E3E0F0",
  mistDeep: "#C4BEDB",
  white: "#FFFFFF",
};

export const FONTS = (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
    .ma-display { font-family: 'Space Grotesk', sans-serif; }
    .ma-body { font-family: 'IBM Plex Sans', sans-serif; }
    .ma-mono { font-family: 'IBM Plex Mono', monospace; }
    @keyframes ma-draw { to { stroke-dashoffset: 0; } }
    @keyframes ma-fade-up { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes ma-blink { 0%, 100% { opacity: .3; } 50% { opacity: 1; } }
    .ma-fade-up { animation: ma-fade-up .5s ease both; }
    .ma-scrollbar::-webkit-scrollbar { width: 6px; }
    .ma-scrollbar::-webkit-scrollbar-thumb { background: ${C.mistDeep}; border-radius: 3px; }
  `}</style>
);

/* ---------- Heartbeat path generator (shared by hero + risk viz) ---------- */
export function heartbeatPath(width, height, beats, intensity) {
  const midY = height / 2;
  const beatWidth = width / beats;
  let d = `M0,${midY}`;
  for (let i = 0; i < beats; i++) {
    const x0 = i * beatWidth;
    const flat1 = x0 + beatWidth * 0.28;
    const pBump = x0 + beatWidth * 0.38;
    const qDip = x0 + beatWidth * 0.46;
    const rPeak = x0 + beatWidth * 0.52;
    const sDip = x0 + beatWidth * 0.58;
    const tBump = x0 + beatWidth * 0.72;
    const flat2 = x0 + beatWidth;
    const amp = height * 0.42 * intensity;
    d += ` L${flat1},${midY}`;
    d += ` L${pBump},${midY - amp * 0.18}`;
    d += ` L${qDip},${midY + amp * 0.12}`;
    d += ` L${rPeak},${midY - amp}`;
    d += ` L${sDip},${midY + amp * 0.55}`;
    d += ` L${tBump},${midY - amp * 0.22}`;
    d += ` L${flat2},${midY}`;
  }
  return d;
}

export function PulseLine({ width = 600, height = 80, beats = 4, intensity = 0.5, color = C.vital, stroke = 2.5, animate = true, className = "" }) {
  const pathRef = useRef(null);
  const d = heartbeatPath(width, height, beats, intensity);
  useEffect(() => {
    if (animate && pathRef.current) {
      const len = pathRef.current.getTotalLength();
      pathRef.current.style.strokeDasharray = `${len}`;
      pathRef.current.style.strokeDashoffset = `${len}`;
      pathRef.current.style.animation = `ma-draw 1.8s ease forwards`;
    }
  }, [animate, d]);
  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} className={className} preserveAspectRatio="none">
      <path ref={pathRef} d={d} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* Risk waveform: maps a 0-1 probability to intensity + color + beat count */
export function riskVisual(probability) {
  if (probability < 0.33) return { intensity: 0.18, color: C.vital, beats: 3, label: "low" };
  if (probability < 0.66) return { intensity: 0.55, color: C.amber, beats: 3, label: "medium" };
  return { intensity: 1, color: C.pulse, beats: 4, label: "high" };
}

export function RiskWave({ probability, size = "md" }) {
  const { intensity, color, beats, label } = riskVisual(probability);
  const h = size === "lg" ? 90 : 56;
  return (
    <div className="w-full">
      <PulseLine width={480} height={h} beats={beats} intensity={intensity} color={color} stroke={size === "lg" ? 3 : 2.5} />
    </div>
  );
}

/* ---------- Small shared UI atoms ---------- */
export function Button({ children, variant = "primary", onClick, className = "", type = "button", disabled }) {
  const base = "ma-body inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold transition-all disabled:opacity-50";
  const styles = {
    primary: { background: `linear-gradient(135deg, ${C.vital}, #7C6FE0)`, color: C.white, boxShadow: "0 10px 25px -8px rgba(90,79,207,0.55)" },
    dark: { backgroundColor: C.ink, color: C.white, boxShadow: "0 10px 25px -10px rgba(30,27,58,0.5)" },
    ghost: { backgroundColor: C.white, color: C.ink, border: `1.5px solid ${C.mist}` },
    ghostDark: { backgroundColor: C.white, color: C.vitalDeep, boxShadow: "0 10px 25px -8px rgba(0,0,0,0.25)" },
    heroGhost: { backgroundColor: "rgba(255,255,255,0.12)", color: C.white, border: `1.5px solid rgba(255,255,255,0.5)` },
    pulse: { background: `linear-gradient(135deg, ${C.pulse}, #F0688E)`, color: C.white, boxShadow: "0 10px 25px -8px rgba(214,51,108,0.5)" },
  };
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={`${base} ${className} hover:-translate-y-0.5 active:scale-[0.98]`} style={styles[variant]}>
      {children}
    </button>
  );
}

export function Card({ children, className = "", onClick, style = {} }) {
  return (
    <div
      onClick={onClick}
      className={`rounded-2xl bg-white ${onClick ? "cursor-pointer hover:-translate-y-0.5" : ""} transition-all ${className}`}
      style={{ boxShadow: "0 15px 35px -15px rgba(30,27,58,0.12)", border: `1px solid ${C.mist}`, ...style }}
    >
      {children}
    </div>
  );
}

export function Badge({ children, tone = "vital" }) {
  const map = {
    vital: { bg: "#EDEAFB", fg: C.vitalDeep },
    amber: { bg: "#F6E9D4", fg: "#8A5E1C" },
    pulse: { bg: "#FBE0EA", fg: "#A8285C" },
  };
  const t = map[tone];
  return (
    <span className="ma-mono text-xs px-2 py-1 rounded-md font-medium" style={{ backgroundColor: t.bg, color: t.fg }}>
      {children}
    </span>
  );
}

export function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div className="ma-body text-sm flex items-start gap-2 p-3 rounded-lg mb-4" style={{ backgroundColor: "#FBE0EA", color: "#A8285C" }}>
      <AlertCircle size={16} className="mt-0.5 shrink-0" /> <span>{message}</span>
    </div>
  );
}

