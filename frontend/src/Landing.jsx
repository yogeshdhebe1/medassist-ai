import React, { useEffect, useRef, useState } from "react";
import { motion, useScroll, useTransform, useInView, useMotionValueEvent, AnimatePresence, useReducedMotion } from "framer-motion";
import {
  Activity, Stethoscope, MessageCircle, Calendar, ArrowRight, Heart, Brain, Droplet, Wind,
  FileText, ShieldCheck, Gauge, Plus, Minus, ScanLine, Salad,
} from "lucide-react";
import { C, PulseLine, Button, riskVisual } from "./ui";

/* ------------------------------ helpers ------------------------------ */
const ease = [0.22, 1, 0.36, 1];

function Reveal({ children, delay = 0, y = 28, className = "" }) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.7, delay, ease }}
    >
      {children}
    </motion.div>
  );
}

function CountUp({ to, suffix = "", decimals = 0, duration = 1.6 }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    let raf;
    const start = performance.now();
    const tick = (t) => {
      const p = Math.min((t - start) / (duration * 1000), 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(to * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, to, duration]);
  return <span ref={ref}>{val.toFixed(decimals)}{suffix}</span>;
}

function SplitHeadline({ text, className = "" }) {
  const reduce = useReducedMotion();
  const words = text.split(" ");
  return (
    <h1 className={className} aria-label={text}>
      {words.map((w, i) => (
        <span key={i} className="inline-block overflow-hidden align-bottom mr-[0.25em]" aria-hidden="true">
          <motion.span
            className="inline-block"
            initial={reduce ? false : { y: "110%" }}
            animate={{ y: 0 }}
            transition={{ duration: 0.8, delay: 0.15 + i * 0.07, ease }}
          >
            {w}
          </motion.span>
        </span>
      ))}
    </h1>
  );
}

/* ------------------------------ NAV ------------------------------ */
function Nav({ goTo }) {
  const { scrollY } = useScroll();
  const [solid, setSolid] = useState(false);
  useMotionValueEvent(scrollY, "change", (v) => setSolid(v > 40));
  const links = [["Features", "features"], ["How it works", "how"], ["FAQ", "faq"]];
  const jump = (id) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  return (
    <motion.nav
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.7, ease }}
      className="fixed top-0 inset-x-0 z-50 transition-all duration-300"
      style={{
        backgroundColor: solid ? "rgba(30,27,58,0.93)" : "transparent",
        backdropFilter: solid ? "blur(14px)" : "none",
        boxShadow: solid ? "0 8px 30px rgba(0,0,0,0.18)" : "none",
      }}
    >
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2 ma-display font-bold text-lg text-white">
          <Activity size={22} strokeWidth={2.5} /> MedAssist AI
        </div>
        <div className="hidden md:flex items-center gap-8">
          {links.map(([label, id]) => (
            <button key={id} onClick={() => jump(id)} className="ma-body text-sm text-white/80 hover:text-white transition-colors">{label}</button>
          ))}
        </div>
        <Button variant="ghostDark" className="!py-2.5 !px-5" onClick={() => goTo("auth")}>Sign in</Button>
      </div>
    </motion.nav>
  );
}

/* ------------------------------ HERO DEMO CARD ------------------------------ */
const DEMO = [
  { label: "Diabetes", p: 0.12, note: "Glucose and BMI in range" },
  { label: "Heart disease", p: 0.52, note: "Resting BP slightly elevated" },
  { label: "Stroke", p: 0.81, note: "Age and glucose are major factors" },
];

