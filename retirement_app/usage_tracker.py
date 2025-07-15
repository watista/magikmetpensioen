import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger("retirement_app")

COUNTER_FILE = Path(__file__).resolve().parent / "../usage_stats.json"

def increment_usage(birthdate: str) -> None:
    try:
        # Create file if missing
        if not COUNTER_FILE.exists():
            COUNTER_FILE.write_text(json.dumps({"count": 0, "birthdates": []}, indent=2))

        # Load safely
        with COUNTER_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        data["count"] = data.get("count", 0) + 1
        data.setdefault("birthdates", []).append({
            "date": birthdate,
            "timestamp": datetime.now().isoformat(timespec="seconds")
        })

        with COUNTER_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        logger.warning(f"Usage tracking failed: {e}")
