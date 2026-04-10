from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
import os
import time
from typing import Any, Callable

from ai_config import get_mode_display_name, normalize_analysis_mode

try:
    import psutil
except ImportError:
    psutil = None

try:
    from codecarbon import OfflineEmissionsTracker
except ImportError:
    OfflineEmissionsTracker = None


# Default offline region for local energy estimates
DEFAULT_COUNTRY_ISO_CODE = "FIN"


# Basic input-size helper used across the run summary
def count_words(text: str) -> int:
    if not isinstance(text, str) or not text.strip():
        return 0
    return len(text.split())


# Keep numeric output compact and stable in saved metrics
def _round_if_number(value: Any, digits: int = 6):
    if isinstance(value, (int, float)) and math.isfinite(value):
        return round(float(value), digits)
    return value


# Store timestamps in a consistent machine-readable format
def _as_iso_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


# Collect lightweight process stats for the current Python run
def _get_process_stats() -> tuple[float | None, float | None, int | None]:
    if psutil is None:
        return None, None, None

    process = psutil.Process(os.getpid())
    cpu_times = process.cpu_times()
    cpu_seconds = float(getattr(cpu_times, "user", 0.0) + getattr(cpu_times, "system", 0.0))
    rss_bytes = None
    try:
        rss_bytes = int(process.memory_info().rss)
    except Exception:
        rss_bytes = None
    try:
        cpu_count = psutil.cpu_count(logical=True) or 1
    except Exception:
        cpu_count = None
    return cpu_seconds, rss_bytes, cpu_count


# Coerce different possible Gemini/EcoLogits metric formats into a single number or None
def _coerce_range_value(value: Any):
    if value is None:
        return None

    for attr in ("mean", "value"):
        candidate = getattr(value, attr, None)
        if isinstance(candidate, (int, float)) and math.isfinite(candidate):
            return float(candidate)

    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)

    minimum = getattr(value, "min", None)
    maximum = getattr(value, "max", None)
    if isinstance(minimum, (int, float)) and isinstance(maximum, (int, float)):
        return float(minimum + maximum) / 2.0

    return None


# Convert library warning/error objects into simple text lists
def _collect_status_messages(messages: Any) -> list[str]:
    if not messages:
        return []

    collected = []
    for message in messages:
        text = getattr(message, "message", None)
        if isinstance(text, str) and text.strip():
            collected.append(text.strip())
        elif isinstance(message, str) and message.strip():
            collected.append(message.strip())
    return collected


# Normalize token metadata from Gemini responses into one shape
def build_token_usage(usage_metadata: Any) -> dict[str, int | None]:
    if usage_metadata is None:
        return {
            "prompt_tokens": None,
            "output_tokens": None,
            "thought_tokens": None,
            "total_tokens": None,
        }

    prompt_tokens = getattr(usage_metadata, "prompt_token_count", None)
    candidates_tokens = getattr(usage_metadata, "candidates_token_count", None)
    thoughts_tokens = getattr(usage_metadata, "thoughts_token_count", None)
    total_tokens = getattr(usage_metadata, "total_token_count", None)

    output_tokens = None
    if isinstance(candidates_tokens, int) or isinstance(thoughts_tokens, int):
        output_tokens = int(candidates_tokens or 0) + int(thoughts_tokens or 0)

    return {
        "prompt_tokens": prompt_tokens if isinstance(prompt_tokens, int) else None,
        "output_tokens": output_tokens,
        "thought_tokens": thoughts_tokens if isinstance(thoughts_tokens, int) else None,
        "total_tokens": total_tokens if isinstance(total_tokens, int) else None,
    }


# Read EcoLogits output into the app's simplified sustainability schema
def extract_ecologits_metrics(impacts: Any) -> dict[str, Any]:
    if impacts is None:
        return {
            "energy_kwh": None,
            "co2e_kg": None,
            "estimate_status": "unavailable",
            "estimation_source": "ecologits",
            "warnings": [],
            "errors": [],
        }

    energy_kwh = _coerce_range_value(getattr(getattr(impacts, "energy", None), "value", None))
    co2e_kg = _coerce_range_value(getattr(getattr(impacts, "gwp", None), "value", None))
    warnings = _collect_status_messages(getattr(impacts, "warnings", None))
    errors = _collect_status_messages(getattr(impacts, "errors", None))

    if energy_kwh is not None and co2e_kg is not None:
        estimate_status = "complete"
    elif energy_kwh is not None or co2e_kg is not None:
        estimate_status = "partial"
    else:
        estimate_status = "unavailable"

    return {
        "energy_kwh": _round_if_number(energy_kwh),
        "co2e_kg": _round_if_number(co2e_kg),
        "estimate_status": estimate_status,
        "estimation_source": "ecologits",
        "warnings": warnings,
        "errors": errors,
    }