function LiveRiskCard() {
  const [i, setI] = useState(0);
  const reduce = useReducedMotion();
  useEffect(() => {
    if (reduce) return;
    const t = setInterval(() => setI((x) => (x + 1) % DEMO.length), 3600);
    return () => clearInterval(t);
  }, [reduce]);
  const d = DEMO[i];
  const rv = riskVisual(d.p);
  return (
    <div className="relative">
      {/* arch backdrop */}
      <motion.div
        className="absolute -inset-4 rounded-t-[200px] rounded-b-[36px]"
        style={{ background: "linear-gradient(160deg, rgba(255,255,255,0.28), rgba(255,255,255,0.04))", border: "1px solid rgba(255,255,255,0.25)" }}
        animate={reduce ? {} : { y: [0, -8, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.92, y: 30 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 0.5, ease }}
        className="relative rounded-t-[180px] rounded-b-3xl bg-white px-7 pt-20 pb-7"
        style={{ boxShadow: "0 40px 80px -30px rgba(20,16,70,0.6)" }}
      >
        <div className="flex items-center justify-center gap-4 mb-1">
          <span className="ma-mono text-[11px]" style={{ color: "#9491AC" }}>Sample result</span>
          <span className="flex items-center gap-1.5 ma-mono text-[11px]" style={{ color: C.vitalDeep }}>
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: rv.color, animation: "ma-blink 1.4s infinite" }} /> live demo
          </span>
        </div>
        <AnimatePresence mode="wait">
          <motion.div key={d.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.4 }}>
            <div className="ma-display text-xl font-bold mt-2" style={{ color: C.ink }}>{d.label}</div>
            <div className="flex items-end gap-2 mt-1">
              <div className="ma-display text-5xl font-bold" style={{ color: rv.color }}>{Math.round(d.p * 100)}%</div>
              <div className="ma-mono text-xs pb-2 uppercase" style={{ color: rv.color }}>{rv.label} risk</div>
            </div>
            <div className="mt-2 -mx-1"><PulseLine key={d.label} width={420} height={70} beats={rv.beats} intensity={rv.intensity} color={rv.color} stroke={3} /></div>
            <div className="ma-body text-sm mt-1" style={{ color: "#6E6B8A" }}>{d.note}</div>
          </motion.div>
        </AnimatePresence>
        <div className="flex gap-1.5 mt-5">
          {DEMO.map((_, k) => (
            <div key={k} className="h-1 flex-1 rounded-full overflow-hidden" style={{ backgroundColor: C.paperDim }}>
              {k === i && !reduce && <motion.div key={i} className="h-full" style={{ backgroundColor: C.vital }} initial={{ width: 0 }} animate={{ width: "100%" }} transition={{ duration: 3.6, ease: "linear" }} />}
              {k === i && reduce && <div className="h-full w-full" style={{ backgroundColor: C.vital }} />}
            </div>
          ))}
        </div>
      </motion.div>

      {/* floating chips */}
      {[
        { t: "Symptom checker", icon: Stethoscope, cls: "-left-12 top-8", d: 0 },
        { t: "Report OCR", icon: ScanLine, cls: "-right-10 top-[58%]", d: 1.2 },
        { t: "AI chat", icon: MessageCircle, cls: "-left-8 -bottom-5", d: 2.1 },
      ].map(({ t, icon: Icon, cls, d: delay }) => (
        <motion.div
          key={t}
          className={`absolute ${cls} hidden md:flex items-center gap-2 px-3.5 py-2 rounded-full bg-white ma-body text-xs font-semibold`}
          style={{ color: C.ink, boxShadow: "0 14px 30px -10px rgba(20,16,70,0.45)" }}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={reduce ? { opacity: 1, scale: 1 } : { opacity: 1, scale: 1, y: [0, -9, 0] }}
          transition={{ opacity: { delay: 1 + delay * 0.2 }, scale: { delay: 1 + delay * 0.2 }, y: { duration: 5, repeat: Infinity, delay, ease: "easeInOut" } }}
        >
          <Icon size={14} color={C.vital} /> {t}
        </motion.div>
      ))}
    </div>
  );
}

