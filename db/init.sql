CREATE TABLE IF NOT EXISTS agri_telemetry_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    node_id VARCHAR(32) NOT NULL DEFAULT 'ESP32-NODE-01',
    temperature NUMERIC(5, 2) NOT NULL,
    humidity NUMERIC(5, 2) NOT NULL,
    soil_moisture NUMERIC(5, 2) NOT NULL,
    crop_queried VARCHAR(32) NOT NULL,
    suitability_verdict VARCHAR(16) NOT NULL,
    advisory_text TEXT NOT NULL,
    is_satellite_fallback BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON agri_telemetry_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_crop ON agri_telemetry_logs (crop_queried);
CREATE INDEX IF NOT EXISTS idx_telemetry_node_id ON agri_telemetry_logs (node_id);

INSERT INTO agri_telemetry_logs 
(node_id, temperature, humidity, soil_moisture, crop_queried, suitability_verdict, advisory_text, is_satellite_fallback)
VALUES 
('SYSTEM-INIT', 24.50, 60.00, 52.00, 'Wheat', 'Optimal', 'System database initialization verification record.', FALSE);