# Wrap local analysis so CodeCarbon can estimate energy and emissions for that task
def run_with_codecarbon_tracking(
    operation: Callable[[], Any],
    *,
    task_name: str = "berts_analysis",
    country_iso_code: str = DEFAULT_COUNTRY_ISO_CODE,
):
    if OfflineEmissionsTracker is None:
        return operation(), {
            "energy_kwh": None,
            "co2e_kg": None,
            "estimate_status": "unavailable",
            "estimation_source": "codecarbon",
            "warnings": ["CodeCarbon is not installed."],
            "errors": [],
        }

    tracker = None
    tracking_error = None
    try:
        tracker = OfflineEmissionsTracker(
            country_iso_code=country_iso_code,
            save_to_file=False,
            log_level="error",
        )
        tracker.start()
        tracker.start_task(task_name)
    except Exception as exc:
        tracking_error = exc

    result = operation()

    if tracking_error is not None or tracker is None:
        return result, {
            "energy_kwh": None,
            "co2e_kg": None,
            "estimate_status": "unavailable",
            "estimation_source": "codecarbon",
            "warnings": [],
            "errors": [f"CodeCarbon tracking unavailable: {tracking_error}"],
        }

    try:
        task_data = tracker.stop_task(task_name)
        return result, extract_codecarbon_metrics(task_data)
    except Exception as exc:
        return result, {
            "energy_kwh": None,
            "co2e_kg": None,
            "estimate_status": "unavailable",
            "estimation_source": "codecarbon",
            "warnings": [],
            "errors": [f"CodeCarbon tracking unavailable: {exc}"],
        }
    finally:
        if tracker is not None:
            try:
                tracker.stop()
            except Exception:
                pass


# Convert CodeCarbon task output into the same simplified schema
def extract_codecarbon_metrics(task_data: Any) -> dict[str, Any]:
    if task_data is None:
        return {
            "energy_kwh": None,
            "co2e_kg": None,
            "estimate_status": "unavailable",
            "estimation_source": "codecarbon",
            "warnings": ["CodeCarbon did not return task-level data."],
            "errors": [],
        }

    cpu_energy = getattr(task_data, "cpu_energy", None)
    gpu_energy = getattr(task_data, "gpu_energy", None)
    ram_energy = getattr(task_data, "ram_energy", None)
    total_energy = None
    energy_values = [value for value in (cpu_energy, gpu_energy, ram_energy) if isinstance(value, (int, float))]
    if energy_values:
        total_energy = float(sum(energy_values))

    co2e_kg = getattr(task_data, "emissions", None)
    duration = getattr(task_data, "duration", None)

    if isinstance(total_energy, (int, float)) and isinstance(co2e_kg, (int, float)):
        estimate_status = "complete"
    elif isinstance(total_energy, (int, float)) or isinstance(co2e_kg, (int, float)):
        estimate_status = "partial"
    else:
        estimate_status = "unavailable"

    return {
        "energy_kwh": _round_if_number(total_energy),
        "co2e_kg": _round_if_number(co2e_kg),
        "duration_seconds": _round_if_number(duration, digits=3),
        "estimate_status": estimate_status,
        "estimation_source": "codecarbon",
        "warnings": [],
        "errors": [],
    }