/* ------------------------------ HERO ------------------------------ */
function Hero({ goTo }) {
  const ref = useRef(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const blobY = useTransform(scrollYProgress, [0, 1], [0, 140]);
  return (
    <section ref={ref} className="relative overflow-hidden rounded-b-[48px] pb-40"
      style={{ background: "linear-gradient(180deg, #1C1745 0%, #3B2FD6 38%, #7B6BFF 72%, #B9B2F7 100%)" }}>
      {/* animated aurora blobs */}
      <motion.div style={{ y: blobY }} className="absolute inset-0 pointer-events-none">
        <motion.div className="absolute -top-24 -left-24 w-[460px] h-[460px] rounded-full blur-3xl" style={{ background: "#8A7AFF", opacity: 0.45 }}
          animate={reduce ? {} : { x: [0, 60, 0], y: [0, 40, 0] }} transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }} />
        <motion.div className="absolute top-40 right-0 w-[380px] h-[380px] rounded-full blur-3xl" style={{ background: "#D6336C", opacity: 0.22 }}
          animate={reduce ? {} : { x: [0, -50, 0], y: [0, 50, 0] }} transition={{ duration: 17, repeat: Infinity, ease: "easeInOut" }} />
        <div className="absolute inset-0 opacity-[0.07]" style={{ backgroundImage: "radial-gradient(#fff 1px, transparent 1px)", backgroundSize: "28px 28px" }} />
      </motion.div>

      <div className="relative max-w-6xl mx-auto px-6 pt-36 grid md:grid-cols-2 gap-16 items-center">
        <div>
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05, duration: 0.6 }}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full ma-body text-xs font-medium text-white mb-6"
            style={{ backgroundColor: "rgba(255,255,255,0.14)", border: "1px solid rgba(255,255,255,0.3)" }}>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-300" /> 5 trained ML models · FastAPI backend
          </motion.div>
          <SplitHeadline text="Know your health risk before it becomes a problem." className="ma-display font-bold text-white text-4xl md:text-6xl leading-[1.05]" />
          <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9, duration: 0.7 }}
            className="ma-body text-white/80 text-lg mt-6 max-w-md">
            Check symptoms, screen for diabetes, heart, stroke and kidney disease, read your lab reports and book a doctor, all in one place.
          </motion.p>
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.1, duration: 0.7 }} className="flex flex-wrap gap-3 mt-8">
            <Button variant="ghostDark" onClick={() => goTo("auth")}>Start free check <ArrowRight size={16} /></Button>
            <Button variant="heroGhost" onClick={() => document.getElementById("features")?.scrollIntoView({ behavior: "smooth" })}>See what it does</Button>
          </motion.div>
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }} className="ma-body text-xs text-white/60 mt-5">
            General information only, not a medical diagnosis.
          </motion.p>
        </div>
        <LiveRiskCard />
      </div>
    </section>
  );
}

/* ------------------------------ QUICK CHECK BAR ------------------------------ */
function QuickBar({ goTo }) {
  const opts = [["Diabetes", Droplet], ["Heart", Heart], ["Stroke", Brain], ["Kidney", Wind]];
  const [sel, setSel] = useState(0);
  return (
    <div className="relative max-w-5xl mx-auto px-6 -mt-24 z-10">
      <Reveal>
        <div className="rounded-3xl bg-white p-5 md:p-6 flex flex-col md:flex-row md:items-center gap-5" style={{ boxShadow: "0 30px 60px -25px rgba(30,27,58,0.35)", border: `1px solid ${C.mist}` }}>
          <div className="md:w-48 shrink-0">
            <div className="ma-display font-bold" style={{ color: C.ink }}>Start a risk check</div>
            <div className="ma-body text-xs mt-1" style={{ color: "#9491AC" }}>Pick a condition, sign in, run the model.</div>
          </div>
          <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-2">
            {opts.map(([name, Icon], k) => (
              <button key={name} onClick={() => setSel(k)} className="relative ma-body text-sm font-medium rounded-xl py-3 flex items-center justify-center gap-2" style={{ color: sel === k ? C.white : C.ink }}>
                {sel === k && <motion.span layoutId="quickpill" className="absolute inset-0 rounded-xl" style={{ background: `linear-gradient(135deg, ${C.vital}, #7C6FE0)` }} transition={{ type: "spring", stiffness: 380, damping: 30 }} />}
                {sel !== k && <span className="absolute inset-0 rounded-xl" style={{ backgroundColor: C.paperDim }} />}
                <span className="relative flex items-center gap-2"><Icon size={16} /> {name}</span>
              </button>
            ))}
          </div>
          <Button onClick={() => goTo("auth")} className="shrink-0">Check {opts[sel][0].toLowerCase()} <ArrowRight size={16} /></Button>
        </div>
      </Reveal>
    </div>
  );
}

