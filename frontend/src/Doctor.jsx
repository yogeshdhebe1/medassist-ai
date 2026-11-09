import React, { useState, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { Users, Calendar, Check, X, RefreshCw, FileText, StickyNote, Clock, UserRound, ChevronRight, Send } from "lucide-react";
import { api } from "./api";
import { C, Button, Card, Badge, ErrorBanner } from "./ui";

const tone = (s) => (s === "confirmed" || s === "completed" ? "vital" : s === "cancelled" ? "pulse" : "amber");
const fmt = (iso) => new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
const asList = (d) => (Array.isArray(d) ? d : d?.items || []);

/* ---------- shared hook: doctor's appointments ---------- */
function useAppointments() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = () => {
    setLoading(true);
    api.listMyAppointments().then((d) => { setList(asList(d)); setError(""); }).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };
  useEffect(load, []);
  const setStatus = async (id, status) => {
    try { await api.updateAppointmentStatus(id, status); load(); } catch (e) { setError(e.message); }
  };
  return { list, loading, error, load, setStatus };
}

function AppointmentRow({ a, setStatus }) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="ma-body text-sm font-medium" style={{ color: C.ink }}>{a.patient_name || "Patient"}</div>
          <div className="ma-body text-xs mt-0.5 flex items-center gap-1" style={{ color: "#6E6B8A" }}><Clock size={12} /> {fmt(a.scheduled_at)}</div>
          {a.reason && <div className="ma-body text-xs mt-1" style={{ color: "#9491AC" }}>“{a.reason}”</div>}
        </div>
        <Badge tone={tone(a.status)}>{a.status}</Badge>
      </div>
      {(a.status === "pending" || a.status === "confirmed") && (
        <div className="flex gap-2 mt-3">
          {a.status === "pending" && (
            <button onClick={() => setStatus(a.id, "confirmed")} className="ma-body text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 text-white" style={{ backgroundColor: C.vital }}>
              <Check size={13} /> Confirm
            </button>
          )}
          {a.status === "confirmed" && (
            <button onClick={() => setStatus(a.id, "completed")} className="ma-body text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 text-white" style={{ backgroundColor: C.vital }}>
              <Check size={13} /> Mark completed
            </button>
          )}
          <button onClick={() => setStatus(a.id, "cancelled")} className="ma-body text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 border" style={{ borderColor: "#F6CBDB", color: "#A8285C" }}>
            <X size={13} /> {a.status === "pending" ? "Decline" : "Cancel"}
          </button>
        </div>
      )}
    </Card>
  );
}

