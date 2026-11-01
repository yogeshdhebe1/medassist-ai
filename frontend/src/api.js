const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/v1";

const getToken = () => { try { return localStorage.getItem("access_token"); } catch { return null; } };
const setToken = (t) => { try { t ? localStorage.setItem("access_token", t) : localStorage.removeItem("access_token"); } catch { /* ignore */ } };

async function request(path, { method = "GET", body, auth = true } = {}) {
  const isForm = typeof FormData !== "undefined" && body instanceof FormData;
  const headers = isForm ? {} : { "Content-Type": "application/json" };
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { method, headers, body: body ? (isForm ? body : JSON.stringify(body)) : undefined });
  } catch {
    throw new Error("Cannot reach the backend. Is it running on " + API_BASE + "?");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && auth) { setToken(null); window.dispatchEvent(new Event("medassist:unauthorized")); }
    const msg = data?.error?.message || (Array.isArray(data?.detail) ? `${data.detail[0].loc?.slice(-1)[0]}: ${data.detail[0].msg}` : data?.detail) || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  register: (email, password, phone) => request("/auth/register", { method: "POST", auth: false, body: { email, password, phone } }),
  login: async (email, password) => {
    const d = await request("/auth/login", { method: "POST", auth: false, body: { email, password } });
    setToken(d.access_token);
    return d;
  },
  logout: () => setToken(null),
  isLoggedIn: () => !!getToken(),

  getMyProfile: () => request("/patients/me"),
  updateMyProfile: (body) => request("/patients/me", { method: "PUT", body }),

  predictDiabetes: (b) => request("/ai/disease-prediction/diabetes", { method: "POST", body: b }),
  predictHeartDisease: (b) => request("/ai/disease-prediction/heart-disease", { method: "POST", body: b }),
  predictStroke: (b) => request("/ai/disease-prediction/stroke", { method: "POST", body: b }),
  predictKidneyDisease: (b) => request("/ai/disease-prediction/kidney-disease", { method: "POST", body: b }),

  getKnownSymptoms: () => request("/ai/symptom-checker/symptoms", { auth: false }),
  checkSymptoms: (symptoms) => request("/ai/symptom-checker", { method: "POST", body: { symptoms } }),

  getHealthRiskScore: () => request("/ai/health-risk-score", { method: "POST" }),
  getDietRecommendation: (goal) => request("/ai/recommendations/diet", { method: "POST", body: goal ? { goal } : {} }),
  getExerciseRecommendation: (goal) => request("/ai/recommendations/exercise", { method: "POST", body: goal ? { goal } : {} }),

  startChatSession: () => request("/chat/sessions", { method: "POST" }),
  sendChatMessage: (sessionId, message) => request(`/chat/sessions/${sessionId}/messages`, { method: "POST", body: { message } }),

  listDoctors: () => request("/doctors"),
  uploadReport: (file, reportType) => {
    const form = new FormData();
    form.append("file", file);
    if (reportType) form.append("report_type", reportType);
    return request("/reports/upload", { method: "POST", body: form });
  },
  listMyReports: () => request("/reports"),
  analyzeReport: (id) => request(`/reports/${id}/analyze`, { method: "POST" }),
  getReportAnalysis: (id) => request(`/reports/${id}/analysis`),
  listMyAppointments: () => request("/appointments"),
  bookAppointment: (doctorId, scheduledAt, reason) => request("/appointments", { method: "POST", body: { doctor_id: doctorId, scheduled_at: scheduledAt, reason } }),

  listNotifications: () => request("/notifications"),
  getUnreadCount: () => request("/notifications/unread-count"),
};