/* ------------------------------ MARQUEE ------------------------------ */
function Marquee() {
  const items = ["Random Forest", "XGBoost", "Tesseract OCR", "FastAPI", "PostgreSQL", "JWT + RBAC", "React", "scikit-learn"];
  const row = [...items, ...items];
  return (
    <div className="mt-20 overflow-hidden" aria-hidden="true" style={{ maskImage: "linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent)", WebkitMaskImage: "linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent)" }}>
      <motion.div className="flex gap-12 w-max" animate={{ x: ["0%", "-50%"] }} transition={{ duration: 30, repeat: Infinity, ease: "linear" }}>
        {row.map((t, i) => (
          <span key={i} className="ma-display text-xl font-bold whitespace-nowrap flex items-center gap-12" style={{ color: C.mistDeep }}>
            {t} <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: C.mistDeep }} />
          </span>
        ))}
      </motion.div>
    </div>
  );
}

/* ------------------------------ FEATURES (bento) ------------------------------ */
const FEATURES = [
  { icon: Heart, title: "Disease risk screening", body: "Diabetes, heart disease, stroke and kidney disease, each with its own trained model and the factors behind the result.", span: "md:col-span-2", tint: true },
  { icon: Stethoscope, title: "Symptom checker", body: "Pick your symptoms and get ranked possible conditions.", span: "" },
  { icon: Gauge, title: "One health score", body: "All your results combined into a single 0–100 score.", span: "" },
  { icon: FileText, title: "Report reader", body: "Upload a lab report image. We read the values and flag the ones outside normal range.", span: "" },
  { icon: Salad, title: "Diet and exercise tips", body: "Safe, rule-based suggestions that follow your latest results.", span: "" },
  { icon: ShieldCheck, title: "Private by design", body: "Login with JWT, role-based access, and doctors only see patients assigned to them.", span: "md:col-span-3" },
];

function Features() {
  return (
    <section id="features" className="max-w-6xl mx-auto px-6 pt-28">
      <Reveal>
        <h2 className="ma-display font-bold text-3xl md:text-5xl max-w-2xl leading-[1.15]" style={{ color: C.ink }}>Everything you need to understand your numbers</h2>
        <p className="ma-body mt-4 max-w-xl" style={{ color: "#6E6B8A" }}>Six tools, one account. Each one connects to the same patient profile.</p>
      </Reveal>
      <div className="grid md:grid-cols-3 gap-5 mt-12">
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 36 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.6, delay: (i % 3) * 0.1, ease }}
            whileHover={{ y: -6 }}
            className={`group relative overflow-hidden rounded-3xl p-7 ${f.span}`}
            style={f.tint
              ? { background: "linear-gradient(135deg, #2A2170, #5A4FCF)", color: C.white }
              : { backgroundColor: C.white, border: `1px solid ${C.mist}`, color: C.ink, boxShadow: "0 18px 40px -26px rgba(30,27,58,0.25)" }}
          >
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center transition-transform duration-300 group-hover:rotate-6 group-hover:scale-110"
              style={{ backgroundColor: f.tint ? "rgba(255,255,255,0.16)" : "#EDEAFB" }}>
              <f.icon size={22} color={f.tint ? "#fff" : C.vital} />
            </div>
            <h3 className="ma-display font-bold text-xl mt-5">{f.title}</h3>
            <p className="ma-body text-sm mt-2 leading-relaxed" style={{ color: f.tint ? "rgba(255,255,255,0.78)" : "#6E6B8A" }}>{f.body}</p>
            {f.tint && <div className="absolute bottom-0 inset-x-0 opacity-40"><PulseLine width={600} height={60} beats={5} intensity={0.7} color="#fff" stroke={2} /></div>}
          </motion.div>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------ HOW IT WORKS ------------------------------ */
