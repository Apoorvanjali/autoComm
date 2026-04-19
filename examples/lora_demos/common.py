"""
Shared helpers for isolated LoRA demos.

These utilities are intentionally scoped to examples/ so the main
AutoComm runtime remains unchanged.
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict

import numpy as np
import torch


@dataclass
class DemoReport:
    task: str
    base_model: str
    dataset: str
    train_samples: int
    eval_samples: int
    metrics: Dict[str, Any]
    trainable_parameters: int
    total_parameters: int
    trainable_percent: float
    output_dir: str
    generated_at_utc: str


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def best_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def count_parameters(model: torch.nn.Module) -> Dict[str, float]:
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    pct = (100.0 * trainable / total) if total else 0.0
    return {
        "trainable": int(trainable),
        "total": int(total),
        "trainable_percent": float(round(pct, 4)),
    }


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_report(path: str, report: DemoReport) -> None:
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(report), f, ensure_ascii=False, indent=2)


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
