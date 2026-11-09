import React, { useState, useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity, Stethoscope, MessageCircle, Calendar, Search, ChevronRight, Send,
  ArrowRight, Heart, Brain, Droplet, Wind, LogOut, Menu, AlertCircle, RefreshCw, FileText, UploadCloud, Salad, Dumbbell, Check, Users, UserRound
} from "lucide-react";
import { api } from "./api";
import { C, FONTS, PulseLine, riskVisual, RiskWave, Button, Card, Badge, ErrorBanner } from "./ui";
import Landing from "./Landing";
import { DoctorOverview, DoctorAppointments, DoctorPatients, DoctorProfile } from "./Doctor";

/* =====================================================================
   VIEW: AUTH (real API)
===================================================================== */
function Auth({ onAuthed }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("test@example.com");
  const [password, setPassword] = useState("Passw0rd!");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    setError("");
    setInfo("");
    try {
      if (mode === "register") {
        await api.register(email, password, phone || undefined);
        setInfo("Account created. If login fails, the account may need verification (is_verified) in the database.");
        setMode("login");
      } else {
        await api.login(email, password);
        onAuthed();
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const inputCls = "ma-body w-full mt-1 px-3 py-2.5 rounded-lg border outline-none text-sm";
  return (
    <div className="min-h-screen flex items-center justify-center px-6" style={{ backgroundColor: C.paper }}>
      <motion.div className="w-full max-w-sm" initial={{ opacity: 0, y: 24, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}><Card className="p-8">
        <div className="flex items-center gap-2 ma-display font-bold text-lg mb-1" style={{ color: C.ink }}>
          <Activity size={20} color={C.vital} /> MedAssist AI
        </div>
        <p className="ma-body text-sm mb-6" style={{ color: "#6E6B8A" }}>
          {mode === "login" ? "Welcome back — sign in to continue." : "Create your patient account."}
        </p>
        <ErrorBanner message={error} />
        {info && <div className="ma-body text-sm p-3 rounded-lg mb-4" style={{ backgroundColor: "#EDEAFB", color: C.vitalDeep }}>{info}</div>}
        <div className="space-y-3">
          <div>
            <label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>EMAIL</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputCls} style={{ borderColor: C.mist }} />
          </div>
          <div>
            <label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>PASSWORD</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={(e) => e.key === "Enter" && submit()} className={inputCls} style={{ borderColor: C.mist }} />
          </div>
          {mode === "register" && (
            <div>
              <label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>PHONE</label>
              <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91XXXXXXXXXX" className={inputCls} style={{ borderColor: C.mist }} />
            </div>
          )}
        </div>
        <Button className="w-full mt-6" onClick={submit} disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"} <ArrowRight size={16} />
        </Button>
        <div className="text-center mt-5 ma-body text-sm" style={{ color: "#6E6B8A" }}>
          {mode === "login" ? (
            <>New here? <button onClick={() => setMode("register")} className="font-medium" style={{ color: C.vital }}>Create an account</button></>
          ) : (
            <>Already registered? <button onClick={() => setMode("login")} className="font-medium" style={{ color: C.vital }}>Sign in</button></>
          )}
        </div>
      </Card></motion.div>
    </div>
  );
}

/* =====================================================================
   SHARED: APP SHELL
===================================================================== */
function Shell({ view, goTo, children, navItems }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const patientNav = [
    { key: "dashboard", label: "Dashboard", icon: Activity },
    { key: "symptom-checker", label: "Symptom Checker", icon: Stethoscope },
    { key: "disease-risk", label: "Disease Risk", icon: Heart },
    { key: "chat", label: "AI Chat", icon: MessageCircle },
    { key: "reports", label: "Reports", icon: FileText },
    { key: "plan", label: "Lifestyle", icon: Salad },
    { key: "appointments", label: "Appointments", icon: Calendar },
  ];
  const nav = navItems || patientNav;
  const signOut = () => { api.logout(); goTo("auth"); };
  return (
    <div className="min-h-screen ma-body" style={{ backgroundColor: C.paper }}>
      <header className="border-b sticky top-0 z-10" style={{ borderColor: C.mist, backgroundColor: "rgba(247,246,251,0.85)", backdropFilter: "blur(12px)" }}>
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 ma-display font-bold" style={{ color: C.ink }}>
            <Activity size={20} color={C.vital} /> MedAssist AI
          </div>
          <button className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}><Menu size={22} color={C.ink} /></button>
          <div className="hidden md:flex items-center gap-1">
            {nav.map((n) => (
              <button key={n.key} onClick={() => goTo(n.key)} title={n.label} aria-label={n.label} className="ma-body text-sm px-3 py-2 rounded-lg flex items-center gap-1.5 transition-colors"
                style={{ color: view === n.key ? C.vitalDeep : "#5F5A78", backgroundColor: view === n.key ? "#EDEAFB" : "transparent", fontWeight: view === n.key ? 500 : 400 }}>
                <n.icon size={15} /> <span className="hidden lg:inline">{n.label}</span>
              </button>
            ))}
          </div>
          <button onClick={signOut} className="hidden md:flex items-center gap-1.5 ma-body text-sm" style={{ color: "#9491AC" }}>
            <LogOut size={15} /> Sign out
          </button>
        </div>
        {menuOpen && (
          <div className="md:hidden px-6 pb-4 flex flex-col gap-1">
            {nav.map((n) => (
              <button key={n.key} onClick={() => { goTo(n.key); setMenuOpen(false); }} className="text-left text-sm px-3 py-2 rounded-lg flex items-center gap-2" style={{ color: C.ink }}>
                <n.icon size={15} /> {n.label}
              </button>
            ))}
            <button onClick={signOut} className="text-left text-sm px-3 py-2 rounded-lg flex items-center gap-2" style={{ color: "#9491AC" }}><LogOut size={15} /> Sign out</button>
          </div>
        )}
      </header>
      <motion.main key={view} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }} className="max-w-6xl mx-auto px-6 py-8">{children}</motion.main>
    </div>
  );
}