function How() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 75%", "end 55%"] });
  const h = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);
  const steps = [
    { icon: Calendar, t: "Create your account", d: "Sign up with your email. Your profile is created the first time you log in." },
    { icon: Heart, t: "Enter your numbers", d: "Fill in values from a recent checkup, or load a sample profile to see how it works." },
    { icon: Gauge, t: "Read your result", d: "See the risk level, the factors behind it, and your combined health score." },
    { icon: Stethoscope, t: "Talk to a doctor", d: "Book an appointment. Your assigned doctor can see your results and add notes." },
  ];
  return (
    <section id="how" className="max-w-4xl mx-auto px-6 pt-32">
      <Reveal><h2 className="ma-display font-bold text-3xl md:text-5xl text-center" style={{ color: C.ink }}>From numbers to next steps in four moves</h2></Reveal>
      <div ref={ref} className="relative mt-16">
        <div className="absolute left-6 top-2 bottom-2 w-0.5 rounded" style={{ backgroundColor: C.mist }} />
        <motion.div className="absolute left-6 top-2 w-0.5 rounded origin-top" style={{ height: h, background: `linear-gradient(${C.vital}, ${C.pulse})` }} />
        <div className="space-y-10">
          {steps.map((s, i) => (
            <Reveal key={s.t} delay={0.05}>
              <div className="flex gap-6 items-start relative">
                <div className="relative z-10 w-12 h-12 rounded-full flex items-center justify-center shrink-0 text-white" style={{ background: `linear-gradient(135deg, ${C.vital}, #7C6FE0)`, boxShadow: `0 0 0 6px ${C.paper}` }}>
                  <s.icon size={20} />
                </div>
                <div className="pt-1">
                  <h3 className="ma-display font-bold text-xl" style={{ color: C.ink }}>{s.t}</h3>
                  <p className="ma-body mt-1.5 max-w-lg" style={{ color: "#6E6B8A" }}>{s.d}</p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ------------------------------ STATS ------------------------------ */
function Stats() {
  const stats = [
    { n: 5, s: "", l: "trained ML models" },
    { n: 13, s: "", l: "backend modules" },
    { n: 97.6, s: "%", d: 1, l: "symptom checker test accuracy" },
    { n: 4, s: "", l: "conditions screened" },
  ];
  return (
    <section className="max-w-6xl mx-auto px-6 pt-32">
      <div className="relative overflow-hidden rounded-[36px] px-8 py-14" style={{ background: "linear-gradient(120deg, #241F52, #4B3DF2 55%, #8A7AFF)" }}>
        <div className="absolute inset-0 opacity-[0.07]" style={{ backgroundImage: "radial-gradient(#fff 1px, transparent 1px)", backgroundSize: "26px 26px" }} />
        <div className="relative grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((s) => (
            <div key={s.l}>
              <div className="ma-display font-bold text-white text-4xl md:text-5xl"><CountUp to={s.n} suffix={s.s} decimals={s.d || 0} /></div>
              <div className="ma-body text-sm text-white/70 mt-2">{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ------------------------------ FAQ ------------------------------ */
const FAQS = [
  ["Is this a medical diagnosis?", "No. MedAssist AI gives risk estimates from the numbers you enter. It does not replace a doctor, and anything concerning should be checked with one."],
  ["How accurate are the models?", "Each model is trained on a public dataset and tested on held-out data. Accuracy on a public dataset does not guarantee the same accuracy for every person, so treat results as a screening hint."],
  ["Who can see my data?", "Only you, and doctors you are assigned to. Access is enforced on the server with role-based rules, not just hidden in the interface."],
  ["How does the report reader work?", "It uses OCR to read text from a report image, then matches the lab values against standard reference ranges. Clear, well-lit images work best."],
];

function FAQ() {
  const [open, setOpen] = useState(0);
  return (
    <section id="faq" className="max-w-3xl mx-auto px-6 pt-32">
      <Reveal><h2 className="ma-display font-bold text-3xl md:text-5xl text-center" style={{ color: C.ink }}>Questions people ask first</h2></Reveal>
      <div className="mt-12 space-y-3">
        {FAQS.map(([q, a], i) => {
          const isOpen = open === i;
          return (
            <Reveal key={q} delay={i * 0.05} y={16}>
              <div className="rounded-2xl bg-white overflow-hidden" style={{ border: `1px solid ${isOpen ? C.vital : C.mist}`, transition: "border-color .3s" }}>
                <button onClick={() => setOpen(isOpen ? -1 : i)} aria-expanded={isOpen} className="w-full flex items-center justify-between text-left px-6 py-5 ma-display font-semibold" style={{ color: C.ink }}>
                  {q}
                  <motion.span animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.3 }} className="shrink-0 ml-4">{isOpen ? <Minus size={18} color={C.vital} /> : <Plus size={18} color={C.vital} />}</motion.span>
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.35, ease }}>
                      <p className="ma-body text-sm leading-relaxed px-6 pb-5" style={{ color: "#6E6B8A" }}>{a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </Reveal>
          );
        })}
      </div>
    </section>
  );
}

/* ------------------------------ CTA + FOOTER ------------------------------ */
function CTA({ goTo }) {
  return (
    <section className="max-w-6xl mx-auto px-6 pt-32">
      <Reveal>
        <div className="relative overflow-hidden rounded-[36px] px-8 py-16 text-center" style={{ background: "linear-gradient(135deg, #1C1745, #4B3DF2)" }}>
          <div className="absolute inset-x-0 bottom-0 opacity-30"><PulseLine width={1200} height={90} beats={9} intensity={0.8} color="#fff" stroke={2} /></div>
          <h2 className="relative ma-display font-bold text-white text-3xl md:text-5xl max-w-2xl mx-auto leading-[1.15]">Your first check takes about two minutes</h2>
          <p className="relative ma-body text-white/75 mt-4">No cards, no setup. Create an account and run a model.</p>
          <div className="relative mt-8"><Button variant="ghostDark" onClick={() => goTo("auth")}>Create your account <ArrowRight size={16} /></Button></div>
        </div>
      </Reveal>
    </section>
  );
}

function Footer() {
  return (
    <footer className="max-w-6xl mx-auto px-6 py-14 mt-10 flex flex-col md:flex-row items-center justify-between gap-3 ma-body text-sm" style={{ color: "#9491AC" }}>
      <div className="flex items-center gap-2 ma-display font-bold" style={{ color: C.ink }}><Activity size={18} color={C.vital} /> MedAssist AI</div>
      <div>A personal project. Not a medical device and not a substitute for professional advice.</div>
    </footer>
  );
}

/* ------------------------------ PAGE ------------------------------ */
export default function Landing({ goTo }) {
  return (
    <div style={{ backgroundColor: C.paper }} className="min-h-screen">
      <Nav goTo={goTo} />
      <Hero goTo={goTo} />
      <QuickBar goTo={goTo} />
      <Marquee />
      <Features />
      <How />
      <Stats />
      <FAQ />
      <CTA goTo={goTo} />
      <Footer />
    </div>
  );
}
