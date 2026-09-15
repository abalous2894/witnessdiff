from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from witnessdiff.models import EVIDENCE_BUNDLE_SCHEMA, EvidenceBundle


def parse_evidence_bundle(raw: Any) -> EvidenceBundle:
    if not isinstance(raw, dict):
        raise ValueError("evidence bundle must be a JSON object")
    if raw.get("schema") != EVIDENCE_BUNDLE_SCHEMA:
        raise ValueError(f"unsupported schema: {raw.get('schema')!r}")
    return EvidenceBundle.model_validate(raw)


def load_evidence_bundle(path: Path | str) -> EvidenceBundle:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_evidence_bundle(data)
