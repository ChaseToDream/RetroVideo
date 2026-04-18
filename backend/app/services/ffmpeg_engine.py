import asyncio
import re
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.utils.presets import load_preset

NOISE_MAP = {"light": 8, "medium": 15, "strong": 20}
COLOR_PRESETS = {
    "original": {"saturation": 1.0, "contrast": 1.0, "brightness": 0.0, "hue": 0},
    "low_saturation": {"saturation": 0.6, "contrast": 1.1, "brightness": 0.0, "hue": 0},
    "yellowish": {"saturation": 0.7, "contrast": 1.05, "brightness": 0.02, "hue": 10},
    "greenish": {"saturation": 0.65, "contrast": 1.0, "brightness": 0.0, "hue": -15},
    "bluish": {"saturation": 0.7, "contrast": 1.1, "brightness": -0.02, "hue": 15},
    "high_contrast": {"saturation": 0.8, "contrast": 1.4, "brightness": 0.0, "hue": 0},
}


def build_ffmpeg_command(
    input_path: str,
    output_path: str,
    preset_name: str,
    params: dict[str, Any] | None = None,
    is_preview: bool = False,
) -> list[str]:
    """构建 FFmpeg 处理命令"""
    preset = load_preset(preset_name)
    if params:
        preset = _merge_params(preset, params)

    video_cfg = preset["video"]
    color_cfg = preset.get("color", {})
    noise_cfg = preset.get("noise", {})
    scanlines_cfg = preset.get("scanlines", {})
    watermark_cfg = preset.get("watermark", {})
    audio_cfg = preset.get("audio", {})
    output_cfg = preset.get("output", {})

    cmd = [settings.FFMPEG_PATH, "-y"]

    if is_preview:
        cmd.extend(["-t", str(settings.PREVIEW_DURATION)])

    cmd.extend(["-i", input_path])

    vf_filters = _build_video_filters(video_cfg, color_cfg, noise_cfg, scanlines_cfg, watermark_cfg)
    if vf_filters:
        cmd.extend(["-vf", vf_filters])

    af_filters = _build_audio_filters(audio_cfg)
    if af_filters:
        cmd.extend(["-af", af_filters])

    cmd.extend(["-c:v", "libx264"])
    cmd.extend(["-b:v", str(video_cfg.get("bitrate", "64k"))])
    cmd.extend(["-pix_fmt", "yuv420p"])

    if audio_cfg.get("codec") == "amr_nb":
        cmd.extend(["-c:a", "libopencore_amrnb"])
    else:
        cmd.extend(["-c:a", "aac"])
    audio_bitrate = audio_cfg.get("bitrate", "12k")
    cmd.extend(["-b:a", str(audio_bitrate)])

    output_format = output_cfg.get("format", "mp4")
    if output_format == "3gp":
        cmd.extend(["-f", "3gp"])
    else:
        cmd.extend(["-f", "mp4"])

    cmd.append(output_path)
    return cmd


def _build_video_filters(video_cfg, color_cfg, noise_cfg, scanlines_cfg, watermark_cfg) -> str:
    """构建视频滤镜链"""
    filters = []

    width = video_cfg.get("width", 176)
    height = video_cfg.get("height", 144)
    scale_flag = video_cfg.get("scale_flag", "neighbor")
    filters.append(f"scale={width}:{height}:flags={scale_flag}")

    fps = video_cfg.get("fps", 15)
    filters.append(f"fps={fps}")

    sat = color_cfg.get("saturation", 1.0)
    con = color_cfg.get("contrast", 1.0)
    bri = color_cfg.get("brightness", 0.0)
    if sat != 1.0 or con != 1.0 or bri != 0.0:
        filters.append(f"eq=saturation={sat}:contrast={con}:brightness={bri}")

    hue = color_cfg.get("hue", 0)
    if hue != 0:
        filters.append(f"hue=h={hue}")

    if noise_cfg.get("enabled", False):
        strength = noise_cfg.get("strength", "medium")
        noise_val = NOISE_MAP.get(strength, 15)
        filters.append(f"noise=alls={noise_val}:allf=t+u")

    if scanlines_cfg.get("enabled", False):
        opacity = scanlines_cfg.get("opacity", 0.15)
        filters.append(f"drawbox=y=ih-20:w=iw:h=20:color=black@{opacity}:t=fill")

    if watermark_cfg.get("enabled", False):
        fmt = watermark_cfg.get("format", "%Y.%m.%d %H\\:%M\\:%S")
        font_size = watermark_cfg.get("font_size", 10)
        font_color = watermark_cfg.get("font_color", "white")
        pos = watermark_cfg.get("position", "bottom_right")
        escaped_fmt = fmt.replace(":", "\\\\\\:")
        if pos == "bottom_right":
            x, y = "w-text_w-5", "h-18"
        elif pos == "bottom_left":
            x, y = "5", "h-18"
        elif pos == "top_right":
            x, y = "w-text_w-5", "5"
        else:
            x, y = "5", "5"
        filters.append(
            f"drawtext=text='%{{localtime\\:{escaped_fmt}}}':"
            f"fontsize={font_size}:fontcolor={font_color}:x={x}:y={y}"
        )

    return ",".join(filters)


def _build_audio_filters(audio_cfg) -> str:
    """构建音频滤镜链"""
    filters = []
    sample_rate = audio_cfg.get("sample_rate", 8000)
    if sample_rate and sample_rate < 44100:
        filters.append(f"aformat=sample_rates={sample_rate}")
    channels = audio_cfg.get("channels", 1)
    if channels == 1:
        filters.append("aformat=channel_layouts=mono")
    return ",".join(filters)


def _merge_params(preset: dict, params: dict) -> dict:
    """合并用户自定义参数到预设"""
    import copy
    merged = copy.deepcopy(preset)
    for key, value in params.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


async def run_ffmpeg(cmd: list[str]) -> tuple[bool, str]:
    """执行 FFmpeg 命令，返回 (成功与否, 输出信息)"""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    output = stderr.decode("utf-8", errors="replace")
    return proc.returncode == 0, output


def parse_progress(stderr_output: str) -> int:
    """从 FFmpeg stderr 输出解析处理进度百分比"""
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr_output)
    if not duration_match:
        return 0
    total = int(duration_match.group(1)) * 3600 + int(duration_match.group(2)) * 60 + float(duration_match.group(3))

    time_matches = re.findall(r"time=\s*(\d+):(\d+):(\d+\.\d+)", stderr_output)
    if not time_matches:
        return 0
    last = time_matches[-1]
    current = int(last[0]) * 3600 + int(last[1]) * 60 + float(last[2])

    if total <= 0:
        return 0
    return min(int(current / total * 100), 99)
