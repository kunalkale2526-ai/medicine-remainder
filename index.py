import { useState, useEffect, useRef } from “react”;

const DAYS = [“Sun”, “Mon”, “Tue”, “Wed”, “Thu”, “Fri”, “Sat”];
const FREQ_OPTIONS = [“Daily”, “Weekly”, “Custom”];

function uuid() {
return Math.random().toString(36).slice(2, 10);
}

function timeToMinutes(t) {
const [h, m] = t.split(”:”).map(Number);
return h * 60 + m;
}

function nowMinutes() {
const d = new Date();
return d.getHours() * 60 + d.getMinutes();
}

function formatTime(t) {
const [h, m] = t.split(”:”).map(Number);
const ampm = h >= 12 ? “PM” : “AM”;
const hh = h % 12 || 12;
return `${hh}:${m.toString().padStart(2, "0")} ${ampm}`;
}

const INITIAL_MEDS = [
{
id: uuid(),
name: “Vitamin D”,
dosage: “1 tablet”,
frequency: “Daily”,
times: [“08:00”],
days: [0, 1, 2, 3, 4, 5, 6],
color: “#34d399”,
doses: {},
},
{
id: uuid(),
name: “Metformin”,
dosage: “500mg”,
frequency: “Daily”,
times: [“07:30”, “19:30”],
days: [0, 1, 2, 3, 4, 5, 6],
color: “#60a5fa”,
doses: {},
},
];

const COLORS = [
“#f472b6”, “#60a5fa”, “#34d399”, “#fb923c”,
“#a78bfa”, “#facc15”, “#f87171”, “#2dd4bf”,
];