@dataclass
class SustainabilityRunTracker:
    filepath: str
    text: str

    # Tracks sustainability metrics for a single analysis run, including local resource usage and any provided energy/emission estimates
    def __post_init__(self):
        self._started_at = time.time()
        self._start_perf_counter = time.perf_counter()
        self._start_cpu_seconds, self._start_rss_bytes, self._cpu_count = _get_process_stats()

    # Build the final metrics object and merge in estimator-specific values
    def finalize(self, *, mode: str, extra_metrics: dict[str, Any] | None = None) -> dict[str, Any]:
        ended_at = time.time()
        runtime_seconds = time.perf_counter() - self._start_perf_counter
        end_cpu_seconds, end_rss_bytes, _ = _get_process_stats()

        cpu_percent_avg = None
        if (
            isinstance(self._start_cpu_seconds, (int, float))
            and isinstance(end_cpu_seconds, (int, float))
            and runtime_seconds > 0
        ):
            cpu_delta_seconds = max(0.0, end_cpu_seconds - self._start_cpu_seconds)
            cpu_percent_avg = (cpu_delta_seconds / runtime_seconds) * 100.0
            if isinstance(self._cpu_count, int) and self._cpu_count > 0:
                cpu_percent_avg /= self._cpu_count

        ram_mb_avg = None
        if isinstance(self._start_rss_bytes, int) and isinstance(end_rss_bytes, int):
            ram_mb_avg = ((self._start_rss_bytes + end_rss_bytes) / 2.0) / (1024 * 1024)

        word_count = count_words(self.text)
        char_count = len(self.text) if isinstance(self.text, str) else 0

        metrics = {
            "method": get_mode_display_name(mode),
            "mode": normalize_analysis_mode(mode),
            "document_count": 1,
            "source_file": self.filepath,
            "input_chars": char_count,
            "input_words": word_count,
            "runtime_seconds": _round_if_number(runtime_seconds, digits=3),
            "cpu_percent_avg": _round_if_number(cpu_percent_avg, digits=3),
            "ram_mb_avg": _round_if_number(ram_mb_avg, digits=3),
            "started_at": _as_iso_timestamp(self._started_at),
            "ended_at": _as_iso_timestamp(ended_at),
            "estimate_status": "unavailable",
            "estimation_source": "baseline",
            "energy_kwh": None,
            "co2e_kg": None,
            "warnings": [],
            "errors": [],
            "is_estimate": True,
        }

        if isinstance(extra_metrics, dict):
            warnings = list(metrics["warnings"])
            warnings.extend(extra_metrics.get("warnings", []))
            errors = list(metrics["errors"])
            errors.extend(extra_metrics.get("errors", []))
            metrics.update(extra_metrics)
            metrics["warnings"] = warnings
            metrics["errors"] = errors

        return metrics


# Shared number formatting for the UI text block
def _format_number(value: Any, digits: int = 3, suffix: str = "") -> str:
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return "Unavailable"
    return f"{value:.{digits}f}{suffix}"


# Keep energy in one fixed unit so runs stay easy to compare
def _format_energy(value_kwh: Any) -> str:
    if not isinstance(value_kwh, (int, float)) or not math.isfinite(value_kwh):
        return "Unavailable"
    return f"{value_kwh:.6f} kWh"


# Use friendlier emission units for very small values
def _format_emissions(value_kg: Any) -> str:
    if not isinstance(value_kg, (int, float)) or not math.isfinite(value_kg):
        return "Unavailable"
    if value_kg >= 1:
        return f"{value_kg:.2f} kg CO2e"

    value_g = value_kg * 1000.0
    if value_g >= 1:
        return f"{value_g:.2f} g CO2e"

    value_mg = value_g * 1000.0
    return f"{value_mg:.2f} mg CO2e"


# Collapse resource stats into one short UI line
def _format_resource_usage(metrics: dict[str, Any]) -> str:
    cpu_text = _format_number(metrics.get("cpu_percent_avg"), digits=1, suffix="%")
    ram_text = _format_number(metrics.get("ram_mb_avg"), digits=1, suffix=" MB")
    return f"Usage: CPU {cpu_text}, RAM {ram_text}"


# Readability helper
def format_sustainability_for_ui(metrics: dict[str, Any] | None) -> str:
    if not isinstance(metrics, dict) or not metrics:
        return "Sustainability metrics are unavailable for this analysis run."

    lines = [
        "Sustainability Metrics",
        "",
        f"Method: {metrics.get('method', 'Unavailable')}",
        (
            "Input size: "
            f"{metrics.get('input_words', 'Unavailable')} words"
        ),
        f"Runtime: {_format_number(metrics.get('runtime_seconds'), digits=1, suffix=' s')}",
        _format_resource_usage(metrics),
        f"Estimated energy: {_format_energy(metrics.get('energy_kwh'))}",
        f"Estimated emissions: {_format_emissions(metrics.get('co2e_kg'))}",
    ]

    warnings = metrics.get("warnings") or []
    errors = metrics.get("errors") or []
    if warnings and metrics.get("estimate_status") != "complete":
        lines.append(f"Notes: {'; '.join(warnings)}")
    if errors:
        lines.append(f"Estimate issues: {'; '.join(errors)}")

    return "\n".join(lines)