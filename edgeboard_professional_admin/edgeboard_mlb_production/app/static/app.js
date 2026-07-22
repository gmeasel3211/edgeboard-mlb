(() => {
  "use strict";

  const body = document.body;
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const menuClose = document.querySelector("[data-menu-close]");

  const closeMenu = () => body.classList.remove("menu-open");
  menuToggle?.addEventListener("click", () => body.classList.toggle("menu-open"));
  menuClose?.addEventListener("click", closeMenu);
  document.querySelectorAll(".side-nav a").forEach((link) => link.addEventListener("click", closeMenu));

  function showToast(title, message, kind = "success") {
    const region = document.getElementById("toast-region");
    if (!region) return;
    const toast = document.createElement("div");
    toast.className = `toast ${kind}`;
    toast.innerHTML = `
      <span class="toast-dot"></span>
      <div><strong></strong><span></span></div>
    `;
    toast.querySelector("strong").textContent = title;
    toast.querySelector("span").textContent = message;
    region.appendChild(toast);
    window.setTimeout(() => toast.remove(), 5200);
  }

  function errorMessage(payload, fallback) {
    if (!payload) return fallback;
    if (Array.isArray(payload.detail)) return payload.detail.join(" ");
    return payload.detail || payload.message || fallback;
  }

  document.querySelectorAll("[data-table-search]").forEach((input) => {
    const table = document.getElementById(input.dataset.tableSearch);
    if (!table) return;
    const rows = [...table.querySelectorAll("tbody tr")];
    const empty = document.querySelector("[data-search-empty]");
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      let visible = 0;
      rows.forEach((row) => {
        const match = !query || row.textContent.toLowerCase().includes(query);
        row.hidden = !match;
        if (match) visible += 1;
      });
      if (empty) empty.hidden = visible !== 0;
    });
  });

  const adminButtons = [...document.querySelectorAll("[data-admin-action]")];
  const operationState = document.querySelector("[data-operation-state]");
  const operationDetail = document.querySelector("[data-operation-detail]");
  const operationOutput = document.querySelector("[data-operation-output]");
  const operationJson = document.querySelector("[data-operation-json]");

  function setAdminBusy(busy, label = "System ready", detail = "No action in progress") {
    adminButtons.forEach((button) => {
      button.disabled = busy;
      if (!button.dataset.originalText) button.dataset.originalText = button.textContent.trim();
      button.textContent = busy ? "Working…" : button.dataset.originalText;
    });
    if (operationState) {
      const dot = operationState.querySelector(".pulse-dot");
      const title = operationState.querySelector("b");
      dot?.classList.toggle("working", busy);
      if (title) title.textContent = label;
      if (operationDetail) operationDetail.textContent = detail;
    }
  }

  function showOperationResult(payload) {
    if (!operationOutput || !operationJson) return;
    operationJson.textContent = JSON.stringify(payload, null, 2);
    operationOutput.hidden = false;
  }

  adminButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      const confirmation = button.dataset.confirm;
      if (confirmation && !window.confirm(confirmation)) return;
      const action = button.dataset.adminAction;
      setAdminBusy(true, "Operation running", "Keep this page open while the server completes the request.");
      try {
        const response = await fetch("/admin/actions/refresh", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json" },
          body: JSON.stringify({ action }),
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(errorMessage(payload, "The operation failed."));
        showOperationResult(payload);
        const title = action === "force_official" ? "Official card regenerated" : action === "grade" ? "Grading complete" : "Refresh complete";
        showToast(title, "The server completed the requested operation.");
        setAdminBusy(false, "Operation complete", "Refresh the page to update every dashboard counter.");
      } catch (error) {
        setAdminBusy(false, "Operation failed", error.message || "Unknown server error");
        showToast("Action failed", error.message || "Unknown server error", "error");
      }
    });
  });

  document.querySelector("[data-output-close]")?.addEventListener("click", () => {
    if (operationOutput) operationOutput.hidden = true;
  });

  const settingsForm = document.querySelector("[data-settings-form]");
  settingsForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButtons = [...settingsForm.querySelectorAll("button[type='submit']"), ...document.querySelectorAll("button[form='settings-form']")];
    submitButtons.forEach((button) => button.disabled = true);
    const values = {};
    settingsForm.querySelectorAll("[data-setting-key]").forEach((input) => {
      const scale = Number(input.dataset.scale || 1);
      values[input.dataset.settingKey] = Number(input.value) * scale;
    });
    try {
      const response = await fetch("/admin/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({ settings: values }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(errorMessage(payload, "Settings could not be saved."));
      showToast("Settings saved", payload.message || "The model configuration was updated.");
      settingsForm.querySelectorAll(".setting-label em").forEach((badge) => badge.textContent = "Override");
    } catch (error) {
      showToast("Settings failed", error.message || "Unknown server error", "error");
    } finally {
      submitButtons.forEach((button) => button.disabled = false);
    }
  });

  const resetButton = document.querySelector("[data-settings-reset]");
  resetButton?.addEventListener("click", async () => {
    const confirmation = resetButton.dataset.confirm;
    if (confirmation && !window.confirm(confirmation)) return;
    resetButton.disabled = true;
    try {
      const response = await fetch("/admin/settings/reset", {
        method: "POST",
        headers: { "Accept": "application/json" },
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(errorMessage(payload, "Settings could not be reset."));
      showToast("Overrides reset", payload.message || "Deployment values restored.");
      window.setTimeout(() => window.location.reload(), 900);
    } catch (error) {
      showToast("Reset failed", error.message || "Unknown server error", "error");
      resetButton.disabled = false;
    }
  });

  async function pollRefreshState() {
    if (body.dataset.page !== "admin") return;
    try {
      const response = await fetch("/admin/actions/status", { headers: { "Accept": "application/json" } });
      if (!response.ok) return;
      const state = await response.json();
      if (state.running) {
        setAdminBusy(true, "Refresh running", state.started_at ? `Started ${new Date(state.started_at).toLocaleTimeString()}` : "Server operation in progress");
      }
    } catch (_) {
      // Status polling is supplemental; do not interrupt the page on failure.
    }
  }

  pollRefreshState();
  if (body.dataset.page === "admin") window.setInterval(pollRefreshState, 5000);
})();
