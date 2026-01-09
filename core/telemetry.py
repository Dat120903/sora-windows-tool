"""
Telemetry - Lightweight tracking for latency and error classes.
NO sensitive data logged.
"""
import time
from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict

@dataclass
class RequestMetrics:
    endpoint: str
    latency_ms: float
    success: bool
    error_class: str = ""  # e.g., "401", "429", "network", "timeout"

class Telemetry:
    """Simple telemetry for API monitoring."""
    
    def __init__(self):
        self.metrics: List[RequestMetrics] = []
        self.error_counts: Dict[str, int] = defaultdict(int)
        self._start_times: Dict[str, float] = {}

    def start_request(self, request_id: str):
        """Mark start of a request."""
        self._start_times[request_id] = time.time()

    def end_request(self, request_id: str, endpoint: str, 
                    success: bool, error_class: str = ""):
        """Record completed request."""
        start = self._start_times.pop(request_id, time.time())
        latency = (time.time() - start) * 1000  # ms
        
        metric = RequestMetrics(
            endpoint=endpoint,
            latency_ms=latency,
            success=success,
            error_class=error_class
        )
        self.metrics.append(metric)
        
        if not success:
            self.error_counts[error_class] += 1

    def get_stats(self) -> Dict:
        """Get summary statistics."""
        if not self.metrics:
            return {"total_requests": 0}
        
        latencies = [m.latency_ms for m in self.metrics]
        success_count = sum(1 for m in self.metrics if m.success)
        
        return {
            "total_requests": len(self.metrics),
            "success_rate": success_count / len(self.metrics),
            "avg_latency_ms": sum(latencies) / len(latencies),
            "max_latency_ms": max(latencies),
            "error_breakdown": dict(self.error_counts)
        }

    def clear(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.error_counts.clear()
        self._start_times.clear()

# Singleton
telemetry = Telemetry()
