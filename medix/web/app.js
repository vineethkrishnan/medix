const $ = (id) => document.getElementById(id);
const api = {
  async get(url) {
    const response = await fetch(url);
    return response.json();
  },
  async post(url, body) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return response.json();
  },
};

const state = {
  files: [],
  root: "",
  isDir: false,
  formats: null,
  lastOutputDir: "",
  historyWindow: "7d",
};

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function fmtDuration(seconds) {
  if (!seconds || seconds <= 0) return "--:--";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const pad = (n) => String(n).padStart(2, "0");
  return h ? `${pad(h)}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;
}

function fmtSize(bytes) {
  if (!bytes || bytes <= 0) return "N/A";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(1)} ${units[unit]}`;
}

function fillSelect(select, options, selected) {
  select.innerHTML = "";
  for (const [key, label] of Object.entries(options)) {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = label.split(" — ")[0] === label ? label : label;
    if (key === selected) option.selected = true;
    select.appendChild(option);
  }
}

// ───────────────────────────── init

async function init() {
  const prereq = await api.get("/api/prereq");
  if (!prereq.ready) {
    $("prereq").hidden = false;
    const hasMissing = prereq.missing && prereq.missing.length;
    $("prereq-title").textContent = hasMissing
      ? "FFmpeg not found."
      : "FFmpeg is broken.";
    const detail = hasMissing
      ? ` Missing: ${prereq.missing.join(", ")}.`
      : prereq.broken && prereq.broken.length
        ? ` Broken: ${prereq.broken.join(", ")}.`
        : "";
    $("prereq-hint").textContent = `${detail} ${prereq.hint || ""}`.trim();
  }

  state.formats = await api.get("/api/formats");
  const { output_formats } = state.formats;
  const formatSelect = $("output-format");
  formatSelect.innerHTML = "";
  for (const [name, def] of Object.entries(output_formats)) {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = `${name} — ${def.description}`;
    formatSelect.appendChild(option);
  }
  applyFormatDefaults();

  fillSelect($("video-codec"), state.formats.video_codecs, "libx264");
  fillSelect($("audio-codec"), state.formats.audio_codecs, "aac");
  fillSelect($("resolution"), state.formats.resolutions, "original");
  fillSelect($("frame-rate"), state.formats.frame_rates, "original");
  fillSelect($("preset"), state.formats.presets, "medium");
  fillSelect($("audio-bitrate"), state.formats.audio_bitrates, "auto");

  bindEvents();
  loadHistory();
}

function applyFormatDefaults() {
  const def = state.formats.output_formats[$("output-format").value];
  if (!def) return;
  if ($("video-codec").options.length) $("video-codec").value = def.default_vcodec;
  if ($("audio-codec").options.length) $("audio-codec").value = def.default_acodec;
}

// ───────────────────────────── events

function bindEvents() {
  $("theme-toggle").addEventListener("click", () => {
    const root = document.documentElement;
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
  });

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
  });

  $("pick-file").addEventListener("click", () => pick("file", "path-input"));
  $("pick-dir").addEventListener("click", () => pick("dir", "path-input"));
  $("pick-output").addEventListener("click", () => pick("dir", "output-dir"));
  $("scan-btn").addEventListener("click", scan);
  $("select-all").addEventListener("change", (event) => {
    document
      .querySelectorAll("#files-table tbody input[type=checkbox]")
      .forEach((box) => (box.checked = event.target.checked));
  });

  $("output-format").addEventListener("change", applyFormatDefaults);
  $("advanced-toggle").addEventListener("change", (event) => {
    $("advanced").hidden = !event.target.checked;
  });
  $("crf").addEventListener("input", (event) => {
    $("crf-value").textContent = event.target.value;
  });

  $("convert-btn").addEventListener("click", convert);

  document.querySelectorAll("#window-chips .chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document
        .querySelectorAll("#window-chips .chip")
        .forEach((other) => other.classList.remove("active"));
      chip.classList.add("active");
      state.historyWindow = chip.dataset.window;
      loadHistory();
    });
  });
}

function switchTab(name) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === name);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `tab-${name}`);
  });
  if (name === "history") loadHistory();
}

async function pick(mode, targetId) {
  const result = await api.post("/api/pick", { mode });
  if (result.path) $(targetId).value = result.path;
}

// ───────────────────────────── scan

async function scan() {
  const path = $("path-input").value.trim();
  if (!path) {
    $("scan-status").textContent = "Enter or pick a path first.";
    return;
  }
  $("scan-status").textContent = "Scanning…";
  const result = await api.post("/api/scan", {
    path,
    recursive: $("recursive").checked,
  });

  if (result.error) {
    $("scan-status").textContent = result.error;
    $("files-card").hidden = true;
    $("settings-card").hidden = true;
    return;
  }

  state.files = result.files;
  state.root = result.root;
  state.isDir = result.is_dir;
  $("output-dir").value = result.default_output;

  if (!result.files.length) {
    $("scan-status").textContent = "No media files found.";
    $("files-card").hidden = true;
    $("settings-card").hidden = true;
    return;
  }

  $("scan-status").textContent = `Found ${result.files.length} file(s).`;
  renderFiles();
  $("files-card").hidden = false;
  $("settings-card").hidden = false;
}

