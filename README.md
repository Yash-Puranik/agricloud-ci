# AgriCloud-CI

An automated, edge-to-cloud precision agriculture monitoring and decision support platform. AgriCloud-CI fuses ground-level volumetric soil moisture measurements from physical edge microcontrollers with real-time atmospheric data sourced from satellite weather APIs, evaluating microclimate suitability against calibrated agronomic physiological envelopes.

The system features a decoupled microservice architecture, dual-tier persistence with automated SQLite failover for zero-downtime data logging, containerized deployment configurations, and automated continuous integration workflows.

**Live Deployment:** <https://your-deployment-url.vercel.app>

---

## Architecture Overview

The platform processes and evaluates environmental metrics across five distinct tiers:

1. **Edge Acquisition:** Physical ESP32 nodes sample capacitive analog soil moisture probes via 12-bit ADC channels and dispatch periodic JSON payloads over HTTP.
2. **Ingestion Gateway & Atmospheric Fusion:** A Python REST backend validates payload physical ranges (-10°C to 60°C, 0% to 100% RH). When edge hardware transmits without ambient sensors, the gateway fetches local ambient temperature and relative humidity from the Open-Meteo REST service to construct a complete environmental profile.
3. **Agronomic Decision Engine:** A rule-based evaluation matrix assesses target crop bounds for Wheat, Cotton, and Soybeans, classifying viability into Optimal, Marginal, or Unsuitable statuses with actionable physiological advisories.
4. **Dual-Tier Fault-Tolerant Persistence:** Records are primarily committed to a PostgreSQL relational database. If the upstream database service is unreachable, writes immediately route to an embedded SQLite store (`agricloud.db`) without interrupting ingestion or failing client requests.
5. **Presentation Gateway:** A responsive web interface styled with Tailwind CSS provides live metric streaming, manual stress testing, and real-time historical audit logs.

---

## Repository Tree

```
agricloud-ci/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── backend/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_decision_matrix.py
│   │   ├── test_meteo_client.py
│   │   └── test_telemetry_payload.py
│   ├── app.py
│   ├── config.py
│   ├── db_service.py
│   ├── decision_matrix.py
│   ├── Dockerfile
│   ├── meteo_client.py
│   └── requirements.txt
├── db/
│   └── init.sql
├── firmware/
│   └── esp32_firmware/
│       └── esp32_firmware.ino
├── frontend/
│   ├── src/
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── style.css
│   │   │   └── js/
│   │   │       └── dashboard.js
│   │   ├── advisory.html
│   │   ├── history.html
│   │   └── index.html
│   ├── Dockerfile
│   └── nginx.conf
├── scripts/
│   └── run_checks.sh
├── .dockerignore
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Technical Specifications

| Subsystem | Technology Stack | Core Function |
| :--- | :--- | :--- |
| **Edge Hardware** | ESP32, C++ (Arduino Core) | 12-bit ADC multi-sampling, linear sensor calibration, Wi-Fi JSON dispatch |
| **Backend Core** | Python 3.11, Flask | Ingestion routing, weather service integration, data validation |
| **Decision Intelligence** | Python | Agronomic boundary matching, multi-variable compound stress detection |
| **Primary Persistence** | PostgreSQL 16 | Relational persistence with indexed chronological telemetry queries |
| **Failover Persistence** | SQLite 3 | Automated file-based disk fallback during upstream database outages |
| **Web Gateway & UI** | Nginx, HTML5, Tailwind CSS, JS | Static asset delivery, reverse proxying, asynchronous client polling |
| **Automation & Quality** | GitHub Actions, Pytest, Flake8 | Pre-commit validation, boundary test verification, release deployment |

---

## Agronomic Evaluation Envelopes

The evaluation matrix applies deterministic boundaries across supported crop varieties:

| Crop Variety | Nominal Temp (°C) | Nominal Humidity (%) | Nominal Soil Moisture (%) | Physiological Stress Thresholds |
| :--- | :--- | :--- | :--- | :--- |
| **Wheat** | 12.0 – 25.0 | 40.0 – 75.0 | 35.0 – 65.0 | Thermal stress $\ge$ 32°C; Chill injury $\le$ 4°C; Wilting point $\le$ 20%; Hypoxia $\ge$ 80% |
| **Cotton** | 21.0 – 35.0 | 50.0 – 85.0 | 40.0 – 70.0 | Heat stress $\ge$ 40°C; Growth retardation $\le$ 15°C; Wilting point $\le$ 25%; Waterlogging $\ge$ 85% |
| **Soybeans** | 20.0 – 30.0 | 55.0 – 80.0 | 45.0 – 75.0 | Flower abortion $\ge$ 36°C; Germination halt $\le$ 10°C; Wilting point $\le$ 25%; Root rot risk $\ge$ 85% |

- **Optimal:** All measured parameters reside strictly within nominal bounds.
- **Marginal:** Exactly one metric exhibits moderate deviation outside nominal bounds without breaching critical limits.
- **Unsuitable:** Multiple metrics deviate simultaneously, or any single metric breaches a critical physiological limit.

---

## API Interface Specification

### 1. Ingestion Service
- **Endpoint:** `POST /api/telemetry`
- **Description:** Ingests raw sensor readings from edge devices or testing interfaces. If ambient air temperature or humidity are omitted, the service triggers satellite weather fallback.
- **Parameters:** `node_id` (string), `soil_moisture` (float, required), `temperature` (float, optional), `humidity` (float, optional), `crop` (string).
- **Result:** Agronomic verdict, active violation list, advisory message, and provenance metadata.

### 2. Historical Audit Service
- **Endpoint:** `GET /api/history`
- **Description:** Retrieves chronological telemetry records from the active persistence tier.
- **Parameters:** `limit` (integer, default 20).
- **Result:** Formatted list of historical evaluations with timestamps, node identifiers, metric values, verdicts, and fallback flags.

### 3. Service Health
- **Endpoint:** `GET /health`
- **Description:** Readiness and liveness endpoint used by orchestration probes and automated monitors.
- **Result:** Service operational status and HTTP 200 response.

---

## Deployment & Execution

### Local Environment Setup
1. Configure a local Python 3.11 virtual environment.
2. Install application dependencies from `backend/requirements.txt`.
3. Execute validation scripts via `scripts/run_checks.sh` to confirm environment readiness and pass the test suite.
4. Launch the application entrypoint `backend/app.py`. The service will automatically manage persistence, utilizing the local SQLite fallback if PostgreSQL is not active.

### Container Orchestration
The platform includes container definitions supporting isolated multi-container runtime:
- **`db`:** PostgreSQL 16 initialized using volume-mounted schema scripts (`db/init.sql`).
- **`backend`:** Hardened multi-stage Python runtime running under an unprivileged system user with integrated health checking.
- **`frontend`:** Unprivileged Nginx gateway serving static assets and routing `/api/` traffic to the backend service.

---

## Continuous Integration & Deployment Pipeline

The workflow maintains continuous quality through two independent pipelines:

- **`ci.yml` (Continuous Integration):**
  - Triggers on all pushes and pull requests across all repository branches.
  - Enforces PEP 8 syntax standards via Flake8, scans codebase for inadvertent secret commitments, and executes unit and integration tests via Pytest.
- **`deploy.yml` (Continuous Deployment):**
  - Triggers exclusively on pushes to the `main` branch following successful CI validation.
  - Packages and releases updated platform artifacts to the production cloud infrastructure.

---

## License

This project is licensed under the MIT License.