const attendanceRows = document.getElementById("attendance-rows");
const leaveRows = document.getElementById("leave-rows");
const summaryNode = document.getElementById("attendance-summary");
const userMetaNode = document.getElementById("user-meta");
const leaveForm = document.getElementById("leave-form");
const leaveFormContainer = document.getElementById("leave-form-container");
const leaveRoleNote = document.getElementById("leave-role-note");
const attendanceEmployeeHeader = document.getElementById("attendance-employee-header");
const attendanceActions = document.querySelector(".actions");

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

async function loadProfile() {
    currentUser = await api("/api/accounts/me/");
    userMetaNode.textContent = `${currentUser.first_name || currentUser.username} - ${(currentUser.role_label || currentUser.role).toUpperCase()} | ${currentUser.department || "No department"}`;
    updateAttendanceSection();
    updateLeaveSection();
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

async function safeRefresh() {
    try {
        await loadProfile();
        await Promise.all([loadAttendance(), loadLeaves()]);
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
