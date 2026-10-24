// State Management
let currentTab = "dashboard";
let studentsData = [];
let dashboardBarChart = null;
let dashboardPieChart = null;
let analyticsBarChart = null;
let analyticsPieChart = null;
let analyticsSubjectChart = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupNavigation();
  setupAuth();
  loadDashboardData();
  loadStudents();
  loadAttendance();
  loadMarks();
  loadAnalytics();
  loadFullReport();
  loadRiskAnalysis();

  // Search input listener
  const searchInput = document.getElementById("students-search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      renderStudentsTable(studentsData.filter(s => 
        s.name.toLowerCase().includes(q) ||
        s.roll_no.toLowerCase().includes(q) ||
        (s.city && s.city.toLowerCase().includes(q)) ||
        (s.class && s.class.toLowerCase().includes(q))
      ));
    });
  }

  // Attendance filter listeners
  const attDate = document.getElementById("attendance-date-filter");
  const attStudent = document.getElementById("attendance-student-filter");
  if (attDate) attDate.addEventListener("change", loadAttendance);
  if (attStudent) attStudent.addEventListener("change", loadAttendance);

  // Marks filter listener
  const marksStudent = document.getElementById("marks-student-filter");
  if (marksStudent) marksStudent.addEventListener("change", loadMarks);

  // Mobile toggle
  const mobileToggle = document.getElementById("mobile-toggle");
  if (mobileToggle) {
    mobileToggle.addEventListener("click", () => {
      document.querySelector(".sidebar").classList.toggle("mobile-open");
    });
  }

  // Set default dates
  const today = new Date().toISOString().split("T")[0];
  const addAttDate = document.getElementById("add-att-date");
  const bulkAttDate = document.getElementById("bulk-att-date");
  if (addAttDate) addAttDate.value = today;
  if (bulkAttDate) bulkAttDate.value = today;
});

// ================= TOAST NOTIFICATIONS =================

function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  const icon = type === "success" ? "fa-circle-check text-success" : (type === "error" ? "fa-circle-xmark text-danger" : "fa-circle-info text-info");
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ================= THEME TOGGLE =================

function initTheme() {
  const saved = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeIcon(saved);

  const toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme");
      const next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
      updateThemeIcon(next);
      // Re-render charts for theme colors
      loadAnalytics();
      loadDashboardData();
    });
  }
}

function updateThemeIcon(theme) {
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  btn.innerHTML = theme === "dark" ? `<i class="fa-solid fa-sun"></i>` : `<i class="fa-solid fa-moon"></i>`;
}

// ================= NAVIGATION =================

function setupNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const tab = item.getAttribute("data-tab");
      switchTab(tab);
    });
  });

  // Handle URL hash
  const hash = window.location.hash.replace("#", "");
  if (hash) {
    switchTab(hash);
  }
}

function switchTab(tabId) {
  const panes = document.querySelectorAll(".tab-pane");
  const navItems = document.querySelectorAll(".nav-item");
  const targetPane = document.getElementById(`tab-${tabId}`);

  if (!targetPane) return;

  panes.forEach(p => p.classList.remove("active"));
  navItems.forEach(n => n.classList.remove("active"));

  targetPane.classList.add("active");
  const activeNav = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
  if (activeNav) activeNav.classList.add("active");

  // Update Breadcrumb
  const pageTitle = activeNav ? activeNav.querySelector("span").textContent : "Dashboard";
  document.getElementById("breadcrumb-page").textContent = pageTitle;
  window.location.hash = tabId;
  currentTab = tabId;

  // Close mobile sidebar if open
  document.querySelector(".sidebar").classList.remove("mobile-open");

  // Refresh tab specific views
  if (tabId === "analytics") {
    loadAnalytics();
  } else if (tabId === "dashboard") {
    loadDashboardData();
  } else if (tabId === "risk") {
    loadRiskAnalysis();
  } else if (tabId === "agent") {
    runAgentScan();
    loadAgentLogs();
  }
}

// ================= MODAL HELPERS =================

function showModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add("active");
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove("active");
}

window.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal")) {
    e.target.classList.remove("active");
  }
});

// ================= AUTHENTICATION (Screens 1 & 2) =================

function setupAuth() {
  const btnAuth = document.getElementById("btn-show-auth");
  if (btnAuth) {
    btnAuth.addEventListener("click", () => showModal("modal-auth"));
  }

  fetch("/api/auth/me")
    .then(r => r.json())
    .then(data => {
      if (data.authenticated && data.user) {
        setAuthUser(data.user.username);
      }
    })
    .catch(() => {});
}

function setAuthUser(name) {
  document.getElementById("nav-username").textContent = name;
  document.getElementById("nav-user-avatar").textContent = name.charAt(0).toUpperCase();
  document.getElementById("greeting-username").textContent = name;
}

function toggleAuthMode(mode) {
  const loginForm = document.getElementById("form-login");
  const signupForm = document.getElementById("form-signup");
  const btnLogin = document.getElementById("btn-tab-login");
  const btnSignup = document.getElementById("btn-tab-signup");
  const title = document.getElementById("auth-title");

  if (mode === "login") {
    loginForm.classList.remove("hidden");
    signupForm.classList.add("hidden");
    btnLogin.classList.add("active");
    btnSignup.classList.remove("active");
    title.textContent = "Screen 1: User Login";
  } else {
    loginForm.classList.add("hidden");
    signupForm.classList.remove("hidden");
    btnLogin.classList.remove("active");
    btnSignup.classList.add("active");
    title.textContent = "Screen 2: User Registration";
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const u = document.getElementById("login-username").value.trim();
  const p = document.getElementById("login-password").value.trim();
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: u, password: p })
    });
    const data = await res.json();
    if (data.success) {
      setAuthUser(data.user.username);
      closeModal("modal-auth");
      showToast(`Welcome back, ${data.user.username}!`);
      loadDashboardData();
    } else {
      showToast(data.error || "Login failed", "error");
    }
  } catch (err) {
    showToast("Error connecting to server", "error");
  }
}

