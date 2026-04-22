from fastapi import FastAPI, BackgroundTasks, HTTPException
from models import TelemetryData, IngestionResponse
from plugins import AnomalyDetectionPlugin, ImputationPlugin
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelEngine")

app = FastAPI(title="Sentinel: Self-Healing Ingestion Pipeline")

# Plugin Registration
PIPELINE = [
    AnomalyDetectionPlugin(),
    ImputationPlugin()
]

def log_to_review_queue(data: TelemetryData, score: float, logs: list):
    """Background task for manual audit when confidence is low."""
    logger.warning(f"🚨 [REVIEW] Score: {score} | Sensor: {data.sensor_id} | Logs: {logs}")

@app.post("/ingest", response_model=IngestionResponse)
async def ingest_telemetry(payload: TelemetryData, background_tasks: BackgroundTasks):
    current_data = payload
    confidence = 1.0
    processing_logs = []
    context = {}

    try:
        # Process through modular plugins
        for plugin in PIPELINE:
            current_data, penalty, log = await plugin.process(current_data, context)
            confidence -= penalty
            processing_logs.append(log)

        final_score = round(max(0.0, confidence), 2)
        status = "accepted"

        # The Twist: Confidence Scoring & Routing
        if final_score < 0.7:
            status = "flagged_for_review"
            background_tasks.add_task(log_to_review_queue, current_data, final_score, processing_logs)

        return {
            "status": status,
            "confidence_score": final_score,
            "data": current_data,
            "logs": processing_logs
        }

    except Exception as e:
        logger.error(f"Ingestion Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error")