/* =====================================================================
   DASHBOARD
===================================================================== */
function NameCard({ onSaved }) {
  const [name, setName] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const save = async () => {
    setBusy(true); setErr("");
    try { onSaved(await api.updateMyProfile({ full_name: name.trim() })); } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };
  return (
    <Card className="p-5 mb-6">
      <div className="ma-body text-sm font-medium mb-1" style={{ color: C.ink }}>What should we call you?</div>
      <div className="ma-body text-xs mb-3" style={{ color: "#6E6B8A" }}>Your name is shown to doctors you book with.</div>
      <ErrorBanner message={err} />
      <div className="flex gap-2">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name" className="ma-body flex-1 px-3 py-2 rounded-lg border outline-none text-sm" style={{ borderColor: C.mist }} />
        <Button disabled={!name.trim() || busy} onClick={save}>{busy ? "..." : "Save"}</Button>
      </div>
    </Card>
  );
}

function Dashboard({ goTo }) {
  const [profile, setProfile] = useState(null);
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try { setProfile(await api.getMyProfile()); } catch (e) { /* ignore */ }
      try { setRisk(await api.getHealthRiskScore()); } catch (e) { /* no predictions yet */ }
      setLoading(false);
    })();
  }, []);

  const actions = [
    { key: "symptom-checker", icon: Stethoscope, title: "Symptom Checker", body: "Not feeling right? Start here." },
    { key: "disease-risk", icon: Heart, title: "Disease Risk Check", body: "Screen for 4 common conditions." },
    { key: "chat", icon: MessageCircle, title: "Ask AI Health Chat", body: "Get answers to follow-up questions." },
    { key: "appointments", icon: Calendar, title: "Appointments", body: "View or book time with a doctor." },
  ];

  return (
    <div className="ma-fade-up">
      <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>
        {profile?.full_name ? `Welcome back, ${profile.full_name.split(" ")[0]}` : "Welcome back"}
      </h1>
      <p className="ma-body text-sm mb-8" style={{ color: "#6E6B8A" }}>Here's where things stand today.</p>

      {profile && !profile.full_name && <NameCard onSaved={setProfile} />}

      <Card className="p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>HEALTH RISK SCORE</div>
            {loading ? (
              <div className="ma-display text-2xl font-bold mt-1" style={{ color: "#9491AC" }}>Loading...</div>
            ) : risk ? (
              <div className="ma-display text-3xl font-bold mt-1" style={{ color: riskVisual(risk.overall_score / 100).color }}>
                {risk.overall_score}<span className="text-base" style={{ color: "#9491AC" }}>/100</span>
              </div>
            ) : (
              <div className="ma-body text-sm mt-1" style={{ color: "#9491AC" }}>No predictions run yet</div>
            )}
          </div>
          {risk && <Badge tone="vital">{String(risk.trend || "").replace("_", " ")}</Badge>}
        </div>
        {risk ? (
          <>
            <RiskWave probability={risk.overall_score / 100} size="lg" />
            <div className="grid grid-cols-4 gap-3 mt-4">
              {Object.entries(risk.component_scores || {}).map(([k, v]) => (
                <div key={k}>
                  <div className="ma-mono text-[10px] capitalize" style={{ color: "#9491AC" }}>{k}</div>
                  <div className="ma-body text-sm font-medium" style={{ color: v === null ? "#C4BEDB" : C.ink }}>{v === null ? "—" : `${v}%`}</div>
                </div>
              ))}
            </div>
          </>
        ) : (
          !loading && (
            <div className="ma-body text-sm py-6 text-center" style={{ color: "#9491AC" }}>
              Run a Disease Risk Check first, then your aggregated score will appear here.
              <div className="mt-3"><Button onClick={() => goTo("disease-risk")}>Run a check <ArrowRight size={15} /></Button></div>
            </div>
          )
        )}
      </Card>

      <div className="ma-mono text-xs mb-3" style={{ color: "#6E6B8A" }}>QUICK ACTIONS</div>
      <div className="grid md:grid-cols-4 gap-4">
        {actions.map((a, i) => (
          <motion.div key={a.key} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.08, duration: 0.5 }}>
          <Card onClick={() => goTo(a.key)} className="p-5 h-full">
            <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${C.vital}, #7C6FE0)` }}>
              <a.icon size={19} color="#fff" />
            </div>
            <div className="ma-display font-bold mt-3 text-sm" style={{ color: C.ink }}>{a.title}</div>
            <div className="ma-body text-xs mt-1.5" style={{ color: "#9491AC" }}>{a.body}</div>
            <div className="flex items-center gap-1 mt-3 ma-mono text-xs" style={{ color: C.vital }}>Open <ChevronRight size={13} /></div>
          </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

/* =====================================================================
   SYMPTOM CHECKER
===================================================================== */
const MIN_CONFIDENCE = 0.15; // hide low-confidence guesses; they are mostly noise and can alarm users

function SymptomChecker() {
  const [allSymptoms, setAllSymptoms] = useState([]);
  const [selected, setSelected] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingList, setLoadingList] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.getKnownSymptoms().then((d) => setAllSymptoms(d.symptoms || [])).catch((e) => setError(e.message)).finally(() => setLoadingList(false));
  }, []);

  const toggle = (s) => setSelected((cur) => (cur.includes(s) ? cur.filter((x) => x !== s) : [...cur, s]));

  const check = async () => {
    setLoading(true); setError(""); setResult(null);
    try { setResult(await api.checkSymptoms(selected)); } catch (e) { setError(e.message); } finally { setLoading(false); }
  };

  const filtered = allSymptoms.filter((s) => s.includes(search.toLowerCase()));
  const shown = result ? result.predictions.filter((r) => r.confidence >= MIN_CONFIDENCE) : [];

  return (
    <div className="ma-fade-up grid md:grid-cols-2 gap-6">
      <div>
        <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>Symptom Checker</h1>
        <p className="ma-body text-sm mt-1 mb-4" style={{ color: "#6E6B8A" }}>Select everything you're experiencing right now.</p>
        <ErrorBanner message={error} />
        <div className="relative mb-3">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2" color="#9491AC" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search symptoms..." className="ma-body w-full pl-9 pr-3 py-2 rounded-lg border outline-none text-sm" style={{ borderColor: C.mist }} />
        </div>
        {loadingList ? (
          <div className="ma-body text-sm" style={{ color: "#9491AC" }}>Loading symptom list from backend...</div>
        ) : (
          <div className="flex flex-wrap gap-2 max-h-72 overflow-y-auto ma-scrollbar pr-1">
            {filtered.map((s) => (
              <button key={s} onClick={() => toggle(s)} className="ma-body text-sm px-3 py-2 rounded-lg border"
                style={{ borderColor: selected.includes(s) ? C.vital : C.mist, backgroundColor: selected.includes(s) ? "#EDEAFB" : C.white, color: selected.includes(s) ? C.vitalDeep : "#5F5A78" }}>
                {s.replaceAll("_", " ")}
              </button>
            ))}
          </div>
        )}
        <Button className="mt-5" disabled={!selected.length || loading} onClick={check}>
          {loading ? "Analyzing..." : `Check ${selected.length} symptom(s)`} <ArrowRight size={16} />
        </Button>
      </div>

      <Card className="p-6">
        <div className="ma-mono text-xs mb-4" style={{ color: "#6E6B8A" }}>RESULTS</div>
        {!result && !loading && (
          <div className="text-sm ma-body flex flex-col items-center justify-center h-64 text-center" style={{ color: "#9491AC" }}>
            <Stethoscope size={28} className="mb-3" />
            Select symptoms and run a check to see ranked possibilities here.
          </div>
        )}
        {loading && (
          <div className="flex flex-col items-center justify-center h-64">
            <PulseLine width={300} height={60} beats={3} intensity={0.35} color={C.vital} />
            <div className="ma-mono text-xs mt-3" style={{ color: "#9491AC" }}>Running model...</div>
          </div>
        )}
        {result && shown.length === 0 && (
          <div className="ma-body text-sm flex flex-col items-center justify-center h-64 text-center" style={{ color: "#6E6B8A" }}>
            <AlertCircle size={26} className="mb-3" color={C.amber} />
            <div className="font-medium" style={{ color: C.ink }}>Not enough information yet</div>
            <div className="mt-1.5 max-w-xs">None of the possible conditions reached {Math.round(MIN_CONFIDENCE * 100)}% confidence. Add more symptoms for a more reliable result, or speak to a doctor if you are worried.</div>
          </div>
        )}
        {result && shown.length > 0 && (
          <div className="space-y-4">
            {shown.map((r, i) => (
              <div key={r.disease}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="ma-body text-sm font-medium" style={{ color: C.ink }}>{i + 1}. {r.disease}</span>
                  <span className="ma-mono text-sm" style={{ color: C.vitalDeep }}>{Math.round(r.confidence * 100)}%</span>
                </div>
                <div className="h-1.5 rounded-full" style={{ backgroundColor: C.paperDim }}>
                  <div className="h-1.5 rounded-full" style={{ width: `${r.confidence * 100}%`, backgroundColor: i === 0 ? C.vital : C.mistDeep }} />
                </div>
              </div>
            ))}
            <div className="ma-body text-xs" style={{ color: "#9491AC" }}>
              Showing conditions with at least {Math.round(MIN_CONFIDENCE * 100)}% confidence. This is general information, not a diagnosis.
            </div>
            {result.recommend_doctor_visit && (
              <div className="ma-body text-xs p-3 rounded-lg flex items-center gap-2" style={{ backgroundColor: "#FBE0EA", color: "#A8285C" }}>
                <AlertCircle size={14} /> Consider booking a doctor visit based on these results.
              </div>
            )}
            {result.unrecognized_symptoms?.length > 0 && (
              <div className="ma-mono text-xs" style={{ color: "#9491AC" }}>Unrecognized: {result.unrecognized_symptoms.join(", ")}</div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}

/* =====================================================================
   DISEASE RISK CHECK
===================================================================== */
const DISEASE_CONFIGS = {
  diabetes: {
    label: "Diabetes", icon: Droplet, predict: (b) => api.predictDiabetes(b),
    fields: [
      ["pregnancies", "Pregnancies", "number"], ["glucose", "Glucose (mg/dL)", "number"],
      ["blood_pressure", "Blood Pressure", "number"], ["skin_thickness", "Skin Thickness", "number"],
      ["insulin", "Insulin", "number"], ["bmi", "BMI", "number"],
      ["diabetes_pedigree", "Pedigree Fn", "number"], ["age", "Age", "number"],
    ],
    presets: {
      high: { pregnancies: 6, glucose: 180, blood_pressure: 95, skin_thickness: 35, insulin: 200, bmi: 38.5, diabetes_pedigree: 1.2, age: 55 },
      low: { pregnancies: 0, glucose: 85, blood_pressure: 65, skin_thickness: 20, insulin: 80, bmi: 21.0, diabetes_pedigree: 0.2, age: 25 },
    },
  },
  heart: {
    label: "Heart Disease", icon: Heart, predict: (b) => api.predictHeartDisease(b),
    fields: [
      ["age", "Age", "number"], ["sex", "Sex (1=M,0=F)", "number"], ["cp", "Chest Pain (0-3)", "number"],
      ["trestbps", "Resting BP", "number"], ["chol", "Cholesterol", "number"], ["fbs", "Fasting Sugar>120 (0/1)", "number"],
      ["restecg", "Resting ECG (0-2)", "number"], ["thalach", "Max Heart Rate", "number"], ["exang", "Exercise Angina (0/1)", "number"],
      ["oldpeak", "ST Depression", "number"], ["slope", "ST Slope (0-2)", "number"], ["ca", "Vessels (0-4)", "number"], ["thal", "Thal (0-3)", "number"],
    ],
    presets: {
      high: { age: 65, sex: 1, cp: 0, trestbps: 160, chol: 280, fbs: 1, restecg: 1, thalach: 110, exang: 1, oldpeak: 3.5, slope: 1, ca: 3, thal: 3 },
      low: { age: 35, sex: 0, cp: 2, trestbps: 110, chol: 180, fbs: 0, restecg: 0, thalach: 180, exang: 0, oldpeak: 0.2, slope: 2, ca: 0, thal: 1 },
    },
  },
  stroke: {
    label: "Stroke", icon: Brain, predict: (b) => api.predictStroke(b),
    fields: [
      ["gender", "Gender (Male/Female)", "text"], ["age", "Age", "number"], ["hypertension", "Hypertension (0/1)", "number"],
      ["heart_disease", "Heart Disease (0/1)", "number"], ["ever_married", "Ever Married (Yes/No)", "text"],
      ["work_type", "Work Type", "text"], ["residence_type", "Residence (Urban/Rural)", "text"],
      ["avg_glucose_level", "Avg Glucose", "number"], ["bmi", "BMI", "number"], ["smoking_status", "Smoking Status", "text"],
    ],
    presets: {
      high: { gender: "Male", age: 75, hypertension: 1, heart_disease: 1, ever_married: "Yes", work_type: "Private", residence_type: "Urban", avg_glucose_level: 220, bmi: 35, smoking_status: "smokes" },
      low: { gender: "Female", age: 25, hypertension: 0, heart_disease: 0, ever_married: "No", work_type: "Private", residence_type: "Urban", avg_glucose_level: 85, bmi: 22, smoking_status: "never smoked" },
    },
  },
  kidney: {
    label: "Kidney Disease", icon: Wind, predict: (b) => api.predictKidneyDisease(b),
    fields: [
      ["age", "Age", "number"], ["bp", "Blood Pressure", "number"], ["sg", "Specific Gravity", "number"],
      ["al", "Albumin (0-5)", "number"], ["su", "Sugar (0-5)", "number"], ["rbc", "RBC (normal/abnormal)", "text"],
      ["pc", "Pus Cell (normal/abnormal)", "text"], ["pcc", "Pus Clumps (present/notpresent)", "text"],
      ["ba", "Bacteria (present/notpresent)", "text"], ["bgr", "Blood Glucose", "number"], ["bu", "Blood Urea", "number"],
      ["sc", "Serum Creatinine", "number"], ["sod", "Sodium", "number"], ["pot", "Potassium", "number"],
      ["hemo", "Hemoglobin", "number"], ["pcv", "Packed Cell Vol", "number"], ["wc", "WBC Count", "number"],
      ["rc", "RBC Count", "number"], ["htn", "Hypertension (yes/no)", "text"], ["dm", "Diabetes (yes/no)", "text"],
      ["cad", "Coronary Disease (yes/no)", "text"], ["appet", "Appetite (good/poor)", "text"],
      ["pe", "Pedal Edema (yes/no)", "text"], ["ane", "Anemia (yes/no)", "text"],
    ],
    presets: {
      high: { age: 60, bp: 90, sg: 1.010, al: 3, su: 1, rbc: "abnormal", pc: "abnormal", pcc: "present", ba: "notpresent", bgr: 150, bu: 80, sc: 3.5, sod: 135, pot: 5.0, hemo: 9.5, pcv: 28, wc: 9800, rc: 3.5, htn: "yes", dm: "yes", cad: "no", appet: "poor", pe: "yes", ane: "yes" },
      low: { age: 30, bp: 70, sg: 1.025, al: 0, su: 0, rbc: "normal", pc: "normal", pcc: "notpresent", ba: "notpresent", bgr: 95, bu: 25, sc: 0.8, sod: 140, pot: 4.2, hemo: 15.5, pcv: 45, wc: 7000, rc: 5.2, htn: "no", dm: "no", cad: "no", appet: "good", pe: "no", ane: "no" },
    },
  },
};

function DiseaseRisk() {
  const [conditionKey, setConditionKey] = useState(null);
  const [values, setValues] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectCondition = (key) => { setConditionKey(key); setValues(DISEASE_CONFIGS[key].presets.low); setResult(null); setError(""); };
  const loadPreset = (which) => setValues(DISEASE_CONFIGS[conditionKey].presets[which]);
  const updateField = (key, val, type) => setValues((v) => ({ ...v, [key]: type === "number" ? parseFloat(val) : val }));

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try { setResult(await DISEASE_CONFIGS[conditionKey].predict(values)); } catch (e) { setError(e.message); } finally { setLoading(false); }
  };

  const config = conditionKey ? DISEASE_CONFIGS[conditionKey] : null;
  const rv = result ? riskVisual(result.probability) : null;

  return (
    <div className="ma-fade-up">
      <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>Disease Risk Check</h1>
      <p className="ma-body text-sm mt-1 mb-6" style={{ color: "#6E6B8A" }}>Pick a condition, load a sample profile or edit values, then run the real model.</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {Object.entries(DISEASE_CONFIGS).map(([key, c]) => (
          <Card key={key} onClick={() => selectCondition(key)} className="p-5 text-center" style={conditionKey === key ? { borderColor: C.vital, borderWidth: 1.5 } : {}}>
            <c.icon size={22} color={conditionKey === key ? C.vital : "#9491AC"} className="mx-auto" />
            <div className="ma-body text-sm font-medium mt-2" style={{ color: C.ink }}>{c.label}</div>
          </Card>
        ))}
      </div>

      {config && (
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="ma-display font-bold text-sm" style={{ color: C.ink }}>Input values</div>
              <div className="flex gap-2">
                <button onClick={() => loadPreset("low")} className="ma-mono text-xs px-2 py-1 rounded-md" style={{ backgroundColor: C.paperDim, color: C.vitalDeep }}>Load low-risk</button>
                <button onClick={() => loadPreset("high")} className="ma-mono text-xs px-2 py-1 rounded-md" style={{ backgroundColor: C.paperDim, color: "#A8285C" }}>Load high-risk</button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 max-h-96 overflow-y-auto ma-scrollbar pr-1">
              {config.fields.map(([key, label, type]) => (
                <div key={key}>
                  <label className="ma-mono text-[10px]" style={{ color: "#9491AC" }}>{label}</label>
                  <input type={type} step="any" value={Number.isNaN(values[key]) ? "" : values[key] ?? ""} onChange={(e) => updateField(key, e.target.value, type)}
                    className="ma-body w-full mt-0.5 px-2.5 py-1.5 rounded-md border outline-none text-sm" style={{ borderColor: C.mist }} />
                </div>
              ))}
            </div>
            <Button className="w-full mt-4" onClick={run} disabled={loading}>{loading ? "Running..." : "Run prediction"} <ArrowRight size={16} /></Button>
          </Card>

          <Card className="p-6">
            <div className="ma-mono text-xs mb-4" style={{ color: "#6E6B8A" }}>RESULT</div>
            <ErrorBanner message={error} />
            {!result && !loading && !error && (
              <div className="ma-body text-sm text-center py-16" style={{ color: "#9491AC" }}>Run a check to see your risk waveform.</div>
            )}
            {loading && <div className="flex justify-center py-10"><PulseLine width={400} height={70} beats={3} intensity={0.4} color={C.vital} /></div>}
            {result && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Badge tone={rv.label === "low" ? "vital" : rv.label === "medium" ? "amber" : "pulse"}>{rv.label} risk</Badge>
                  <span className="ma-mono text-lg font-medium" style={{ color: rv.color }}>{Math.round(result.probability * 100)}%</span>
                </div>
                <RiskWave probability={result.probability} size="lg" />
                <div className="mt-5">
                  <div className="ma-mono text-xs mb-2" style={{ color: "#6E6B8A" }}>CONTRIBUTING FACTORS</div>
                  <ul className="space-y-1.5">
                    {(result.contributing_factors || []).map((f) => (
                      <li key={f} className="ma-body text-sm flex items-start gap-2" style={{ color: "#4A4560" }}>
                        <span className="mt-1.5 w-1 h-1 rounded-full shrink-0" style={{ backgroundColor: C.vital }} /> {f}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}

/* =====================================================================
   AI CHAT
===================================================================== */
function Chat() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useEffect(() => { api.startChatSession().then((r) => setSessionId(r.session_id || r.id)).catch((e) => setError(e.message)); }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, thinking]);

  const send = async () => {
    if (!input.trim() || !sessionId) return;
    const userMsg = input;
    setMessages((m) => [...m, { sender: "user", text: userMsg }]);
    setInput(""); setThinking(true); setError("");
    try {
      const r = await api.sendChatMessage(sessionId, userMsg);
      setMessages((m) => [...m, { sender: "bot", text: r.reply || r.response || r.content }]);
    } catch (e) { setError(e.message); } finally { setThinking(false); }
  };

  return (
    <div className="ma-fade-up max-w-2xl mx-auto">
      <h1 className="ma-display text-2xl font-bold mb-1" style={{ color: C.ink }}>AI Health Chat</h1>
      <p className="ma-body text-sm mb-4" style={{ color: "#6E6B8A" }}>General guidance, available any time.</p>
      <ErrorBanner message={error} />
      <Card className="flex flex-col" style={{ height: 460 }}>
        <div className="flex-1 overflow-y-auto ma-scrollbar p-5 space-y-4">
          {messages.length === 0 && (
            <div className="ma-body text-sm text-center py-16" style={{ color: "#9491AC" }}>{sessionId ? "Ask a question to get started." : "Connecting to chat service..."}</div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}>
              <div className="ma-body text-sm px-4 py-2.5 rounded-2xl max-w-[80%]"
                style={m.sender === "user" ? { backgroundColor: C.vital, color: C.white, borderBottomRightRadius: 4 } : { backgroundColor: C.paperDim, color: C.ink, borderBottomLeftRadius: 4 }}>
                {m.text}
              </div>
            </div>
          ))}
          {thinking && (
            <div className="flex justify-start"><div className="px-4 py-3 rounded-2xl" style={{ backgroundColor: C.paperDim }}>
              <PulseLine width={70} height={20} beats={1} intensity={0.5} color={C.vital} stroke={2} animate={false} />
            </div></div>
          )}
          <div ref={endRef} />
        </div>
        <div className="p-3 border-t flex gap-2" style={{ borderColor: C.mist }}>
          <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder="Type your question..." disabled={!sessionId}
            className="ma-body flex-1 px-3 py-2 rounded-lg border outline-none text-sm" style={{ borderColor: C.mist }} />
          <Button onClick={send} disabled={!sessionId} className="!px-4"><Send size={16} /></Button>
        </div>
      </Card>
    </div>
  );
}

/* =====================================================================
   LIFESTYLE (diet + exercise plans from the recommendation engine)
===================================================================== */
const GOALS = [
  { key: "", label: "Automatic" },
  { key: "weight_loss", label: "Lose weight" },
  { key: "maintenance", label: "Maintain" },
  { key: "muscle_gain", label: "Build muscle" },
];

function Lifestyle() {
  const [tab, setTab] = useState("diet");
  const [goal, setGoal] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true); setError(""); setData(null);
    const call = tab === "diet" ? api.getDietRecommendation : api.getExerciseRecommendation;
    call(goal || undefined)
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [tab, goal]);

  return (
    <div className="ma-fade-up max-w-3xl">
      <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>Lifestyle Plan</h1>
      <p className="ma-body text-sm mt-1 mb-6" style={{ color: "#6E6B8A" }}>Diet and exercise suggestions based on your profile and your latest risk results.</p>

      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div className="inline-flex p-1 rounded-full" style={{ backgroundColor: C.paperDim }}>
          {[["diet", "Diet", Salad], ["exercise", "Exercise", Dumbbell]].map(([k, label, Icon]) => (
            <button key={k} onClick={() => setTab(k)} className="relative ma-body text-sm font-medium px-5 py-2 rounded-full flex items-center gap-2" style={{ color: tab === k ? C.white : "#5F5A78" }}>
              {tab === k && <motion.span layoutId="lifestyle-tab" className="absolute inset-0 rounded-full" style={{ background: `linear-gradient(135deg, ${C.vital}, #7C6FE0)` }} transition={{ type: "spring", stiffness: 380, damping: 30 }} />}
              <span className="relative flex items-center gap-2"><Icon size={15} /> {label}</span>
            </button>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          {GOALS.map((g) => (
            <button key={g.key} onClick={() => setGoal(g.key)} className="ma-body text-sm px-3.5 py-2 rounded-full border transition-colors"
              style={{ borderColor: goal === g.key ? C.vital : C.mist, backgroundColor: goal === g.key ? "#EDEAFB" : C.white, color: goal === g.key ? C.vitalDeep : "#5F5A78" }}>
              {g.label}
            </button>
          ))}
        </div>
      </div>

      <ErrorBanner message={error} />

      <Card className="p-6">
        {loading && (
          <div className="flex flex-col items-center justify-center py-14">
            <PulseLine width={300} height={60} beats={3} intensity={0.35} color={C.vital} />
            <div className="ma-mono text-xs mt-3" style={{ color: "#9491AC" }}>Building your plan...</div>
          </div>
        )}
        {!loading && data && (
          <motion.div key={tab + goal} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
            <h2 className="ma-display text-xl font-bold" style={{ color: C.ink }}>{data.title}</h2>
            <div className="ma-body text-sm mt-2 p-3 rounded-lg" style={{ backgroundColor: C.paperDim, color: "#5F5A78" }}>
              <span className="font-medium" style={{ color: C.ink }}>Why this plan: </span>{data.rationale}
            </div>
            <ul className="mt-5 space-y-3">
              {data.plan.map((item, i) => (
                <motion.li key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.05 * i }} className="flex items-start gap-3">
                  <span className="mt-0.5 w-5 h-5 rounded-full flex items-center justify-center shrink-0" style={{ backgroundColor: "#EDEAFB" }}><Check size={12} color={C.vital} /></span>
                  <span className="ma-body text-sm leading-relaxed" style={{ color: "#3F3A58" }}>{item}</span>
                </motion.li>
              ))}
            </ul>
            <div className="ma-body text-xs mt-6" style={{ color: "#9491AC" }}>{data.disclaimer}</div>
          </motion.div>
        )}
      </Card>
    </div>
  );
}

/* =====================================================================
   LAB REPORTS (upload -> OCR -> flagged values)
===================================================================== */
function AnalysisView({ data }) {
  const { analysis, ocr_result } = data;
  const found = analysis.abnormal_values.length + analysis.normal_values.length;
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      {found === 0 ? (
        <div className="ma-body text-sm text-center py-10" style={{ color: "#6E6B8A" }}>
          <AlertCircle size={26} className="mx-auto mb-3" color={C.amber} />
          <div className="font-medium" style={{ color: C.ink }}>No known lab values found</div>
          <div className="mt-1.5 max-w-sm mx-auto">Try a clear, well-lit photo or scan of a lab report. Only 12 common tests are recognised, such as hemoglobin, glucose and cholesterol.</div>
        </div>
      ) : (
        <>
          <div className="ma-body text-sm leading-relaxed mb-4" style={{ color: C.ink }}>{analysis.summary}</div>

          {analysis.abnormal_values.length > 0 && (
            <div className="mb-5">
              <div className="ma-mono text-xs mb-2" style={{ color: "#A8285C" }}>OUTSIDE NORMAL RANGE</div>
              <div className="space-y-2">
                {analysis.abnormal_values.map((v, i) => (
                  <motion.div key={v.test} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
                    className="flex items-center justify-between rounded-xl px-4 py-3" style={{ backgroundColor: "#FDF0F5", border: "1px solid #F6CBDB" }}>
                    <div>
                      <div className="ma-body text-sm font-medium" style={{ color: C.ink }}>{v.test}</div>
                      <div className="ma-mono text-[11px]" style={{ color: "#9491AC" }}>normal {v.reference_range}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="ma-display font-bold" style={{ color: C.pulse }}>{v.value} <span className="text-xs font-normal">{v.unit}</span></span>
                      <Badge tone="pulse">{v.flag}</Badge>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {analysis.normal_values.length > 0 && (
            <div className="mb-5">
              <div className="ma-mono text-xs mb-2" style={{ color: "#6E6B8A" }}>WITHIN NORMAL RANGE</div>
              <div className="grid grid-cols-2 gap-2">
                {analysis.normal_values.map((v) => (
                  <div key={v.test} className="rounded-xl px-3 py-2.5" style={{ backgroundColor: C.paperDim }}>
                    <div className="ma-body text-xs" style={{ color: "#6E6B8A" }}>{v.test}</div>
                    <div className="ma-body text-sm font-medium" style={{ color: C.ink }}>{v.value} {v.unit}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {analysis.next_steps && (
            <div className="ma-body text-sm p-3 rounded-lg" style={{ backgroundColor: "#EDEAFB", color: C.vitalDeep }}>
              <span className="font-medium">Suggested next steps: </span>{analysis.next_steps}
            </div>
          )}
        </>
      )}
      <div className="ma-mono text-[11px] mt-4" style={{ color: "#9491AC" }}>
        {Object.keys(ocr_result.extracted_fields || {}).length}
        {` of 12 known tests found`} · general information, not a diagnosis
      </div>
    </motion.div>
  );
}

function Reports() {
  const [reports, setReports] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [file, setFile] = useState(null);
  const [reportType, setReportType] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [activeId, setActiveId] = useState(null);
  const fileRef = useRef(null);

  const loadList = () => {
    api.listMyReports().then((d) => setReports(Array.isArray(d) ? d : [])).catch((e) => setError(e.message)).finally(() => setLoadingList(false));
  };
  useEffect(loadList, []);

  const pickFile = (f) => {
    setError("");
    if (!f) return;
    if (!["image/png", "image/jpeg"].includes(f.type)) {
      setFile(null);
      setError("Only JPG or PNG images can be analysed. Take a photo or screenshot of the report.");
      return;
    }
    setFile(f);
  };

  const uploadAndAnalyze = async () => {
    setError(""); setResult(null);
    try {
      setBusy("Uploading...");
      const rep = await api.uploadReport(file, reportType.trim() || undefined);
      setActiveId(rep.id);
      setBusy("Reading the report...");
      setResult(await api.analyzeReport(rep.id));
      setFile(null); setReportType(""); if (fileRef.current) fileRef.current.value = "";
      loadList();
    } catch (e) {
      setError(e.message);
      loadList();
    } finally {
      setBusy("");
    }
  };

  const openReport = async (id) => {
    setError(""); setResult(null); setActiveId(id); setBusy("Loading analysis...");
    try {
      setResult(await api.getReportAnalysis(id));
    } catch (e) {
      try { setResult(await api.analyzeReport(id)); } catch (e2) { setError(e2.message); }
    } finally {
      setBusy("");
    }
  };

  return (
    <div className="ma-fade-up grid md:grid-cols-2 gap-6">
      <div>
        <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>Lab Reports</h1>
        <p className="ma-body text-sm mt-1 mb-5" style={{ color: "#6E6B8A" }}>Upload a photo of a lab report. We read the values and flag the ones outside the normal range.</p>
        <ErrorBanner message={error} />

        <Card className="p-5">
          <label
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); pickFile(e.dataTransfer.files?.[0]); }}
            className="flex flex-col items-center justify-center text-center rounded-2xl cursor-pointer py-9 px-4 transition-colors"
            style={{ border: `2px dashed ${file ? C.vital : C.mistDeep}`, backgroundColor: file ? "#F3F1FD" : C.paper }}
          >
            <UploadCloud size={30} color={C.vital} />
            <div className="ma-body text-sm font-medium mt-2" style={{ color: C.ink }}>{file ? file.name : "Choose an image or drop it here"}</div>
            <div className="ma-body text-xs mt-1" style={{ color: "#9491AC" }}>{file ? `${(file.size / 1024).toFixed(0)} KB` : "JPG or PNG, up to 15 MB"}</div>
            <input ref={fileRef} type="file" accept="image/png,image/jpeg" className="hidden" onChange={(e) => pickFile(e.target.files?.[0])} />
          </label>
          <div className="mt-4">
            <label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>REPORT TYPE (OPTIONAL)</label>
            <input value={reportType} onChange={(e) => setReportType(e.target.value)} placeholder="e.g. Blood test"
              className="ma-body w-full mt-1 px-3 py-2 rounded-lg border outline-none text-sm" style={{ borderColor: C.mist }} />
          </div>
          <Button className="w-full mt-4" disabled={!file || !!busy} onClick={uploadAndAnalyze}>
            {busy || "Upload and analyze"} {!busy && <ArrowRight size={16} />}
          </Button>
        </Card>

        <div className="ma-mono text-xs mt-6 mb-2" style={{ color: "#6E6B8A" }}>YOUR REPORTS</div>
        {loadingList ? (
          <div className="ma-body text-sm" style={{ color: "#9491AC" }}>Loading...</div>
        ) : reports.length === 0 ? (
          <div className="ma-body text-sm" style={{ color: "#9491AC" }}>No reports yet.</div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto ma-scrollbar pr-1">
            {reports.map((r) => (
              <Card key={r.id} onClick={() => openReport(r.id)} className="px-4 py-3" style={activeId === r.id ? { borderColor: C.vital } : {}}>
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="ma-body text-sm font-medium truncate" style={{ color: C.ink }}>{r.original_filename}</div>
                    <div className="ma-mono text-[11px]" style={{ color: "#9491AC" }}>{new Date(r.uploaded_at).toLocaleString()}{r.report_type ? ` · ${r.report_type}` : ""}</div>
                  </div>
                  <ChevronRight size={16} color="#9491AC" className="shrink-0" />
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Card className="p-6 h-fit">
        <div className="ma-mono text-xs mb-4" style={{ color: "#6E6B8A" }}>ANALYSIS</div>
        {busy && (
          <div className="flex flex-col items-center justify-center py-14">
            <PulseLine width={300} height={60} beats={3} intensity={0.35} color={C.vital} />
            <div className="ma-mono text-xs mt-3" style={{ color: "#9491AC" }}>{busy}</div>
          </div>
        )}
        {!busy && !result && (
          <div className="ma-body text-sm flex flex-col items-center justify-center text-center py-14" style={{ color: "#9491AC" }}>
            <FileText size={28} className="mb-3" />
            Upload a report, or pick one from your list, to see the analysis here.
          </div>
        )}
        {!busy && result && <AnalysisView data={result} />}
      </Card>
    </div>
  );
}

/* =====================================================================
   APPOINTMENTS
===================================================================== */
function Appointments() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [doctors, setDoctors] = useState([]);
  const [doctorId, setDoctorId] = useState("");
  const [date, setDate] = useState("");
  const [reason, setReason] = useState("");
  const [booking, setBooking] = useState(false);
  const [bookError, setBookError] = useState("");

  const load = () => {
    setLoading(true);
    api.listMyAppointments().then((d) => setList(Array.isArray(d) ? d : d.items || [])).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };
  useEffect(load, []);
  useEffect(() => { api.listDoctors().then((d) => setDoctors(Array.isArray(d) ? d : [])).catch(() => setDoctors([])); }, []);

  const book = async () => {
    setBooking(true); setBookError("");
    try {
      await api.bookAppointment(doctorId, new Date(date).toISOString(), reason);
      setDoctorId(""); setDate(""); setReason(""); load();
    } catch (e) { setBookError(e.message); } finally { setBooking(false); }
  };

  const field = "ma-body w-full mt-1 px-3 py-2 rounded-lg border outline-none text-sm";
  return (
    <div className="ma-fade-up grid md:grid-cols-2 gap-6">
      <div>
        <div className="flex items-center justify-between mb-1">
          <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>Appointments</h1>
          <button onClick={load} aria-label="Refresh"><RefreshCw size={16} color="#9491AC" /></button>
        </div>
        <p className="ma-body text-sm mt-1 mb-4" style={{ color: "#6E6B8A" }}>Your upcoming and past bookings.</p>
        <ErrorBanner message={error} />
        {loading ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>Loading...</div>
          : list.length === 0 ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>No appointments yet — book one using the form.</div>
          : (
            <div className="space-y-3">
              {list.map((a) => (
                <Card key={a.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="ma-body text-sm font-medium" style={{ color: C.ink }}>{new Date(a.scheduled_at).toLocaleString()}</div>
                    <Badge tone={a.status === "confirmed" ? "vital" : a.status === "cancelled" ? "pulse" : "amber"}>{a.status}</Badge>
                  </div>
                  {a.reason && <div className="ma-body text-xs mt-1" style={{ color: "#9491AC" }}>{a.reason}</div>}
                </Card>
              ))}
            </div>
          )}
      </div>

      <Card className="p-6 h-fit">
        <div className="ma-display font-bold text-sm mb-4" style={{ color: C.ink }}>Book a new appointment</div>
        <ErrorBanner message={bookError} />
        <div className="space-y-3">
          <div><label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>DOCTOR</label>
            {doctors.length > 0 ? (
              <select value={doctorId} onChange={(e) => setDoctorId(e.target.value)} className={field} style={{ borderColor: C.mist, backgroundColor: C.white }}>
                <option value="">Select a doctor</option>
                {doctors.map((d) => (
                  <option key={d.id} value={d.id}>
                    {(d.full_name || `Doctor ${d.id.slice(0, 8)}`) + (d.specialization ? ` · ${d.specialization}` : "")}
                  </option>
                ))}
              </select>
            ) : (
              <input value={doctorId} onChange={(e) => setDoctorId(e.target.value)} placeholder="No doctors listed yet. Paste a doctor ID" className={field} style={{ borderColor: C.mist }} />
            )}</div>
          <div><label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>DATE & TIME</label>
            <input type="datetime-local" value={date} onChange={(e) => setDate(e.target.value)} className={field} style={{ borderColor: C.mist }} /></div>
          <div><label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>REASON</label>
            <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Annual checkup" className={field} style={{ borderColor: C.mist }} /></div>
        </div>
        <Button className="w-full mt-4" disabled={!doctorId || !date || booking} onClick={book}>{booking ? "Booking..." : "Book appointment"} <Calendar size={15} /></Button>
      </Card>
    </div>
  );
}

/* =====================================================================
   ROOT APP
===================================================================== */
export default function App() {
  const home = () => (api.getRole() === "doctor" ? "d-overview" : "dashboard");
  const [view, setView] = useState(api.isLoggedIn() ? home() : "landing");
  const goTo = (v) => setView(v);

  useEffect(() => {
    const onUnauthorized = () => setView("auth");
    window.addEventListener("medassist:unauthorized", onUnauthorized);
    return () => window.removeEventListener("medassist:unauthorized", onUnauthorized);
  }, []);

  const renderView = () => {
    if (view === "landing") return <Landing goTo={goTo} />;
    if (view === "auth" || !api.isLoggedIn()) return <Auth onAuthed={() => setView(home())} />;
    if (api.getRole() === "doctor") {
      const doctorNav = [
        { key: "d-overview", label: "Overview", icon: Activity },
        { key: "d-patients", label: "Patients", icon: Users },
        { key: "d-appointments", label: "Appointments", icon: Calendar },
        { key: "d-profile", label: "Profile", icon: UserRound },
      ];
      const wrap = (el, v) => <Shell view={v} goTo={goTo} navItems={doctorNav}>{el}</Shell>;
      switch (view) {
        case "d-patients": return wrap(<DoctorPatients AnalysisView={AnalysisView} />, view);
        case "d-appointments": return wrap(<DoctorAppointments />, view);
        case "d-profile": return wrap(<DoctorProfile />, view);
        default: return wrap(<DoctorOverview goTo={goTo} />, "d-overview");
      }
    }
    switch (view) {
      case "symptom-checker": return <Shell view={view} goTo={goTo}><SymptomChecker /></Shell>;
      case "disease-risk": return <Shell view={view} goTo={goTo}><DiseaseRisk /></Shell>;
      case "chat": return <Shell view={view} goTo={goTo}><Chat /></Shell>;
      case "plan": return <Shell view={view} goTo={goTo}><Lifestyle /></Shell>;
      case "reports": return <Shell view={view} goTo={goTo}><Reports /></Shell>;
      case "appointments": return <Shell view={view} goTo={goTo}><Appointments /></Shell>;
      default: return <Shell view="dashboard" goTo={goTo}><Dashboard goTo={goTo} /></Shell>;
    }
  };

  return <div className="ma-body">{FONTS}{renderView()}</div>;
}