async function handleSignup(e) {
  e.preventDefault();
  const u = document.getElementById("signup-username").value.trim();
  const em = document.getElementById("signup-email").value.trim();
  const p = document.getElementById("signup-password").value.trim();
  try {
    const res = await fetch("/api/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: u, email: em, password: p })
    });
    const data = await res.json();
    if (data.success) {
      setAuthUser(data.user.username);
      closeModal("modal-auth");
      showToast("Account created successfully!");
      loadDashboardData();
    } else {
      showToast(data.error || "Signup failed", "error");
    }
  } catch (err) {
    showToast("Error connecting to server", "error");
  }
}

// ================= DASHBOARD DATA & CHARTS (Screen 3, 12, 13) =================

async function loadDashboardData() {
  try {
    const res = await fetch("/api/dashboard/stats");
    const data = await res.json();
    if (!data.success) return;

    // KPI numbers
    document.getElementById("kpi-total-students").textContent = data.total_students;
    document.getElementById("kpi-avg-marks").textContent = `${data.avg_marks_pct}%`;
    document.getElementById("kpi-attendance-rate").textContent = `${data.attendance_rate}%`;
    document.getElementById("kpi-total-exams").textContent = data.total_exams;

    // Top students table
    const topTbody = document.querySelector("#dashboard-top-students-table tbody");
    if (topTbody) {
      if (!data.top_students || data.top_students.length === 0) {
        topTbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No student exam records yet</td></tr>`;
      } else {
        topTbody.innerHTML = data.top_students.map((s, idx) => `
          <tr>
            <td><span class="badge-grade ${idx === 0 ? 'grade-a' : 'grade-b'}">#${idx + 1}</span></td>
            <td><strong>${escapeHtml(s.name)}</strong></td>
            <td><span class="badge-roll">${escapeHtml(s.roll_no)}</span></td>
            <td>${escapeHtml(s.class || 'N/A')}</td>
            <td><strong class="text-success">${Math.round(s.avg_score)} / 100</strong></td>
          </tr>
        `).join("");
      }
    }

    // Load Charts for Dashboard
    renderDashboardCharts();
  } catch (err) {
    console.error("Failed to load dashboard stats", err);
  }
}

async function renderDashboardCharts() {
  try {
    const res = await fetch("/api/analytics");
    const data = await res.json();
    if (!data.success) return;

    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const textColor = isDark ? "#9ca3af" : "#475569";
    const gridColor = isDark ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)";

    // Dashboard Bar Chart (Screen 12)
    const ctxBar = document.getElementById("dashboard-bar-chart");
    if (ctxBar) {
      if (dashboardBarChart) dashboardBarChart.destroy();
      dashboardBarChart = new Chart(ctxBar, {
        type: "bar",
        data: {
          labels: data.student_marks.map(s => s.name),
          datasets: [{
            label: "Average Marks",
            data: data.student_marks.map(s => s.avg_marks),
            backgroundColor: "rgba(99, 102, 241, 0.8)",
            borderColor: "#6366f1",
            borderWidth: 1.5,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              grid: { color: gridColor },
              ticks: { color: textColor }
            },
            x: {
              grid: { display: false },
              ticks: { color: textColor }
            }
          }
        }
      });
    }

    // Dashboard Pie Chart (Screen 13)
    const ctxPie = document.getElementById("dashboard-pie-chart");
    if (ctxPie) {
      if (dashboardPieChart) dashboardPieChart.destroy();
      dashboardPieChart = new Chart(ctxPie, {
        type: "doughnut",
        data: {
          labels: ["Present", "Absent"],
          datasets: [{
            data: [data.attendance_dist.Present, data.attendance_dist.Absent],
            backgroundColor: ["#10b981", "#ef4444"],
            borderColor: isDark ? "#111827" : "#ffffff",
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom",
              labels: { color: textColor, padding: 15, font: { size: 12 } }
            }
          },
          cutout: "65%"
        }
      });
    }
  } catch (err) {
    console.error("Chart error", err);
  }
}

// ================= STUDENTS (Screens 4, 5, 6, 7) =================

async function loadStudents() {
  try {
    const res = await fetch("/api/students");
    const data = await res.json();
    if (!data.success) return;

    studentsData = data.students || [];
    renderStudentsTable(studentsData);
    populateStudentSelects(studentsData);
  } catch (err) {
    console.error("Failed to load students", err);
  }
}

function renderStudentsTable(list) {
  const tbody = document.getElementById("students-tbody");
  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No students found</td></tr>`;
    return;
  }

  tbody.innerHTML = list.map(s => `
    <tr>
      <td>${s.id}</td>
      <td><span class="badge-roll">${escapeHtml(s.roll_no)}</span></td>
      <td><strong>${escapeHtml(s.name)}</strong></td>
      <td>${escapeHtml(s.class || '-')}</td>
      <td>${escapeHtml(s.city || '-')}</td>
      <td>${escapeHtml(s.phone || '-')}</td>
      <td class="text-right">
        <button class="btn-action" title="View Official Report Card" style="color:var(--info);" onclick="openReportCard(${s.id})">
          <i class="fa-solid fa-file-invoice"></i>
        </button>
        <button class="btn-action" title="Generate Academic Merit Certificate" style="color:var(--warning);" onclick="openCertificate(${s.id})">
          <i class="fa-solid fa-award"></i>
        </button>
        <button class="btn-action edit" title="Edit Student (Screen 6)" onclick="openEditStudent(${s.id})">
          <i class="fa-solid fa-pen"></i>
        </button>
        <button class="btn-action delete" title="Delete Student (Screen 7)" onclick="confirmDeleteStudent(${s.id}, '${escapeHtml(s.name)}')">
          <i class="fa-solid fa-trash"></i>
        </button>
      </td>
    </tr>
  `).join("");
}

function populateStudentSelects(list) {
  const optionsHtml = `<option value="">-- Choose Student --</option>` +
    list.map(s => `<option value="${s.id}">${escapeHtml(s.name)} (Roll: ${escapeHtml(s.roll_no)})</option>`).join("");

  const attSelect = document.getElementById("add-att-student");
  const marksSelect = document.getElementById("add-marks-student");
  const attFilter = document.getElementById("attendance-student-filter");
  const marksFilter = document.getElementById("marks-student-filter");

  if (attSelect) attSelect.innerHTML = optionsHtml;
  if (marksSelect) marksSelect.innerHTML = optionsHtml;

  const filterOptionsHtml = `<option value="">All Students</option>` +
    list.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`).join("");

  if (attFilter) attFilter.innerHTML = filterOptionsHtml;
  if (marksFilter) marksFilter.innerHTML = filterOptionsHtml;

  // Bulk student list
  const bulkContainer = document.getElementById("bulk-students-list");
  if (bulkContainer) {
    bulkContainer.innerHTML = list.map(s => `
      <div class="bulk-row">
        <div>
          <strong>${escapeHtml(s.name)}</strong>
          <span class="badge-roll ml-2">${escapeHtml(s.roll_no)}</span>
        </div>
        <div class="status-toggle">
          <label><input type="radio" name="bulk_${s.id}" value="P" checked> <span>Present</span></label>
          <label><input type="radio" name="bulk_${s.id}" value="A"> <span>Absent</span></label>
        </div>
      </div>
    `).join("");
  }
}

// Add Student (Screen 4)
async function handleAddStudent(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById("add-student-name").value.trim(),
    roll_no: document.getElementById("add-student-roll").value.trim(),
    class: document.getElementById("add-student-class").value.trim(),
    city: document.getElementById("add-student-city").value.trim(),
    phone: document.getElementById("add-student-phone").value.trim()
  };

  try {
    const res = await fetch("/api/students", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast("Student added successfully (Screen 4)");
      closeModal("modal-add-student");
      document.getElementById("form-add-student").reset();
      loadStudents();
      loadDashboardData();
    } else {
      showToast(data.error || "Failed to add student", "error");
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

// Edit Student (Screen 6)
function openEditStudent(id) {
  const s = studentsData.find(x => x.id === id);
  if (!s) return;
  document.getElementById("edit-student-id").value = s.id;
  document.getElementById("edit-student-name").value = s.name;
  document.getElementById("edit-student-roll").value = s.roll_no;
  document.getElementById("edit-student-class").value = s.class || "";
  document.getElementById("edit-student-city").value = s.city || "";
  document.getElementById("edit-student-phone").value = s.phone || "";
  showModal("modal-edit-student");
}

async function handleUpdateStudent(e) {
  e.preventDefault();
  const id = document.getElementById("edit-student-id").value;
  const payload = {
    name: document.getElementById("edit-student-name").value.trim(),
    roll_no: document.getElementById("edit-student-roll").value.trim(),
    class: document.getElementById("edit-student-class").value.trim(),
    city: document.getElementById("edit-student-city").value.trim(),
    phone: document.getElementById("edit-student-phone").value.trim()
  };

  try {
    const res = await fetch(`/api/students/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast("Student updated successfully (Screen 6)");
      closeModal("modal-edit-student");
      loadStudents();
      loadDashboardData();
    } else {
      showToast(data.error || "Update failed", "error");
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

// Delete Student (Screen 7)
async function confirmDeleteStudent(id, name) {
  if (!confirm(`Are you sure you want to delete student "${name}" (Screen 7)? All marks and attendance records will be removed.`)) return;

  try {
    const res = await fetch(`/api/students/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast("Student record deleted (Screen 7)");
      loadStudents();
      loadAttendance();
      loadMarks();
      loadDashboardData();
    } else {
      showToast(data.error || "Delete failed", "error");
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

// ================= ATTENDANCE (Screens 8 & 9) =================

async function loadAttendance() {
  const dateVal = document.getElementById("attendance-date-filter")?.value || "";
  const studentVal = document.getElementById("attendance-student-filter")?.value || "";

  let url = "/api/attendance?";
  if (dateVal) url += `date=${encodeURIComponent(dateVal)}&`;
  if (studentVal) url += `student_id=${encodeURIComponent(studentVal)}&`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (!data.success) return;

    const tbody = document.getElementById("attendance-tbody");
    if (!tbody) return;

    if (!data.attendance || data.attendance.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No attendance entries found for selected criteria</td></tr>`;
      return;
    }

    tbody.innerHTML = data.attendance.map(a => `
      <tr>
        <td>#${a.id}</td>
        <td><strong>${escapeHtml(a.att_date)}</strong></td>
        <td>${escapeHtml(a.name)}</td>
        <td><span class="badge-roll">${escapeHtml(a.roll_no)}</span></td>
        <td>${escapeHtml(a.class || '-')}</td>
        <td>
          <span class="badge-pill ${a.status === 'P' ? 'badge-present' : 'badge-absent'}">
            <i class="fa-solid ${a.status === 'P' ? 'fa-check' : 'fa-xmark'}"></i>
            ${a.status === 'P' ? 'Present' : 'Absent'}
          </span>
        </td>
        <td class="text-right">
          <button class="btn-action delete" title="Delete Entry" onclick="deleteAttendance(${a.id})">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Failed to load attendance", err);
  }
}

function resetAttendanceFilters() {
  const d = document.getElementById("attendance-date-filter");
  const s = document.getElementById("attendance-student-filter");
  if (d) d.value = "";
  if (s) s.value = "";
  loadAttendance();
}

async function handleAddAttendance(e) {
  e.preventDefault();
  const payload = {
    student_id: document.getElementById("add-att-student").value,
    att_date: document.getElementById("add-att-date").value,
    status: document.getElementById("add-att-status").value
  };

  try {
    const res = await fetch("/api/attendance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast("Attendance recorded (Screen 8)");
      closeModal("modal-add-attendance");
      loadAttendance();
      loadDashboardData();
    } else {
      showToast(data.error || "Failed to add attendance", "error");
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

async function handleBulkAttendance(e) {
  e.preventDefault();
  const attDate = document.getElementById("bulk-att-date").value;
  const records = [];
  studentsData.forEach(s => {
    const radios = document.getElementsByName(`bulk_${s.id}`);
    for (const r of radios) {
      if (r.checked) {
        records.push({ student_id: s.id, status: r.value, att_date: attDate });
        break;
      }
    }
  });

  try {
    const res = await fetch("/api/attendance/bulk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ records })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      closeModal("modal-bulk-attendance");
      loadAttendance();
      loadDashboardData();
    } else {
      showToast(data.error || "Bulk action failed", "error");
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

async function deleteAttendance(id) {
  if (!confirm("Delete this attendance entry?")) return;
  try {
    const res = await fetch(`/api/attendance/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast("Attendance entry deleted");
      loadAttendance();
      loadDashboardData();
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

// ================= MARKS (Screens 10 & 11) =================

async function loadMarks() {
  const studentVal = document.getElementById("marks-student-filter")?.value || "";
  let url = "/api/marks";
  if (studentVal) url += `?student_id=${encodeURIComponent(studentVal)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (!data.success) return;

    const tbody = document.getElementById("marks-tbody");
    if (!tbody) return;

    if (!data.marks || data.marks.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-muted">No marks records found</td></tr>`;
      return;
    }

    tbody.innerHTML = data.marks.map(m => {
      const pct = m.percentage;
      let grade = "grade-f", gradeLabel = "Fail";
      if (pct >= 90) { grade = "grade-a"; gradeLabel = "A+"; }
      else if (pct >= 80) { grade = "grade-a"; gradeLabel = "A"; }
      else if (pct >= 70) { grade = "grade-b"; gradeLabel = "B"; }
      else if (pct >= 60) { grade = "grade-c"; gradeLabel = "C"; }

      return `
        <tr>
          <td>#${m.id}</td>
          <td><span class="badge-roll">${escapeHtml(m.roll_no)}</span></td>
          <td><strong>${escapeHtml(m.name)}</strong></td>
          <td>${escapeHtml(m.class || '-')}</td>
          <td>${escapeHtml(m.subject)}</td>
          <td><strong>${m.marks_obtained}</strong> / ${m.total_marks}</td>
          <td>
            <div style="display:flex; align-items:center; gap:8px;">
              <span>${pct}%</span>
              <div style="flex:1; height:6px; background:var(--bg-input); border-radius:3px; overflow:hidden; max-width:80px;">
                <div style="width:${pct}%; height:100%; background:var(--accent-gradient);"></div>
              </div>
            </div>
          </td>
          <td><span class="badge-grade ${grade}">${gradeLabel}</span></td>
          <td class="text-right">
            <button class="btn-action delete" title="Delete Marks" onclick="deleteMarks(${m.id})">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error("Failed to load marks", err);
  }
}

async function handleAddMarks(e) {
  e.preventDefault();
  const payload = {
    student_id: document.getElementById("add-marks-student").value,
    subject: document.getElementById("add-marks-subject").value.trim(),
    marks_obtained: parseInt(document.getElementById("add-marks-obtained").value, 10),
    total_marks: parseInt(document.getElementById("add-marks-total").value, 10)
  };

  try {
    const res = await fetch("/api/marks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast("Marks recorded successfully (Screen 10)");
      closeModal("modal-add-marks");
      document.getElementById("form-add-marks").reset();
      loadMarks();
      loadDashboardData();
    } else {
      showToast(data.error || "Failed to add marks", "error");
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

async function deleteMarks(id) {
  if (!confirm("Delete this marks entry?")) return;
  try {
    const res = await fetch(`/api/marks/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast("Marks entry removed");
      loadMarks();
      loadDashboardData();
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

// ================= ANALYTICS (Screens 12 & 13) =================

async function loadAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    const data = await res.json();
    if (!data.success) return;

    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const textColor = isDark ? "#9ca3af" : "#475569";
    const gridColor = isDark ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)";

    // Screen 12: Bar Chart
    const ctxBar = document.getElementById("analytics-bar-chart");
    if (ctxBar) {
      if (analyticsBarChart) analyticsBarChart.destroy();
      analyticsBarChart = new Chart(ctxBar, {
        type: "bar",
        data: {
          labels: data.student_marks.map(s => s.name),
          datasets: [{
            label: "Average Marks",
            data: data.student_marks.map(s => s.avg_marks),
            backgroundColor: [
              "rgba(99, 102, 241, 0.8)",
              "rgba(168, 85, 247, 0.8)",
              "rgba(59, 130, 246, 0.8)",
              "rgba(16, 185, 129, 0.8)",
              "rgba(245, 158, 11, 0.8)",
              "rgba(236, 72, 153, 0.8)"
            ],
            borderColor: "#6366f1",
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              grid: { color: gridColor },
              ticks: { color: textColor }
            },
            x: {
              grid: { display: false },
              ticks: { color: textColor }
            }
          }
        }
      });
    }

    // Screen 13: Attendance Pie Chart
    const ctxPie = document.getElementById("analytics-pie-chart");
    if (ctxPie) {
      if (analyticsPieChart) analyticsPieChart.destroy();
      analyticsPieChart = new Chart(ctxPie, {
        type: "pie",
        data: {
          labels: ["Present (P)", "Absent (A)"],
          datasets: [{
            data: [data.attendance_dist.Present, data.attendance_dist.Absent],
            backgroundColor: ["#10b981", "#ef4444"],
            borderColor: isDark ? "#111827" : "#ffffff",
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom",
              labels: { color: textColor, padding: 15, font: { size: 12 } }
            }
          }
        }
      });
    }

    // Subject Performance Chart
    const ctxSub = document.getElementById("analytics-subject-chart");
    if (ctxSub && data.subject_marks && data.subject_marks.length > 0) {
      if (analyticsSubjectChart) analyticsSubjectChart.destroy();
      analyticsSubjectChart = new Chart(ctxSub, {
        type: "bar",
        data: {
          labels: data.subject_marks.map(s => s.subject),
          datasets: [{
            label: "Subject Class Average",
            data: data.subject_marks.map(s => s.avg_marks),
            backgroundColor: "rgba(168, 85, 247, 0.75)",
            borderColor: "#a855f7",
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              grid: { color: gridColor },
              ticks: { color: textColor }
            },
            x: {
              grid: { display: false },
              ticks: { color: textColor }
            }
          }
        }
      });
    }
  } catch (err) {
    console.error("Analytics chart error", err);
  }
}

// ================= FULL REPORTS (Screen 14) =================

async function loadFullReport() {
  try {
    const res = await fetch("/api/reports");
    const data = await res.json();
    if (!data.success) return;

    const tbody = document.getElementById("reports-tbody");
    if (!tbody) return;

    if (!data.report || data.report.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No report data generated yet</td></tr>`;
      return;
    }

    tbody.innerHTML = data.report.map(r => `
      <tr>
        <td><span class="badge-roll">${escapeHtml(r.roll_no)}</span></td>
        <td><strong>${escapeHtml(r.name)}</strong></td>
        <td>${escapeHtml(r.class || '-')}</td>
        <td>${escapeHtml(r.city || '-')}</td>
        <td>${escapeHtml(r.phone || '-')}</td>
        <td>${escapeHtml(r.subject)}</td>
        <td><strong class="text-info">${r.marks_obtained}</strong> / ${r.total_marks}</td>
        <td>
          <span class="badge-pill ${r.status === 'P' ? 'badge-present' : (r.status === 'A' ? 'badge-absent' : '')}">
            ${r.status === 'P' ? 'Present' : (r.status === 'A' ? 'Absent' : 'N/A')}
          </span>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Failed to load full report", err);
  }
}

// ================= EARLY WARNING & RISK ANALYSIS =================

let riskListData = [];

async function loadRiskAnalysis() {
  try {
    const res = await fetch("/api/students/risk-analysis");
    const data = await res.json();
    if (!data.success) return;

    riskListData = data.risk_list || [];

    // Dashboard KPIs
    const kpiDefaulters = document.getElementById("kpi-defaulters");
    const kpiCritical = document.getElementById("kpi-critical");
    if (kpiDefaulters) kpiDefaulters.textContent = data.total_defaulters;
    if (kpiCritical) kpiCritical.textContent = data.total_critical;

    // Risk Tab Counters
    const rCrit = document.getElementById("risk-count-critical");
    const rDef = document.getElementById("risk-count-defaulters");
    const rSafe = document.getElementById("risk-count-safe");
    if (rCrit) rCrit.textContent = data.total_critical;
    if (rDef) rDef.textContent = data.total_defaulters;
    if (rSafe) rSafe.textContent = riskListData.filter(x => x.risk_level === "Safe").length;

    renderRiskTable(riskListData);
  } catch (err) {
    console.error("Failed to load risk analysis", err);
  }
}

function filterRiskTable() {
  const level = document.getElementById("risk-filter-level")?.value;
  if (!level) {
    renderRiskTable(riskListData);
  } else {
    renderRiskTable(riskListData.filter(x => x.risk_level === level));
  }
}

function renderRiskTable(list) {
  const tbody = document.getElementById("risk-tbody");
  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No students match current risk filter criteria</td></tr>`;
    return;
  }

  tbody.innerHTML = list.map(s => {
    let riskBadge = `<span class="badge-risk-safe"><i class="fa-solid fa-shield-halved"></i> Safe</span>`;
    if (s.risk_level === "Critical") {
      riskBadge = `<span class="badge-risk-critical"><i class="fa-solid fa-triangle-exclamation"></i> Critical</span>`;
    } else if (s.risk_level === "Warning") {
      riskBadge = `<span class="badge-risk-warning"><i class="fa-solid fa-bell"></i> Warning</span>`;
    }

    const attBadge = s.is_defaulter
      ? `<span class="text-danger font-bold">${s.attendance_pct}% <span class="badge-alert-pill ml-1">Defaulter</span></span>`
      : `<span class="text-success font-bold">${s.attendance_pct}%</span>`;

    return `
      <tr>
        <td><span class="badge-roll">${escapeHtml(s.roll_no)}</span></td>
        <td><strong>${escapeHtml(s.name)}</strong></td>
        <td>${escapeHtml(s.class || '-')}</td>
        <td>${attBadge}</td>
        <td><strong>${s.avg_score}%</strong> (${s.exam_count} exams)</td>
        <td>${riskBadge}</td>
        <td><small class="text-secondary">${escapeHtml(s.ai_recommendation)}</small></td>
        <td class="text-right">
          <button class="btn-action" title="AI Generate Warning Email" style="color:var(--purple);" onclick="openAgentEmailModal(${s.id})">
            <i class="fa-solid fa-envelope-open-text"></i>
          </button>
          <button class="btn-action" title="View Official Report Card" style="color:var(--info);" onclick="openReportCard(${s.id})">
            <i class="fa-solid fa-file-invoice"></i>
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function simulateParentAlert(name, roll, att) {
  showToast(`Simulated Parent SMS/WhatsApp notice generated for ${name} (Roll: ${roll}) - Attendance: ${att}%`, "warning");
}

// ================= OFFICIAL REPORT CARD GENERATOR =================

async function openReportCard(studentId) {
  try {
    const res = await fetch(`/api/students/${studentId}/report-card`);
    const data = await res.json();
    if (!data.success) {
      showToast(data.error || "Failed to load report card", "error");
      return;
    }

    const container = document.getElementById("report-card-printable");
    if (!container) return;

    const s = data.student;
    const att = data.attendance;
    const marks = data.marks;

    container.innerHTML = `
      <div class="report-card-container">
        <!-- Header -->
        <div class="rc-header">
          <div class="rc-institution">NATIONAL INSTITUTE OF ACADEMIC SCIENCES</div>
          <div class="rc-sub-title">DEPARTMENT OF COMPUTER APPLICATIONS • STUDENT TRANSCRIPT</div>
          <div class="rc-session">ACADEMIC SESSION 2026-2027 • OFFICIAL PERFORMANCE DOSSIER</div>
        </div>

        <!-- Student Meta -->
        <div class="rc-student-meta">
          <div class="rc-meta-item"><strong>Student:</strong> ${escapeHtml(s.name)}</div>
          <div class="rc-meta-item"><strong>Roll No:</strong> <span class="badge-roll">${escapeHtml(s.roll_no)}</span></div>
          <div class="rc-meta-item"><strong>Class:</strong> ${escapeHtml(s.class || 'BCA-3')}</div>
          <div class="rc-meta-item"><strong>City:</strong> ${escapeHtml(s.city || 'N/A')}</div>
          <div class="rc-meta-item"><strong>Contact:</strong> ${escapeHtml(s.phone || 'N/A')}</div>
          <div class="rc-meta-item"><strong>Class Rank:</strong> <span class="badge-grade grade-a">#${data.rank} of All Enrolled</span></div>
        </div>

        <!-- Marks Table -->
        <table class="rc-table">
          <thead>
            <tr>
              <th>Subject / Course Title</th>
              <th>Maximum Marks</th>
              <th>Marks Secured</th>
              <th>Percentage</th>
              <th>Letter Grade</th>
              <th>Grade Points</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${marks.map(m => `
              <tr>
                <td><strong>${escapeHtml(m.subject)}</strong></td>
                <td>${m.total_marks}</td>
                <td><strong>${m.marks_obtained}</strong></td>
                <td>${m.percentage}%</td>
                <td><span class="badge-grade ${m.percentage >= 80 ? 'grade-a' : (m.percentage >= 60 ? 'grade-b' : 'grade-c')}">${m.grade}</span></td>
                <td>${m.points}</td>
                <td><strong class="${m.result === 'PASS' ? 'text-success' : 'text-danger'}">${m.result}</strong></td>
              </tr>
            `).join("")}
          </tbody>
        </table>

        <!-- Summary Grid -->
        <div class="rc-summary-grid">
          <div class="rc-box">
            <h4>ACADEMIC AGGREGATE</h4>
            <p><strong>Total Marks:</strong> ${data.total_obtained} / ${data.total_possible}</p>
            <p><strong>Overall Percentage:</strong> <span class="text-info font-bold">${data.overall_percentage}%</span></p>
            <p><strong>Cumulative GPA:</strong> <span class="text-success font-bold">${data.cgpa} / 10.0</span></p>
          </div>

          <div class="rc-box">
            <h4>ATTENDANCE METRICS</h4>
            <p><strong>Lectures Held:</strong> ${att.total} days</p>
            <p><strong>Attended:</strong> ${att.present} days | <strong>Absence:</strong> ${att.absent} days</p>
            <p><strong>Attendance Rate:</strong> <span class="${att.percentage < 75 ? 'text-danger' : 'text-success'} font-bold">${att.percentage}%</span> ${att.percentage < 75 ? '(DEFAULTER)' : '(COMPLIANT)'}</p>
          </div>
        </div>

        <!-- AI Qualitative Remarks -->
        <div class="rc-remark-box">
          <strong>Advisor &amp; AI Faculty Assessment:</strong> "${escapeHtml(data.ai_remark)}"
        </div>

        <!-- Signatures -->
        <div class="rc-signatures">
          <div class="rc-sig-block">
            <div class="rc-sig-line"></div>
            <span class="rc-sig-title">Class Coordinator</span>
          </div>
          <div class="rc-sig-block">
            <div class="rc-sig-line"></div>
            <span class="rc-sig-title">Controller of Examinations</span>
          </div>
          <div class="rc-sig-block">
            <div class="rc-sig-line"></div>
            <span class="rc-sig-title">Director / Principal</span>
          </div>
        </div>

        <div style="text-align: right; margin-top: 24px; font-size: 0.75rem; color: #64748b;">
          Issue Date: ${data.issue_date} • Verified Electronic Document
        </div>
      </div>
    `;

    showModal("modal-report-card");
  } catch (err) {
    showToast("Error generating report card", "error");
  }
}

function printReportCard() {
  window.print();
}

// ================= MERIT CERTIFICATE GENERATOR =================

async function openCertificate(studentId) {
  try {
    const res = await fetch(`/api/students/${studentId}/report-card`);
    const data = await res.json();
    if (!data.success) {
      showToast(data.error || "Failed to load student honors", "error");
      return;
    }

    const container = document.getElementById("certificate-printable");
    if (!container) return;

    const s = data.student;

    container.innerHTML = `
      <div class="certificate-container">
        <div class="cert-seal">
          <i class="fa-solid fa-award"></i>
        </div>
        <div class="cert-title">Certificate of Academic Excellence</div>
        <div class="cert-subtitle">Presented by the Academic Board of Examiners</div>

        <p style="font-size: 1.1rem; color: #475569; margin-top: 15px;">This certificate is proudly awarded to</p>
        <div class="cert-recipient">${escapeHtml(s.name)}</div>
        
        <p class="cert-desc">
          For demonstrating exceptional academic commitment, achieving a cumulative score of <strong>${data.overall_percentage}%</strong> (CGPA: <strong>${data.cgpa}</strong>) with an outstanding class standing in the Department of Computer Applications, Session 2026–2027.
        </p>

        <div class="cert-signatures">
          <div class="rc-sig-block">
            <div class="rc-sig-line"></div>
            <span class="rc-sig-title">Academic Dean</span>
          </div>
          <div class="rc-sig-block">
            <div class="rc-sig-line"></div>
            <span class="rc-sig-title">Head of Department</span>
          </div>
        </div>

        <small style="display: block; margin-top: 24px; color: #64748b;">Date: ${data.issue_date} • Verification Code: CERT-${s.roll_no}-2026</small>
      </div>
    `;

    showModal("modal-certificate");
  } catch (err) {
    showToast("Error generating certificate", "error");
  }
}

function printCertificate() {
  window.print();
}

// ================= BULK CSV IMPORT =================

function insertSampleCsv() {
  const sample = `Kavita Sen, 107, BCA-3, Delhi, 9876543216\nManish Kumar, 108, BCA-3, Noida, 9876543217\nNeha Gupta, 109, BCA-3, Gurgaon, 9876543218\nHarshita Paul, 110, BCA-3, Faridabad, 9876543219`;
  document.getElementById("bulk-csv-textarea").value = sample;
}

async function handleBulkImport(e) {
  e.preventDefault();
  const text = document.getElementById("bulk-csv-textarea").value.trim();
  if (!text) {
    showToast("Please enter CSV rows", "error");
    return;
  }

  try {
    const res = await fetch("/api/students/bulk-import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ csv_text: text })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      closeModal("modal-bulk-import");
      document.getElementById("form-bulk-import").reset();
      loadStudents();
      loadDashboardData();
      loadRiskAnalysis();
    } else {
      showToast(data.error || "Bulk import failed", "error");
    }
  } catch (err) {
    showToast("Server error during import", "error");
  }
}

// ================= STUDENT SELF-SERVICE PORTAL =================

function quickLookup(roll) {
  document.getElementById("portal-roll-input").value = roll;
  lookupRoll(roll);
}

async function handlePortalLookup(e) {
  e.preventDefault();
  const roll = document.getElementById("portal-roll-input").value.trim();
  if (!roll) return;
  lookupRoll(roll);
}

async function lookupRoll(roll) {
  const container = document.getElementById("portal-result-container");
  if (!container) return;

  container.classList.remove("hidden");
  container.innerHTML = `<div class="card p-4 text-center"><i class="fa-solid fa-spinner fa-spin fa-2x text-primary"></i><p class="mt-2 text-muted">Retrieving academic profile for Roll ${escapeHtml(roll)}...</p></div>`;

  try {
    const res = await fetch(`/api/student-portal/${encodeURIComponent(roll)}`);
    const data = await res.json();
    if (!data.success) {
      container.innerHTML = `
        <div class="card p-4 text-center">
          <i class="fa-solid fa-circle-exclamation text-danger fa-2x"></i>
          <h3 class="mt-2 text-danger">Student Not Found</h3>
          <p class="text-muted">${escapeHtml(data.error || 'No records found')}</p>
        </div>
      `;
      return;
    }

    const s = data.student;
    const att = data.attendance;
    const marks = data.marks;

    container.innerHTML = `
      <div class="card">
        <div class="card-header">
          <div>
            <h3 class="card-title"><i class="fa-solid fa-id-badge text-info"></i> ${escapeHtml(s.name)} (Roll: ${escapeHtml(s.roll_no)})</h3>
            <p class="card-subtitle">Class: ${escapeHtml(s.class || 'BCA-3')} • City: ${escapeHtml(s.city || 'N/A')} • Contact: ${escapeHtml(s.phone || 'N/A')}</p>
          </div>
          <div style="display:flex; gap:10px;">
            <button class="btn-primary" onclick="openReportCard(${s.id})">
              <i class="fa-solid fa-file-invoice"></i> View Official Grade Card
            </button>
            <button class="btn-amber" onclick="openCertificate(${s.id})">
              <i class="fa-solid fa-award"></i> Certificate
            </button>
          </div>
        </div>

        <div class="card-body">
          <div class="stats-grid" style="margin-bottom: 24px;">
            <div class="stat-card">
              <div class="stat-icon icon-purple"><i class="fa-solid fa-calculator"></i></div>
              <div class="stat-info">
                <span class="stat-label">Overall Percentage</span>
                <h3 class="stat-value text-info">${data.overall_percentage}%</h3>
                <span class="stat-meta">CGPA: ${data.cgpa} / 10.0</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon icon-green"><i class="fa-solid fa-calendar-check"></i></div>
              <div class="stat-info">
                <span class="stat-label">Attendance Record</span>
                <h3 class="stat-value ${att.percentage < 75 ? 'text-danger' : 'text-success'}">${att.percentage}%</h3>
                <span class="stat-meta">${att.present} Present / ${att.total} Total Days</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon icon-amber"><i class="fa-solid fa-trophy"></i></div>
              <div class="stat-info">
                <span class="stat-label">Class Standing</span>
                <h3 class="stat-value text-amber">Rank #${data.rank}</h3>
                <span class="stat-meta">Academic Batch</span>
              </div>
            </div>
          </div>

          <h4 style="margin-bottom: 12px; font-size: 1.05rem;"><i class="fa-solid fa-book text-primary"></i> Evaluated Subject Scores:</h4>
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Secured / Total</th>
                  <th>Percentage</th>
                  <th>Letter Grade</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                ${marks.map(m => `
                  <tr>
                    <td><strong>${escapeHtml(m.subject)}</strong></td>
                    <td>${m.marks_obtained} / ${m.total_marks}</td>
                    <td>${m.percentage}%</td>
                    <td><span class="badge-grade ${m.percentage >= 80 ? 'grade-a' : 'grade-b'}">${m.grade}</span></td>
                    <td><strong class="${m.result === 'PASS' ? 'text-success' : 'text-danger'}">${m.result}</strong></td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>

          <div class="rc-remark-box" style="margin-top: 20px;">
            <i class="fa-solid fa-robot"></i> <strong>Academic Faculty Advisor Note:</strong> "${escapeHtml(data.ai_remark)}"
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="card p-4 text-center text-danger">Network error connecting to student portal</div>`;
  }
}

// ================= AI ATTENDANCE RISK EMAIL AGENT =================

let agentCurrentDraft = null;

async function runAgentScan() {
  const tbody = document.getElementById("agent-queue-tbody");
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4"><i class="fa-solid fa-robot fa-spin text-purple"></i> Scanning database for attendance risks (<75%)...</td></tr>`;
  }

  try {
    const res = await fetch("/api/agent/scan-defaulters");
    const data = await res.json();
    if (!data.success) {
      showToast("Scan failed", "error");
      return;
    }

    const queue = data.generated_queue || [];
    
    // Update counters
    const defCount = data.total_defaulters_flagged;
    const critCount = queue.filter(x => x.urgency === "CRITICAL").length;

    const elDef = document.getElementById("agent-stat-defaulters");
    const elQueued = document.getElementById("agent-stat-queued");
    const elCrit = document.getElementById("agent-stat-critical");

    if (elDef) elDef.textContent = defCount;
    if (elQueued) elQueued.textContent = queue.length;
    if (elCrit) elCrit.textContent = critCount;

    if (!tbody) return;

    if (queue.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="9" class="text-center py-4 text-success font-semibold">
            <i class="fa-solid fa-circle-check"></i> Great News! All enrolled students currently satisfy the 75% attendance threshold.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = queue.map(item => `
      <tr>
        <td><span class="badge-roll">${escapeHtml(item.roll_no)}</span></td>
        <td><strong>${escapeHtml(item.student_name)}</strong></td>
        <td>BCA-3</td>
        <td><strong class="text-danger font-bold">${item.attendance_pct}%</strong></td>
        <td><span class="badge-alert-pill">-${(75.0 - item.attendance_pct).toFixed(1)}%</span></td>
        <td><code>${escapeHtml(item.student_email)}</code></td>
        <td>
          <span class="${item.urgency === 'CRITICAL' ? 'badge-risk-critical' : 'badge-risk-warning'}">
            ${escapeHtml(item.urgency)}
          </span>
        </td>
        <td><small class="text-secondary">${escapeHtml(item.subject)}</small></td>
        <td class="text-right">
          <button class="btn-action" title="Preview & Send" style="color:var(--purple);" onclick="openAgentEmailModal(${item.student_id}, '${item.template_type}')">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
          <a class="btn-action" title="Open Mail Client" href="${item.mailto_url}" target="_blank" style="color:var(--info); text-decoration:none;">
            <i class="fa-solid fa-arrow-up-right-from-square"></i>
          </a>
        </td>
      </tr>
    `).join("");

    showToast(`AI Agent scan complete: ${defCount} attendance risk(s) identified.`);
  } catch (err) {
    console.error("Agent scan error", err);
    showToast("Error running attendance scan", "error");
  }
}

async function loadAgentLogs() {
  try {
    const res = await fetch("/api/agent/email-logs");
    const data = await res.json();
    if (!data.success) return;

    const logs = data.logs || [];
    const elSent = document.getElementById("agent-stat-sent");
    if (elSent) elSent.textContent = logs.length;

    const tbody = document.getElementById("agent-logs-tbody");
    if (!tbody) return;

    if (logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No emails logged in audit trail yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = logs.map(l => `
      <tr>
        <td>#${l.id}</td>
        <td><span class="badge-roll">${escapeHtml(l.roll_no)}</span></td>
        <td><strong>${escapeHtml(l.name)}</strong></td>
        <td><code>${escapeHtml(l.recipient_email)}</code></td>
        <td><small>${escapeHtml(l.subject)}</small></td>
        <td><span class="badge-pill">${escapeHtml(l.template_type)}</span></td>
        <td><span class="badge-grade grade-a"><i class="fa-solid fa-check"></i> ${escapeHtml(l.status)}</span></td>
        <td><small class="text-muted">${escapeHtml(l.sent_at)}</small></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Agent logs error", err);
  }
}

async function openAgentEmailModal(studentId, templateType = "auto") {
  try {
    const res = await fetch("/api/agent/generate-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, template_type: templateType })
    });
    const data = await res.json();
    if (!data.success) {
      showToast(data.error || "Failed to generate draft", "error");
      return;
    }

    agentCurrentDraft = data;

    document.getElementById("agent-email-student-id").value = data.student_id;
    document.getElementById("agent-target-name").textContent = data.student_name;
    document.getElementById("agent-target-roll").textContent = data.roll_no;
    document.getElementById("agent-target-rate").textContent = `${data.attendance_pct}% Attendance Rate`;
    document.getElementById("agent-template-select").value = data.template_type;
    document.getElementById("agent-email-recipient").value = data.student_email;
    document.getElementById("agent-email-subject").value = data.subject;
    document.getElementById("agent-email-body").value = data.body_text;
    document.getElementById("agent-email-html-view").innerHTML = data.body_html;
    document.getElementById("agent-mailto-link").href = data.mailto_url;

    setAgentEmailView("plain");
    showModal("modal-agent-email");
  } catch (err) {
    showToast("Error contacting agent service", "error");
  }
}

async function regenerateDraftWithTemplate() {
  const sid = document.getElementById("agent-email-student-id").value;
  const tmpl = document.getElementById("agent-template-select").value;
  if (!sid) return;

  try {
    const res = await fetch("/api/agent/generate-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: parseInt(sid), template_type: tmpl })
    });
    const data = await res.json();
    if (data.success) {
      agentCurrentDraft = data;
      document.getElementById("agent-email-subject").value = data.subject;
      document.getElementById("agent-email-body").value = data.body_text;
      document.getElementById("agent-email-html-view").innerHTML = data.body_html;
      document.getElementById("agent-mailto-link").href = data.mailto_url;
      showToast(`Regenerated draft as "${tmpl}" persona`);
    }
  } catch (err) {
    showToast("Failed to switch template", "error");
  }
}

function setAgentEmailView(mode) {
  const btnPlain = document.getElementById("btn-toggle-plain");
  const btnHtml = document.getElementById("btn-toggle-html");
  const bodyText = document.getElementById("agent-email-body");
  const htmlView = document.getElementById("agent-email-html-view");

  if (mode === "plain") {
    btnPlain.style.fontWeight = "700";
    btnPlain.style.color = "var(--accent-primary)";
    btnHtml.style.fontWeight = "400";
    btnHtml.style.color = "var(--text-muted)";
    bodyText.classList.remove("hidden");
    htmlView.classList.add("hidden");
  } else {
    btnHtml.style.fontWeight = "700";
    btnHtml.style.color = "var(--accent-primary)";
    btnPlain.style.fontWeight = "400";
    btnPlain.style.color = "var(--text-muted)";
    bodyText.classList.add("hidden");
    htmlView.classList.remove("hidden");
  }
}

function copyAgentEmail() {
  const text = document.getElementById("agent-email-body").value;
  navigator.clipboard.writeText(text).then(() => {
    showToast("Email draft copied to clipboard!");
  }).catch(() => {
    showToast("Unable to copy", "error");
  });
}

async function handleSendAgentEmail(e) {
  e.preventDefault();
  const payload = {
    student_id: parseInt(document.getElementById("agent-email-student-id").value),
    recipient_email: document.getElementById("agent-email-recipient").value.trim(),
    subject: document.getElementById("agent-email-subject").value.trim(),
    body: document.getElementById("agent-email-body").value.trim(),
    template_type: document.getElementById("agent-template-select").value
  };

  try {
    const res = await fetch("/api/agent/send-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      closeModal("modal-agent-email");
      loadAgentLogs();
      loadRiskAnalysis();
    } else {
      showToast(data.error || "Failed to record dispatch", "error");
    }
  } catch (err) {
    showToast("Network error", "error");
  }
}

// ================= UTILITIES =================

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}


