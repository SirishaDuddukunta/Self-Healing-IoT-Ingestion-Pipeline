import numpy as np
from abc import ABC, abstractmethod
from models import TelemetryData
from typing import Dict, Any, Tuple

class PipelinePlugin(ABC):
    @abstractmethod
    async def process(self, data: TelemetryData, context: Dict[str, Any]) -> Tuple[TelemetryData, float, str]:
        """
        Returns: (modified_data, penalty_score, log_entry)
        """
        pass

class AnomalyDetectionPlugin(PipelinePlugin):
    def __init__(self, threshold=3.0):
        self.threshold = threshold
        # Simulated historical norms for the sensor
        self.history = {"temp_sensor_01": [20.1, 20.2, 19.8, 20.5, 20.0]}

    async def process(self, data: TelemetryData, context: Dict[str, Any]):
        vals = self.history.get(data.sensor_id, [])
        if len(vals) < 2:
            return data, 0.0, "Insufficient history for z-score analysis"

        mu, sigma = np.mean(vals), np.std(vals)
        z_score = abs((data.value - mu) / sigma) if sigma > 0 else 0

        if z_score > self.threshold:
            context["is_anomaly"] = True
            return data, 0.4, f"Anomaly flagged: Z-Score {z_score:.2f} exceeds threshold {self.threshold}"
        
        return data, 0.0, "Value within statistical range"

class ImputationPlugin(PipelinePlugin):
    async def process(self, data: TelemetryData, context: Dict[str, Any]):
        if context.get("is_anomaly"):
            # Simple regression/mean imputation
            original_val = data.value
            healed_val = 20.12  # Logic: replace with historical mean
            data.value = healed_val
            return data, 0.2, f"Self-healed: Value {original_val} imputed to {healed_val}"
        
        return data, 0.0, "No imputation necessary"