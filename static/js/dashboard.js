const attendanceRows = document.getElementById("attendance-rows");
const leaveRows = document.getElementById("leave-rows");
const summaryNode = document.getElementById("attendance-summary");
const userMetaNode = document.getElementById("user-meta");
const leaveForm = document.getElementById("leave-form");
const leaveFormContainer = document.getElementById("leave-form-container");
const leaveRoleNote = document.getElementById("leave-role-note");
const attendanceEmployeeHeader = document.getElementById("attendance-employee-header");
const attendanceActions = document.querySelector(".actions");
const employeeAccountPanel = document.getElementById("employee-account-panel");
const employeeAccountForm = document.getElementById("employee-account-form");
const employeeAccountNote = document.getElementById("employee-account-note");
const salarySummaryNode = document.getElementById("salary-summary");
const salaryRows = document.getElementById("salary-rows");
const profileForm = document.getElementById("profile-form");
const profileNote = document.getElementById("profile-note");
const dashboardGrid = document.querySelector(".dashboard-grid");

let currentUser = null;

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
    return "";
}

async function api(url, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        ...(options.headers || {}),
    };
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Request failed");
    }
    if (response.status === 204) {
        return null;
    }
    return response.json();
}

function formatDateTime(value) {
    if (!value) {
        return "-";
    }
    return new Date(value).toLocaleString();
}

function statusTag(status) {
    return `<span class="tag ${status}">${status}</span>`;
}

function formatMoney(value) {
    const amount = Number(value || 0);
    return amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function renderAttendance(rows) {
    const isAdmin = currentUser?.role === "manager";
    if (attendanceEmployeeHeader) {
        attendanceEmployeeHeader.hidden = !isAdmin;
    }

    if (!rows.length) {
        attendanceRows.innerHTML = `<tr><td colspan='${isAdmin ? 5 : 4}'>No attendance records yet.</td></tr>`;
        return;
    }
    attendanceRows.innerHTML = rows
        .map(
            (row) => `
            <tr>
                ${isAdmin ? `<td>${row.employee_name || row.employee || "N/A"}</td>` : ""}
                <td>${row.date}</td>
                <td>${formatDateTime(row.time_in)}</td>
                <td>${formatDateTime(row.time_out)}</td>
                <td>${row.worked_hours}</td>
            </tr>
        `
        )
        .join("");
}

function renderLeaves(rows) {
    if (!rows.length) {
        leaveRows.innerHTML = "<tr><td colspan='5'>No leave requests yet.</td></tr>";
        return;
    }

    const isAdmin = currentUser?.role === "manager";
    leaveRows.innerHTML = rows
        .map((row) => {
            const adminButtons =
                isAdmin && row.status === "pending"
                    ? `
                <div class="inline-actions">
                    <button onclick="decideLeave(${row.id}, 'approve')">Approve</button>
                    <button class="secondary" onclick="decideLeave(${row.id}, 'reject')">Reject</button>
                </div>
            `
                    : "-";

            return `
                <tr>
                    <td>${row.employee_name || "N/A"}</td>
                    <td>${row.leave_type}</td>
                    <td>${row.start_date} to ${row.end_date}</td>
                    <td>${statusTag(row.status)}</td>
                    <td>${adminButtons}</td>
                </tr>
            `;
        })
        .join("");
}

function updateAttendanceSection() {
    const isAdmin = currentUser?.role === "manager";
    if (attendanceActions) {
        attendanceActions.hidden = isAdmin;
    }
}

function updateLeaveSection() {
    const isAdmin = currentUser?.role === "manager";
    if (leaveRoleNote) {
        leaveRoleNote.textContent = isAdmin
            ? "Admin accounts review and approve leave requests. Only employees can file leave requests."
            : "Submit your leave request below. Admin will review it once submitted.";
    }
    if (leaveFormContainer) {
        leaveFormContainer.hidden = isAdmin;
    }
}

function updateEmployeeAccountSection() {
    const isAdmin = currentUser?.role === "manager";
    if (employeeAccountPanel) {
        employeeAccountPanel.hidden = !isAdmin;
    }
    if (employeeAccountNote) {
        employeeAccountNote.textContent = isAdmin
            ? "Use this form to create employee login accounts directly in the app."
            : "";
    }
}

function updateProfileSection() {
    if (profileNote) {
        profileNote.textContent = "Update your basic details anytime. Leave password blank if you do not want to change it.";
    }
}

function applyRoleLayout() {
    if (!dashboardGrid) {
        return;
    }

    const isAdmin = currentUser?.role === "manager";
    dashboardGrid.classList.toggle("admin-layout", isAdmin);
    dashboardGrid.classList.toggle("employee-layout", !isAdmin);
}

function hydrateProfileForm() {
    if (!profileForm || !currentUser) {
        return;
    }

    profileForm.elements.username.value = currentUser.username || "";
    profileForm.elements.first_name.value = currentUser.first_name || "";
    profileForm.elements.last_name.value = currentUser.last_name || "";
    profileForm.elements.email.value = currentUser.email || "";
    profileForm.elements.department.value = currentUser.department || "";
    profileForm.elements.password.value = "";
}

async function loadProfile() {
    currentUser = await api("/api/accounts/me/");
    userMetaNode.textContent = `${currentUser.first_name || currentUser.username} - ${(currentUser.role_label || currentUser.role).toUpperCase()} | ${currentUser.department || "No department"}`;
    applyRoleLayout();
    updateAttendanceSection();
    updateLeaveSection();
    updateEmployeeAccountSection();
    updateProfileSection();
    hydrateProfileForm();
}

async function loadAttendance() {
    const [records, summary] = await Promise.all([
        api("/api/attendance/my-records/"),
        api("/api/attendance/summary/"),
    ]);
    renderAttendance(records);
    summaryNode.textContent = currentUser?.role === "manager"
        ? `This month: ${summary.days_logged} attendance record(s) logged across employees, ${summary.total_hours} total hour(s).`
        : `This month: ${summary.days_logged} day(s) logged, ${summary.total_hours} total hour(s).`;
}

async function loadLeaves() {
    const records = await api("/api/leaves/requests/");
    renderLeaves(records);
}

function renderSalaryRows(rows) {
    if (!rows.length) {
        salaryRows.innerHTML = "<tr><td colspan='5'>No salary records for this month yet.</td></tr>";
        return;
    }

    salaryRows.innerHTML = rows
        .map(
            (row) => `
            <tr>
                <td>${row.employee_name || "N/A"}</td>
                <td>${formatMoney(row.hourly_rate)}</td>
                <td>${row.regular_hours}</td>
                <td>${row.overtime_hours}</td>
                <td>${formatMoney(row.total_pay)}</td>
            </tr>
        `
        )
        .join("");
}

async function loadSalarySummary() {
    const data = await api("/api/attendance/salary-summary/");
    const isAdmin = currentUser?.role === "manager";

    if (isAdmin) {
        renderSalaryRows(data.employees || []);
        salarySummaryNode.textContent = `Manual payroll this month: total regular pay ${formatMoney(data.totals?.regular_pay)}, overtime pay ${formatMoney(data.totals?.overtime_pay)}, combined pay ${formatMoney(data.totals?.total_pay)}.`;
        return;
    }

    const employee = data.employee;
    renderSalaryRows(employee ? [employee] : []);
    salarySummaryNode.textContent = employee
        ? `Your manual salary this month is ${formatMoney(employee.total_pay)} based on ${employee.regular_hours} regular hour(s) and ${employee.overtime_hours} overtime hour(s).`
        : "No salary records for this month yet.";
}

async function safeRefresh() {
    try {
        await loadProfile();
        await Promise.all([loadAttendance(), loadLeaves(), loadSalarySummary()]);
    } catch (error) {
        alert(error.message);
    }
}

document.getElementById("time-in-btn")?.addEventListener("click", async () => {
    try {
        await api("/api/attendance/time-in/", { method: "POST" });
        await loadAttendance();
    } catch (error) {
        alert(error.message);
    }
});

document.getElementById("time-out-btn")?.addEventListener("click", async () => {
    try {
        await api("/api/attendance/time-out/", { method: "POST" });
        await loadAttendance();
    } catch (error) {
        alert(error.message);
    }
});

leaveForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(leaveForm);
    const payload = Object.fromEntries(formData.entries());

    try {
        await api("/api/leaves/requests/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        leaveForm.reset();
        await loadLeaves();
    } catch (error) {
        alert(error.message);
    }
});

employeeAccountForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(employeeAccountForm);
    const payload = Object.fromEntries(formData.entries());

    if (!payload.email) {
        delete payload.email;
    }
    if (!payload.department) {
        delete payload.department;
    }
    if (!payload.hourly_rate) {
        delete payload.hourly_rate;
    }

    try {
        await api("/api/accounts/employees/create/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        employeeAccountForm.reset();
        alert("Employee account created successfully.");
        await loadSalarySummary();
    } catch (error) {
        alert(error.message);
    }
});

profileForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(profileForm);
    const payload = Object.fromEntries(formData.entries());

    if (!payload.email) {
        delete payload.email;
    }
    if (!payload.department) {
        payload.department = "";
    }
    if (!payload.password) {
        delete payload.password;
    }

    try {
        const updated = await api("/api/accounts/me/update/", {
            method: "PATCH",
            body: JSON.stringify(payload),
        });
        currentUser = updated;
        userMetaNode.textContent = `${currentUser.first_name || currentUser.username} - ${(currentUser.role_label || currentUser.role).toUpperCase()} | ${currentUser.department || "No department"}`;
        hydrateProfileForm();
        alert("Profile updated successfully.");
    } catch (error) {
        alert(error.message);
    }
});

async function decideLeave(id, action) {
    const comment = prompt(`Admin comment for ${action}:`) || "";
    try {
        await api(`/api/leaves/requests/${id}/${action}/`, {
            method: "PATCH",
            body: JSON.stringify({ manager_comment: comment }),
        });
        await Promise.all([loadLeaves(), loadAttendance()]);
    } catch (error) {
        alert(error.message);
    }
}

window.decideLeave = decideLeave;

safeRefresh();
