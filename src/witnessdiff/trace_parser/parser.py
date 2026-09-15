from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from witnessdiff.models import REFERENCE_TRACE_SCHEMA, ReferenceTrace


def parse_reference_trace(raw: Any) -> ReferenceTrace:
    if not isinstance(raw, dict):
        raise ValueError("reference trace must be a JSON object")
    if raw.get("schema") != REFERENCE_TRACE_SCHEMA:
        raise ValueError(f"unsupported schema: {raw.get('schema')!r}")
    return ReferenceTrace.model_validate(raw)


def load_reference_trace(path: Path | str) -> ReferenceTrace:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_reference_trace(data)
