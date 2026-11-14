document.addEventListener("DOMContentLoaded", () => {
    const API_BASE = "http://127.0.0.1:5000";

    const tempEl = document.getElementById("temp-val");
    const humEl = document.getElementById("humidity-val");
    const soilEl = document.getElementById("soil-val");
    const advEl = document.getElementById("quick-advisory");
    const verdictTag = document.getElementById("verdict-tag");
    const lastUpdated = document.getElementById("last-updated");
    const nodeStatus = document.getElementById("node-status");

    let simulatedSoil = Number(localStorage.getItem("agricloud_soil")) || 54.0;
    let lastKnownTemp = Number(localStorage.getItem("agricloud_temp")) || 26.0;
    let lastKnownHum = Number(localStorage.getItem("agricloud_hum")) || 60.0;

    function evaluateCropViability(temp, hum, soil, crop = "Wheat") {
        const rules = {
            Wheat:    { minSoil: 45, maxSoil: 65, minTemp: 12, maxTemp: 32, minHum: 35, maxHum: 80 },
            Cotton:   { minSoil: 40, maxSoil: 60, minTemp: 18, maxTemp: 38, minHum: 40, maxHum: 75 },
            Soybeans: { minSoil: 50, maxSoil: 70, minTemp: 15, maxTemp: 34, minHum: 45, maxHum: 85 },
            Rice:     { minSoil: 65, maxSoil: 85, minTemp: 20, maxTemp: 37, minHum: 60, maxHum: 90 },
            Maize:    { minSoil: 45, maxSoil: 65, minTemp: 16, maxTemp: 35, minHum: 40, maxHum: 80 }
        };
        const r = rules[crop] || rules.Wheat;

        if (soil < r.minSoil) {
            return {
                verdict: "Critical",
                badge: "bg-red-100 text-red-800",
                message: `Critical — Soil moisture (${soil.toFixed(1)}%) is below ${crop} threshold (${r.minSoil}%). Initiate irrigation immediately.`
            };
        }
        if (soil > r.maxSoil || temp > r.maxTemp || temp < r.minTemp) {
            return {
                verdict: "Marginal",
                badge: "bg-amber-100 text-amber-800",
                message: `Marginal — ${crop} experiencing thermal or moisture stress (${temp.toFixed(1)}°C, ${soil.toFixed(1)}% moisture). Monitor closely.`
            };
        }
        return {
            verdict: "Optimal",
            badge: "bg-emerald-100 text-emerald-800",
            message: `Optimal — Field conditions (${temp.toFixed(1)}°C, ${hum.toFixed(1)}% RH, ${soil.toFixed(1)}% soil) are ideal for ${crop}.`
        };
    }

    function appendAuditRecord(record) {
        const history = JSON.parse(localStorage.getItem("agricloud_history") || "[]");
        history.unshift(record);
        if (history.length > 30) history.pop();
        localStorage.setItem("agricloud_history", JSON.stringify(history));
    }

    async function pollTelemetry() {
        try {
            const response = await fetch(`${API_BASE}/api/telemetry/live`, { cache: "no-store" });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();

            lastKnownTemp = Number(data.temperature);
            lastKnownHum = Number(data.humidity);

            simulatedSoil -= (Math.random() * 0.7 + 0.5);
            if (simulatedSoil < 39.0) simulatedSoil = 58.0;

            const activeSoil = data.has_hardware ? Number(data.soil_moisture) : simulatedSoil;
            const activeCrop = data.crop || "Wheat";

            localStorage.setItem("agricloud_temp", lastKnownTemp);
            localStorage.setItem("agricloud_hum", lastKnownHum);
            localStorage.setItem("agricloud_soil", activeSoil);

            if (tempEl) tempEl.innerText = lastKnownTemp.toFixed(1);
            if (humEl) humEl.innerText = lastKnownHum.toFixed(1);
            if (soilEl) soilEl.innerText = activeSoil.toFixed(1);

            if (nodeStatus) {
                nodeStatus.innerText = "Online (ESP32-NODE-01)";
                nodeStatus.className = "text-emerald-600 font-semibold";
            }

            const viability = evaluateCropViability(lastKnownTemp, lastKnownHum, activeSoil, activeCrop);
            if (verdictTag) {
                verdictTag.innerText = viability.verdict;
                verdictTag.className = `ml-2 font-mono uppercase text-xs px-2 py-0.5 rounded ${viability.badge}`;
            }
            if (advEl) advEl.innerText = viability.message;
            if (lastUpdated) lastUpdated.innerText = "Updated: " + new Date().toLocaleTimeString();

            appendAuditRecord({
                id: Date.now().toString().slice(-4),
                timestamp: new Date().toISOString(),
                crop: activeCrop,
                soil_moisture: activeSoil,
                temperature: lastKnownTemp,
                humidity: lastKnownHum,
                verdict: viability.verdict
            });

        } catch (err) {
            console.error("Backend connection error:", err);
            if (nodeStatus) {
                nodeStatus.innerText = "Offline (Check Flask :5000)";
                nodeStatus.className = "text-red-600 font-semibold";
            }
        }
    }

    async function loadHistory() {
        const tbody = document.querySelector("tbody");
        if (!tbody) return;

        let records = JSON.parse(localStorage.getItem("agricloud_history") || "[]");

        try {
            const response = await fetch(`${API_BASE}/api/history`, { cache: "no-store" });
            if (response.ok) {
                const backendRecords = await response.json();
                if (Array.isArray(backendRecords) && backendRecords.length > 0 && records.length === 0) {
                    records = backendRecords;
                }
            }
        } catch (_) {}

        if (records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-slate-400">Awaiting telemetry packets...</td></tr>`;
            return;
        }

        tbody.innerHTML = records.map(r => `
            <tr class="border-b border-slate-200 hover:bg-slate-50">
                <td class="py-3 px-4 font-mono text-xs">#${r.id}</td>
                <td class="py-3 px-4 text-xs">${new Date(r.timestamp).toLocaleTimeString()}</td>
                <td class="py-3 px-4 font-medium">${r.crop || "Wheat"}</td>
                <td class="py-3 px-4 font-semibold text-emerald-700">${Number(r.soil_moisture).toFixed(1)}%</td>
                <td class="py-3 px-4">${Number(r.temperature).toFixed(1)} °C</td>
                <td class="py-3 px-4">${Number(r.humidity).toFixed(1)}%</td>
            </tr>
        `).join("");
    }

    // Bind Crop Viability evaluation on advisory.html regardless of exact button/select IDs
    const cropSelect = document.querySelector("select");
    const evalBtn = document.querySelector("button");
    const resultBox = document.getElementById("viability-result") || document.getElementById("advisory-output") || document.querySelector("[data-viability]");

    function runViabilityCheck(e) {
        if (e) e.preventDefault();
        const selectedCrop = cropSelect ? cropSelect.value : "Wheat";
        const res = evaluateCropViability(lastKnownTemp, lastKnownHum, simulatedSoil, selectedCrop);
        if (resultBox) {
            resultBox.innerText = res.message;
        } else if (cropSelect) {
            let autoBox = document.getElementById("auto-viability-box");
            if (!autoBox) {
                autoBox = document.createElement("div");
                autoBox.id = "auto-viability-box";
                autoBox.className = "mt-4 p-4 rounded-lg bg-blue-50 border-l-4 border-blue-600 text-sm text-blue-900 font-medium";
                cropSelect.parentElement.appendChild(autoBox);
            }
            autoBox.innerText = res.message;
        }
    }

    if (cropSelect) {
        cropSelect.addEventListener("change", runViabilityCheck);
        if (evalBtn) evalBtn.addEventListener("click", runViabilityCheck);
        runViabilityCheck();
    }

    if (tempEl) {
        pollTelemetry();
        setInterval(pollTelemetry, 5000);
    }
    if (document.querySelector("tbody") && window.location.pathname.includes("history")) {
        loadHistory();
        setInterval(loadHistory, 5000);
    }
});