export default function App() {
const [meds, setMeds] = useState(INITIAL_MEDS);
const [view, setView] = useState(“dashboard”); // dashboard | add | history
const [now, setNow] = useState(new Date());
const [toasts, setToasts] = useState([]);
const [form, setForm] = useState({
name: “”, dosage: “”, frequency: “Daily”,
times: [“08:00”], days: [0, 1, 2, 3, 4, 5, 6], color: COLORS[0],
});
const alerted = useRef(new Set());

useEffect(() => {
const t = setInterval(() => setNow(new Date()), 30000);
return () => clearInterval(t);
}, []);

// Notification logic
useEffect(() => {
const curMin = nowMinutes();
const today = new Date().getDay();
const todayStr = new Date().toISOString().slice(0, 10);
meds.forEach((med) => {
if (!med.days.includes(today)) return;
med.times.forEach((t) => {
const key = `${med.id}-${todayStr}-${t}`;
if (alerted.current.has(key)) return;
const diff = timeToMinutes(t) - curMin;
if (diff >= 0 && diff <= 1) {
alerted.current.add(key);
addToast(`⏰ Time to take ${med.name} — ${med.dosage}`, “alert”);
}
// Mark missed
if (diff < -1 && diff > -60) {
const doseKey = `${todayStr}-${t}`;
const status = med.doses[doseKey];
if (!status) {
setMeds((prev) =>
prev.map((m) =>
m.id === med.id
? { …m, doses: { …m.doses, [doseKey]: “missed” } }
: m
)
);
}
}
});
});
}, [now, meds]);

function addToast(msg, type = “info”) {
const id = uuid();
setToasts((p) => […p, { id, msg, type }]);
setTimeout(() => setToasts((p) => p.filter((t) => t.id !== id)), 4000);
}

function takeDose(medId, time) {
const todayStr = new Date().toISOString().slice(0, 10);
const key = `${todayStr}-${time}`;
setMeds((prev) =>
prev.map((m) =>
m.id === medId ? { …m, doses: { …m.doses, [key]: “taken” } } : m
)
);
const med = meds.find((m) => m.id === medId);
addToast(`✅ ${med.name} marked as taken!`, “success”);
}

function skipDose(medId, time) {
const todayStr = new Date().toISOString().slice(0, 10);
const key = `${todayStr}-${time}`;
setMeds((prev) =>
prev.map((m) =>
m.id === medId ? { …m, doses: { …m.doses, [key]: “skipped” } } : m
)
);
}

function deleteMed(id) {
setMeds((p) => p.filter((m) => m.id !== id));
addToast(“Medicine removed.”, “info”);
}

function addTime() {
setForm((f) => ({ …f, times: […f.times, “12:00”] }));
}

function removeTime(i) {
setForm((f) => ({ …f, times: f.times.filter((_, idx) => idx !== i) }));
}

function toggleDay(d) {
setForm((f) => ({
…f,
days: f.days.includes(d) ? f.days.filter((x) => x !== d) : […f.days, d],
}));
}

function submitMed() {
if (!form.name.trim()) return addToast(“Please enter a medicine name.”, “error”);
setMeds((p) => […p, { …form, id: uuid(), doses: {} }]);
setForm({
name: “”, dosage: “”, frequency: “Daily”,
times: [“08:00”], days: [0, 1, 2, 3, 4, 5, 6], color: COLORS[0],
});
setView(“dashboard”);
addToast(“Medicine added successfully!”, “success”);
}

const todayStr = now.toISOString().slice(0, 10);
const todayDay = now.getDay();

// Build today’s schedule
const schedule = [];
meds.forEach((med) => {
if (!med.days.includes(todayDay)) return;
med.times.forEach((t) => {
const key = `${todayStr}-${t}`;
schedule.push({
med, time: t, key,
status: med.doses[key] || (timeToMinutes(t) < nowMinutes() - 1 ? “missed” : “pending”),
});
});
});
schedule.sort((a, b) => timeToMinutes(a.time) - timeToMinutes(b.time));

const taken = schedule.filter((s) => s.status === “taken”).length;
const missed = schedule.filter((s) => s.status === “missed”).length;
const pending = schedule.filter((s) => s.status === “pending”).length;
const adherence = schedule.length > 0
? Math.round((taken / (taken + missed)) * 100) || 0 : 100;

return (
<div style={{
minHeight: “100vh”, background: “#0a0f1e”,
fontFamily: “‘DM Sans’, ‘Segoe UI’, sans-serif”,
color: “#e2e8f0”, paddingBottom: 40,
}}>
{/* Ambient bg */}
<div style={{
position: “fixed”, inset: 0, pointerEvents: “none”, zIndex: 0,
background: “radial-gradient(ellipse 80% 50% at 20% 0%, #1e3a5f55 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 80% 100%, #2d1b6922 0%, transparent 60%)”,
}} />

```
{/* Toasts */}
<div style={{ position: "fixed", top: 20, right: 20, zIndex: 999, display: "flex", flexDirection: "column", gap: 8 }}>
{toasts.map((t) => (
<div key={t.id} style={{
background: t.type === "success" ? "#064e3b" : t.type === "alert" ? "#7c2d12" : t.type === "error" ? "#7f1d1d" : "#1e3a5f",
border: `1px solid ${t.type === "success" ? "#34d399" : t.type === "alert" ? "#fb923c" : t.type === "error" ? "#f87171" : "#3b82f6"}`,
color: "#f1f5f9", padding: "10px 16px", borderRadius: 10, fontSize: 14,
maxWidth: 280, boxShadow: "0 4px 20px #0005",
animation: "slideIn 0.3s ease",
}}>{t.msg}</div>
))}
</div>

{/* Header */}
<div style={{
position: "relative", zIndex: 1,
padding: "28px 24px 0", maxWidth: 480, margin: "0 auto",
}}>
<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
<div>
<div style={{ fontSize: 11, letterSpacing: 3, color: "#64748b", textTransform: "uppercase", marginBottom: 4 }}>
{now.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
</div>
<h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: "#f1f5f9" }}>
💊 MedRemind
</h1>
</div>
<div style={{
background: "#1e293b", border: "1px solid #334155",
borderRadius: 12, padding: "6px 14px", fontSize: 15, fontWeight: 600,
}}>
{now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
</div>
</div>

{/* Nav */}
<div style={{ display: "flex", gap: 8, marginTop: 20, marginBottom: 24 }}>
{[["dashboard", "Today"], ["add", "+ Add Med"], ["history", "History"]].map(([v, label]) => (
<button key={v} onClick={() => setView(v)} style={{
padding: "8px 16px", borderRadius: 20, border: "none", cursor: "pointer",
fontSize: 13, fontWeight: 600,
background: view === v ? "#3b82f6" : "#1e293b",
color: view === v ? "#fff" : "#94a3b8",
transition: "all 0.2s",
}}>{label}</button>
))}
</div>

{view === "dashboard" && (
<>
{/* Stats Row */}
<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 20 }}>
{[
{ label: "Taken", val: taken, color: "#34d399", bg: "#064e3b" },
{ label: "Missed", val: missed, color: "#f87171", bg: "#7f1d1d" },
{ label: "Pending", val: pending, color: "#facc15", bg: "#422006" },
].map(({ label, val, color, bg }) => (
<div key={label} style={{
background: bg, border: `1px solid ${color}33`,
borderRadius: 14, padding: "12px 10px", textAlign: "center",
}}>
<div style={{ fontSize: 26, fontWeight: 800, color }}>{val}</div>
<div style={{ fontSize: 11, color: "#94a3b8", marginTop: 2 }}>{label}</div>
</div>
))}
</div>

{/* Adherence */}
<div style={{
background: "#111827", border: "1px solid #1e293b",
borderRadius: 16, padding: "14px 18px", marginBottom: 22,
display: "flex", alignItems: "center", gap: 16,
}}>
<div style={{ flex: 1 }}>
<div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>Today's Adherence</div>
<div style={{
height: 8, background: "#1e293b", borderRadius: 99, overflow: "hidden",
}}>
<div style={{
height: "100%", width: `${adherence}%`,
background: adherence >= 80 ? "#34d399" : adherence >= 50 ? "#facc15" : "#f87171",
borderRadius: 99, transition: "width 0.5s ease",
}} />
</div>
</div>
<div style={{ fontSize: 22, fontWeight: 800, color: adherence >= 80 ? "#34d399" : "#facc15" }}>
{adherence}%
</div>
</div>

{/* Schedule */}
<h2 style={{ margin: "0 0 12px", fontSize: 14, fontWeight: 600, color: "#64748b", letterSpacing: 2, textTransform: "uppercase" }}>
Today's Schedule
</h2>

{schedule.length === 0 ? (
<div style={{
textAlign: "center", padding: "40px 20px",
background: "#111827", borderRadius: 16, color: "#475569",
}}>
No medicines scheduled for today.<br />
<span style={{ cursor: "pointer", color: "#3b82f6" }} onClick={() => setView("add")}>
+ Add one now
</span>
</div>
) : (
<div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
{schedule.map(({ med, time, key, status }) => (
<div key={key} style={{
background: "#111827",
border: `1px solid ${status === "taken" ? "#34d39944" : status === "missed" ? "#f8717144" : "#1e293b"}`,
borderLeft: `4px solid ${med.color}`,
borderRadius: 14, padding: "14px 16px",
display: "flex", alignItems: "center", gap: 12,
opacity: status === "taken" ? 0.7 : 1,
}}>
<div style={{
width: 44, height: 44, borderRadius: 12,
background: med.color + "22", display: "flex",
alignItems: "center", justifyContent: "center",
fontSize: 20,
}}>💊</div>
<div style={{ flex: 1 }}>
<div style={{ fontWeight: 700, fontSize: 15 }}>{med.name}</div>
<div style={{ fontSize: 12, color: "#64748b" }}>{med.dosage} · {formatTime(time)}</div>
</div>
<div>
{status === "taken" ? (
<span style={{ fontSize: 12, color: "#34d399", background: "#064e3b", padding: "4px 10px", borderRadius: 20 }}>✓ Taken</span>
) : status === "missed" ? (
<span style={{ fontSize: 12, color: "#f87171", background: "#7f1d1d", padding: "4px 10px", borderRadius: 20 }}>✗ Missed</span>
) : (
<div style={{ display: "flex", gap: 6 }}>
<button onClick={() => takeDose(med.id, time)} style={{
background: "#34d399", border: "none", borderRadius: 8,
padding: "6px 12px", color: "#fff", fontWeight: 700,
fontSize: 12, cursor: "pointer",
}}>Take</button>
<button onClick={() => skipDose(med.id, time)} style={{
background: "#1e293b", border: "1px solid #334155", borderRadius: 8,
padding: "6px 10px", color: "#94a3b8",
fontSize: 12, cursor: "pointer",
}}>Skip</button>
</div>
)}
</div>
</div>
))}
</div>
)}
</>
)}

{view === "add" && (
<div style={{
background: "#111827", border: "1px solid #1e293b",
borderRadius: 20, padding: 22,
}}>
<h2 style={{ margin: "0 0 20px", fontSize: 18 }}>Add Medicine</h2>

<label style={labelStyle}>Medicine Name</label>
<input value={form.name} onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
placeholder="e.g. Aspirin" style={inputStyle} />

<label style={labelStyle}>Dosage</label>
<input value={form.dosage} onChange={(e) => setForm(f => ({ ...f, dosage: e.target.value }))}
placeholder="e.g. 500mg or 1 tablet" style={inputStyle} />

<label style={labelStyle}>Frequency</label>
<div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
{FREQ_OPTIONS.map((opt) => (
<button key={opt} onClick={() => setForm(f => ({ ...f, frequency: opt }))} style={{
flex: 1, padding: "8px 0", borderRadius: 10, border: "none",
background: form.frequency === opt ? "#3b82f6" : "#1e293b",
color: form.frequency === opt ? "#fff" : "#94a3b8",
fontWeight: 600, fontSize: 13, cursor: "pointer",
}}>{opt}</button>
))}
</div>

<label style={labelStyle}>Reminder Times</label>
{form.times.map((t, i) => (
<div key={i} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
<input type="time" value={t}
onChange={(e) => setForm(f => ({ ...f, times: f.times.map((x, j) => j === i ? e.target.value : x) }))}
style={{ ...inputStyle, flex: 1, marginBottom: 0 }} />
{form.times.length > 1 && (
<button onClick={() => removeTime(i)} style={{
background: "#7f1d1d", border: "none", borderRadius: 8,
color: "#f87171", padding: "0 12px", cursor: "pointer", fontSize: 16,
}}>×</button>
)}
</div>
))}
<button onClick={addTime} style={{
background: "#1e293b", border: "1px dashed #334155",
borderRadius: 10, color: "#64748b", padding: "8px 0",
width: "100%", cursor: "pointer", marginBottom: 16, fontSize: 13,
}}>+ Add another time</button>

<label style={labelStyle}>Days</label>
<div style={{ display: "flex", gap: 6, marginBottom: 16 }}>
{DAYS.map((d, i) => (
<button key={d} onClick={() => toggleDay(i)} style={{
flex: 1, padding: "8px 0", borderRadius: 8, border: "none",
background: form.days.includes(i) ? "#3b82f6" : "#1e293b",
color: form.days.includes(i) ? "#fff" : "#64748b",
fontWeight: 600, fontSize: 11, cursor: "pointer",
}}>{d}</button>
))}
</div>

<label style={labelStyle}>Color Tag</label>
<div style={{ display: "flex", gap: 8, marginBottom: 22, flexWrap: "wrap" }}>
{COLORS.map((c) => (
<div key={c} onClick={() => setForm(f => ({ ...f, color: c }))} style={{
width: 28, height: 28, borderRadius: "50%", background: c,
cursor: "pointer",
border: form.color === c ? "3px solid #fff" : "3px solid transparent",
transition: "border 0.2s",
}} />
))}
</div>

<button onClick={submitMed} style={{
width: "100%", padding: "14px 0", borderRadius: 12,
background: "linear-gradient(135deg, #3b82f6, #6366f1)",
border: "none", color: "#fff", fontSize: 16, fontWeight: 700,
cursor: "pointer", letterSpacing: 0.5,
}}>Save Medicine</button>
</div>
)}

{view === "history" && (
<>
<h2 style={{ margin: "0 0 16px", fontSize: 14, fontWeight: 600, color: "#64748b", letterSpacing: 2, textTransform: "uppercase" }}>
All Medicines
</h2>
{meds.length === 0 ? (
<div style={{ textAlign: "center", color: "#475569", padding: 40 }}>No medicines yet.</div>
) : (
<div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
{meds.map((med) => {
const allDoses = Object.values(med.doses);
const takenCount = allDoses.filter((s) => s === "taken").length;
const missedCount = allDoses.filter((s) => s === "missed").length;
return (
<div key={med.id} style={{
background: "#111827",
border: `1px solid ${med.color}33`,
borderLeft: `4px solid ${med.color}`,
borderRadius: 14, padding: "16px",
}}>
<div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
<div>
<div style={{ fontWeight: 700, fontSize: 16 }}>{med.name}</div>
<div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>
{med.dosage} · {med.frequency}
</div>
<div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>
{med.times.map(formatTime).join(", ")}
</div>
<div style={{ display: "flex", gap: 10, marginTop: 8 }}>
<span style={{ fontSize: 12, color: "#34d399" }}>✓ {takenCount} taken</span>
<span style={{ fontSize: 12, color: "#f87171" }}>✗ {missedCount} missed</span>
</div>
</div>
<button onClick={() => deleteMed(med.id)} style={{
background: "none", border: "1px solid #7f1d1d",
borderRadius: 8, color: "#f87171", padding: "6px 10px",
cursor: "pointer", fontSize: 12,
}}>Delete</button>
</div>
{/* Days chips */}
<div style={{ display: "flex", gap: 4, marginTop: 10, flexWrap: "wrap" }}>
{DAYS.map((d, i) => (
<span key={d} style={{
fontSize: 11, padding: "2px 8px", borderRadius: 20,
background: med.days.includes(i) ? med.color + "33" : "#1e293b",
color: med.days.includes(i) ? med.color : "#475569",
}}>{d}</span>
))}
</div>
</div>
);
})}
</div>
)}
</>
)}
</div>

<style>{`
@keyframes slideIn { from { transform: translateX(40px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
input[type="time"]::-webkit-calendar-picker-indicator { filter: invert(1); }
* { box-sizing: border-box; }
`}</style>
</div>
```

);
}

const labelStyle = {
display: “block”, fontSize: 12, fontWeight: 600,
color: “#64748b”, textTransform: “uppercase”, letterSpacing: 1,
marginBottom: 8,
};

const inputStyle = {
width: “100%”, background: “#0f172a”, border: “1px solid #334155”,
borderRadius: 10, padding: “10px 14px”, color: “#f1f5f9”,
fontSize: 14, marginBottom: 16, outline: “none”,
};
