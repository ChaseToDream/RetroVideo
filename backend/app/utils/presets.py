import json
import os
from pathlib import Path
from typing import Any

from app.core.config import settings

PRESETS_DIR = Path(__file__).resolve().parent.parent.parent / "presets"


def load_preset(name: str) -> dict[str, Any]:
    """加载指定名称的预设配置"""
    preset_path = PRESETS_DIR / f"{name}.json"
    if not preset_path.exists():
        raise FileNotFoundError(f"Preset '{name}' not found")
    with open(preset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_presets() -> list[dict[str, Any]]:
    """列出所有可用预设"""
    presets = []
    for path in sorted(PRESETS_DIR.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            presets.append({
                "name": path.stem,
                "label": data.get("label", path.stem),
                "device": data.get("device", ""),
                "resolution": f"{data['video']['width']}x{data['video']['height']}",
                "fps": data["video"]["fps"],
                "output_format": data["output"]["format"],
            })
    return presets