function renderFiles() {
  const tbody = $("files-table").querySelector("tbody");
  tbody.innerHTML = "";
  state.files.forEach((file, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><input type="checkbox" data-index="${index}" checked /></td>
      <td>${escapeHtml(file.name)}</td>
      <td>${escapeHtml(file.type)}</td>
      <td>${escapeHtml(file.resolution)}</td>
      <td class="mono">${fmtDuration(file.duration)}</td>
      <td class="mono">${fmtSize(file.size)}</td>`;
    tbody.appendChild(row);
  });
}

function selectedFiles() {
  const boxes = document.querySelectorAll(
    "#files-table tbody input[type=checkbox]:checked"
  );
  return Array.from(boxes).map((box) => state.files[Number(box.dataset.index)].path);
}

// ───────────────────────────── convert

async function convert() {
  const files = selectedFiles();
  if (!files.length) {
    $("scan-status").textContent = "Select at least one file.";
    return;
  }

  const settings = {
    output_format: $("output-format").value,
    video_codec: $("video-codec").value,
    audio_codec: $("audio-codec").value,
    resolution: $("resolution").value,
    frame_rate: $("frame-rate").value,
    preset: $("preset").value,
    crf: Number($("crf").value),
    audio_bitrate: $("audio-bitrate").value,
  };

  $("convert-btn").disabled = true;
  $("result-card").hidden = true;
  $("progress-card").hidden = false;
  $("progress-list").innerHTML = "";

  const result = await api.post("/api/convert", {
    files,
    settings,
    input_root: state.root,
    recursive: $("recursive").checked,
    output_dir: $("output-dir").value.trim(),
  });

  if (result.error) {
    $("scan-status").textContent = result.error;
    $("convert-btn").disabled = false;
    return;
  }

  streamProgress(result.job_id);
}

function streamProgress(jobId) {
  const source = new EventSource(`/api/progress?job=${jobId}`);
  source.onmessage = (event) => {
    const snapshot = JSON.parse(event.data);
    renderProgress(snapshot);
    if (snapshot.done) {
      source.close();
      $("convert-btn").disabled = false;
      showResult(snapshot.summary);
      loadHistory();
    }
  };
  source.onerror = () => {
    source.close();
    $("convert-btn").disabled = false;
  };
}

function renderProgress(snapshot) {
  const overall = Math.round(snapshot.overall * 100);
  $("overall-pct").textContent = `${overall}%`;
  $("overall-bar").style.width = `${overall}%`;

  const list = $("progress-list");
  snapshot.files.forEach((file, index) => {
    let row = list.querySelector(`[data-prog="${index}"]`);
    if (!row) {
      row = document.createElement("div");
      row.className = "prog-row";
      row.dataset.prog = String(index);
      row.innerHTML = `
        <div class="row-between">
          <span class="prog-name"></span>
          <span class="chip-status"></span>
        </div>
        <div class="progress-track"><div class="progress-fill"></div></div>`;
      list.appendChild(row);
    }
    const pct = Math.round(file.pct * 100);
    row.querySelector(".prog-name").textContent = file.name;
    const chip = row.querySelector(".chip-status");
    chip.textContent = file.status;
    chip.className = `chip-status ${file.status}`;
    const fill = row.querySelector(".progress-fill");
    fill.style.width = `${pct}%`;
    fill.className = `progress-fill ${file.status === "done" ? "done" : ""}${
      file.status === "failed" ? "failed" : ""
    }`;
  });
}

function showResult(summary) {
  if (!summary) return;
  state.lastOutputDir = summary.output_dir;
  const failed = summary.failed;
  $("result-title").textContent = failed ? "Completed with errors" : "Complete";
  $("result-summary").textContent = failed
    ? `${summary.succeeded} succeeded, ${failed} failed. Output: ${summary.output_dir}`
    : `All ${summary.succeeded} file(s) converted. Output: ${summary.output_dir}`;
  $("result-card").hidden = false;
}

$("open-output").addEventListener("click", () => {
  if (state.lastOutputDir) api.post("/api/open", { path: state.lastOutputDir });
});

// ───────────────────────────── history

async function loadHistory() {
  const result = await api.get(`/api/history?since=${state.historyWindow}`);
  const list = $("history-list");
  list.innerHTML = "";

  if (!result.records.length) {
    list.innerHTML = '<p class="empty">No conversions in this window.</p>';
    return;
  }

  result.records.forEach((record) => {
    const when = new Date(record.timestamp * 1000).toLocaleString();
    const item = document.createElement("div");
    item.className = `history-item ${record.status === "failed" ? "failed" : ""}`;
    item.innerHTML = `
      <div>
        <div class="history-name">${escapeHtml(record.input_name)} → ${escapeHtml(
      record.output_format
    )}</div>
        <div class="history-meta">${escapeHtml(when)} · ${fmtSize(
      record.input_size
    )} → ${fmtSize(record.output_size)} · ${record.elapsed.toFixed(
      1
    )}s</div>
      </div>
      <span class="chip-status ${record.status === "failed" ? "failed" : "done"}">${escapeHtml(
      record.status
    )}</span>`;
    list.appendChild(item);
  });
}

init();