/* =====================================================================
   OVERVIEW
===================================================================== */
export function DoctorOverview({ goTo }) {
  const { list, loading, error, setStatus } = useAppointments();
  const [patients, setPatients] = useState([]);
  const [profile, setProfile] = useState(null);
  useEffect(() => {
    api.listMyPatients().then((d) => setPatients(asList(d))).catch(() => {});
    api.getDoctorProfile().then(setProfile).catch(() => {});
  }, []);

  const now = Date.now();
  const pending = list.filter((a) => a.status === "pending");
  const upcoming = list.filter((a) => a.status === "confirmed" && new Date(a.scheduled_at).getTime() >= now)
    .sort((a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at));
  const stats = [
    { label: "PENDING REQUESTS", value: pending.length, color: "#8A5E1C" },
    { label: "UPCOMING CONFIRMED", value: upcoming.length, color: C.vitalDeep },
    { label: "MY PATIENTS", value: patients.length, color: C.ink },
  ];

  return (
    <div className="ma-fade-up">
      <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>
        {profile?.full_name ? `Good day, ${profile.full_name}` : "Doctor dashboard"}
      </h1>
      <p className="ma-body text-sm mb-6" style={{ color: "#6E6B8A" }}>
        {profile && !profile.full_name ? "Add your name and specialization in Profile so patients can find you." : "Requests waiting for you, and what's coming up."}
      </p>
      <ErrorBanner message={error} />
      <div className="grid grid-cols-3 gap-4 mb-8">
        {stats.map((s) => (
          <Card key={s.label} className="p-5">
            <div className="ma-mono text-[10px]" style={{ color: "#9491AC" }}>{s.label}</div>
            <div className="ma-display text-3xl font-bold mt-1" style={{ color: s.color }}>{loading ? "–" : s.value}</div>
          </Card>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <div className="ma-display font-bold text-sm mb-3" style={{ color: C.ink }}>Needs your response</div>
          {pending.length === 0 ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>No pending requests.</div>
            : <div className="space-y-3">{pending.map((a) => <AppointmentRow key={a.id} a={a} setStatus={setStatus} />)}</div>}
        </div>
        <div>
          <div className="ma-display font-bold text-sm mb-3" style={{ color: C.ink }}>Next up</div>
          {upcoming.length === 0 ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>Nothing scheduled.</div>
            : <div className="space-y-3">{upcoming.slice(0, 4).map((a) => <AppointmentRow key={a.id} a={a} setStatus={setStatus} />)}</div>}
          {list.length > 0 && <button onClick={() => goTo("d-appointments")} className="ma-body text-xs mt-3 flex items-center gap-1" style={{ color: C.vitalDeep }}>All appointments <ChevronRight size={13} /></button>}
        </div>
      </div>
    </div>
  );
}

/* =====================================================================
   APPOINTMENTS
===================================================================== */
export function DoctorAppointments() {
  const { list, loading, error, load, setStatus } = useAppointments();
  const [tab, setTab] = useState("all");
  const tabs = ["all", "pending", "confirmed", "completed", "cancelled"];
  const shown = useMemo(() => (tab === "all" ? list : list.filter((a) => a.status === tab)), [list, tab]);
  return (
    <div className="ma-fade-up max-w-2xl">
      <div className="flex items-center justify-between mb-1">
        <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>Appointments</h1>
        <button onClick={load} aria-label="Refresh"><RefreshCw size={16} color="#9491AC" /></button>
      </div>
      <p className="ma-body text-sm mb-4" style={{ color: "#6E6B8A" }}>Confirming a request also gives you access to that patient's reports.</p>
      <div className="flex gap-1.5 flex-wrap mb-4">
        {tabs.map((t) => (
          <button key={t} onClick={() => setTab(t)} className="ma-body text-xs px-3 py-1.5 rounded-full capitalize"
            style={{ backgroundColor: tab === t ? "#EDEAFB" : "transparent", color: tab === t ? C.vitalDeep : "#6E6B8A", border: `1px solid ${tab === t ? "#D8D2F5" : C.mist}` }}>{t}</button>
        ))}
      </div>
      <ErrorBanner message={error} />
      {loading ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>Loading...</div>
        : shown.length === 0 ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>No {tab === "all" ? "" : tab} appointments.</div>
        : <div className="space-y-3">{shown.map((a) => <AppointmentRow key={a.id} a={a} setStatus={setStatus} />)}</div>}
    </div>
  );
}

/* =====================================================================
   PATIENTS (list + detail: reports + notes)
===================================================================== */
function PatientDetail({ patient, AnalysisView }) {
  const [reports, setReports] = useState([]);
  const [notes, setNotes] = useState([]);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(null); // report id
  const [analysis, setAnalysis] = useState(null);
  const [aLoading, setALoading] = useState(false);
  const [aError, setAError] = useState("");
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setReports([]); setNotes([]); setOpen(null); setAnalysis(null); setError(""); setAError("");
    api.listPatientReports(patient.id).then((d) => setReports(asList(d))).catch((e) => setError(e.message));
    api.listPatientNotes(patient.id).then((d) => setNotes(asList(d))).catch((e) => setError(e.message));
  }, [patient.id]);

  const viewReport = async (r) => {
    setOpen(r.id); setAnalysis(null); setAError(""); setALoading(true);
    try {
      try { setAnalysis(await api.getReportAnalysis(r.id)); }
      catch { setAnalysis(await api.analyzeReport(r.id)); } // not analyzed yet -> run it
    } catch (e) { setAError(e.message); } finally { setALoading(false); }
  };

  const saveNote = async () => {
    setSaving(true);
    try { const n = await api.addPatientNote(patient.id, note); setNotes([n, ...notes]); setNote(""); }
    catch (e) { setError(e.message); } finally { setSaving(false); }
  };

  return (
    <div className="space-y-6">
      <ErrorBanner message={error} />
      <div>
        <div className="ma-mono text-xs mb-2" style={{ color: "#6E6B8A" }}>REPORTS</div>
        {reports.length === 0 ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>This patient hasn't uploaded any reports.</div> : (
          <div className="space-y-2">
            {reports.map((r) => (
              <button key={r.id} onClick={() => viewReport(r)} className="w-full text-left flex items-center justify-between rounded-xl px-4 py-3 border"
                style={{ borderColor: open === r.id ? C.vital : C.mist, backgroundColor: C.white }}>
                <span className="flex items-center gap-2 ma-body text-sm" style={{ color: C.ink }}><FileText size={15} color={C.vital} /> {r.original_filename}</span>
                <span className="ma-mono text-[11px]" style={{ color: "#9491AC" }}>{new Date(r.uploaded_at).toLocaleDateString()}</span>
              </button>
            ))}
          </div>
        )}
        {open && (
          <Card className="p-5 mt-3">
            {aLoading ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>Reading report...</div>
              : aError ? <ErrorBanner message={aError} />
              : analysis ? <AnalysisView data={analysis} /> : null}
          </Card>
        )}
      </div>

      <div>
        <div className="ma-mono text-xs mb-2" style={{ color: "#6E6B8A" }}>CLINICAL NOTES (visible only to you)</div>
        <div className="flex gap-2">
          <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Add a note..." className="ma-body flex-1 px-3 py-2 rounded-lg border outline-none text-sm" style={{ borderColor: C.mist }}
            onKeyDown={(e) => e.key === "Enter" && note.trim() && !saving && saveNote()} />
          <Button disabled={!note.trim() || saving} onClick={saveNote}>{saving ? "..." : "Save"} <Send size={14} /></Button>
        </div>
        <div className="space-y-2 mt-3">
          {notes.length === 0 ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>No notes yet.</div> : notes.map((n) => (
            <div key={n.id} className="rounded-xl px-4 py-3" style={{ backgroundColor: "#F3F1FB" }}>
              <div className="ma-body text-sm" style={{ color: C.ink }}>{n.note}</div>
              <div className="ma-mono text-[10px] mt-1" style={{ color: "#9491AC" }}>{fmt(n.created_at)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function DoctorPatients({ AnalysisView }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sel, setSel] = useState(null);
  useEffect(() => {
    api.listMyPatients().then((d) => { const l = asList(d); setPatients(l); if (l[0]) setSel(l[0]); })
      .catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="ma-fade-up">
      <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>My patients</h1>
      <p className="ma-body text-sm mb-6" style={{ color: "#6E6B8A" }}>Patients appear here after you confirm one of their appointments.</p>
      <ErrorBanner message={error} />
      {loading ? <div className="ma-body text-sm" style={{ color: "#9491AC" }}>Loading...</div>
        : patients.length === 0 ? (
          <Card className="p-8 text-center">
            <Users size={26} className="mx-auto mb-3" color="#B9B3DA" />
            <div className="ma-body text-sm" style={{ color: "#6E6B8A" }}>No patients yet. Confirm an appointment request to add one.</div>
          </Card>
        ) : (
          <div className="grid md:grid-cols-[250px_1fr] gap-6">
            <div className="space-y-2">
              {patients.map((p) => (
                <button key={p.id} onClick={() => setSel(p)} className="w-full text-left px-4 py-3 rounded-xl border flex items-center gap-3"
                  style={{ borderColor: sel?.id === p.id ? C.vital : C.mist, backgroundColor: sel?.id === p.id ? "#F3F1FB" : C.white }}>
                  <UserRound size={18} color={C.vital} />
                  <div>
                    <div className="ma-body text-sm font-medium" style={{ color: C.ink }}>{p.full_name || "Unnamed patient"}</div>
                    <div className="ma-mono text-[10px]" style={{ color: "#9491AC" }}>{[p.gender, p.date_of_birth].filter(Boolean).join(" · ") || "no details"}</div>
                  </div>
                </button>
              ))}
            </div>
            {sel && <motion.div key={sel.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}><PatientDetail patient={sel} AnalysisView={AnalysisView} /></motion.div>}
          </div>
        )}
    </div>
  );
}

/* =====================================================================
   PROFILE
===================================================================== */
export function DoctorProfile() {
  const [p, setP] = useState(null);
  const [form, setForm] = useState({ full_name: "", specialization: "", years_experience: "" });
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    api.getDoctorProfile().then((d) => {
      setP(d);
      setForm({ full_name: d.full_name || "", specialization: d.specialization || "", years_experience: d.years_experience ?? "" });
    }).catch((e) => setError(e.message));
  }, []);
  const save = async () => {
    setSaving(true); setError(""); setSaved(false);
    try {
      const body = { full_name: form.full_name || null, specialization: form.specialization || null,
        years_experience: form.years_experience === "" ? null : Number(form.years_experience) };
      setP(await api.updateDoctorProfile(body)); setSaved(true);
    } catch (e) { setError(e.message); } finally { setSaving(false); }
  };
  const field = "ma-body w-full mt-1 px-3 py-2 rounded-lg border outline-none text-sm";
  return (
    <div className="ma-fade-up max-w-md">
      <h1 className="ma-display text-2xl font-bold" style={{ color: C.ink }}>Profile</h1>
      <p className="ma-body text-sm mb-6" style={{ color: "#6E6B8A" }}>This is what patients see when choosing a doctor.</p>
      <Card className="p-6">
        <ErrorBanner message={error} />
        <div className="space-y-3">
          <div><label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>FULL NAME</label>
            <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="Dr. Meera Shah" className={field} style={{ borderColor: C.mist }} /></div>
          <div><label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>SPECIALIZATION</label>
            <input value={form.specialization} onChange={(e) => setForm({ ...form, specialization: e.target.value })} placeholder="Cardiology" className={field} style={{ borderColor: C.mist }} /></div>
          <div><label className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>YEARS OF EXPERIENCE</label>
            <input type="number" min="0" max="70" value={form.years_experience} onChange={(e) => setForm({ ...form, years_experience: e.target.value })} className={field} style={{ borderColor: C.mist }} /></div>
          {p && <div className="flex items-center gap-2 pt-1"><span className="ma-mono text-xs" style={{ color: "#6E6B8A" }}>VERIFICATION</span><Badge tone={p.is_verified ? "vital" : "amber"}>{p.is_verified ? "verified" : "pending review"}</Badge></div>}
        </div>
        <Button className="w-full mt-5" disabled={saving} onClick={save}>{saving ? "Saving..." : saved ? "Saved ✓" : "Save profile"}</Button>
      </Card>
    </div>
  );
}
