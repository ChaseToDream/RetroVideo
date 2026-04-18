import { useState, useEffect } from 'react'
import useStore from '../store'
import { RESOLUTION_OPTIONS, FPS_OPTIONS, BITRATE_OPTIONS, COLOR_OPTIONS, NOISE_OPTIONS, AUDIO_OPTIONS, OUTPUT_FORMAT_OPTIONS } from '../utils/constants'

export default function ParamPanel() {
  const { video, selectedPreset, presetDetail, customParams, setCustomParams, setPreviewUrl, setIsPreviewLoading } = useStore()
  const [localParams, setLocalParams] = useState({})

  useEffect(() => {
    if (presetDetail) {
      setLocalParams({})
    }
  }, [presetDetail])

  if (!video || !presetDetail) return null

  const updateParam = (key, value) => {
    const newParams = { ...localParams, [key]: value }
    setLocalParams(newParams)
    setCustomParams(newParams)
  }

  const currentVideo = { ...presetDetail.video, ...localParams.video }
  const currentColor = { ...presetDetail.color, ...localParams.color }

  return (
    <div className="mt-6 bg-[var(--retro-gray)] rounded-lg p-4">
      <h3 className="text-[var(--retro-amber)] text-sm mb-4 tracking-wider">▸ 参数调整</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs text-gray-400 mb-1">分辨率</label>
          <select
            className="w-full bg-[var(--retro-dark)] border border-[var(--retro-border)] rounded px-2 py-1.5 text-sm text-gray-200"
            value={`${currentVideo.width}x${currentVideo.height}`}
            onChange={(e) => {
              const opt = RESOLUTION_OPTIONS.find(r => `${r.width}x${r.height}` === e.target.value)
              if (opt) updateParam('video', { ...localParams.video, width: opt.width, height: opt.height })
            }}
          >
            {RESOLUTION_OPTIONS.map(r => (
              <option key={`${r.width}x${r.height}`} value={`${r.width}x${r.height}`}>{r.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">帧率</label>
          <select
            className="w-full bg-[var(--retro-dark)] border border-[var(--retro-border)] rounded px-2 py-1.5 text-sm text-gray-200"
            value={currentVideo.fps}
            onChange={(e) => updateParam('video', { ...localParams.video, fps: parseInt(e.target.value) })}
          >
            {FPS_OPTIONS.map(f => <option key={f} value={f}>{f} fps</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">比特率</label>
          <select
            className="w-full bg-[var(--retro-dark)] border border-[var(--retro-border)] rounded px-2 py-1.5 text-sm text-gray-200"
            value={currentVideo.bitrate}
            onChange={(e) => updateParam('video', { ...localParams.video, bitrate: e.target.value })}
          >
            {BITRATE_OPTIONS.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">色彩效果</label>
          <select
            className="w-full bg-[var(--retro-dark)] border border-[var(--retro-border)] rounded px-2 py-1.5 text-sm text-gray-200"
            value={localParams.colorEffect || 'original'}
            onChange={(e) => updateParam('colorEffect', e.target.value)}
          >
            {COLOR_OPTIONS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">噪点强度</label>
          <select
            className="w-full bg-[var(--retro-dark)] border border-[var(--retro-border)] rounded px-2 py-1.5 text-sm text-gray-200"
            value={localParams.noiseStrength ?? presetDetail.noise?.strength ?? 'medium'}
            onChange={(e) => updateParam('noiseStrength', e.target.value)}
          >
            {NOISE_OPTIONS.map(n => <option key={n.value} value={n.value}>{n.label}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">扫描线</label>
          <label className="flex items-center gap-2 mt-1">
            <input
              type="checkbox"
              checked={localParams.scanlines ?? presetDetail.scanlines?.enabled ?? true}
              onChange={(e) => updateParam('scanlines', e.target.checked)}
              className="accent-[var(--retro-green)]"
            />
            <span className="text-sm text-gray-300">开启</span>
          </label>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">日期水印</label>
          <label className="flex items-center gap-2 mt-1">
            <input
              type="checkbox"
              checked={localParams.watermark ?? presetDetail.watermark?.enabled ?? true}
              onChange={(e) => updateParam('watermark', e.target.checked)}
              className="accent-[var(--retro-green)]"
            />
            <span className="text-sm text-gray-300">开启</span>
          </label>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">音频效果</label>
          <select
            className="w-full bg-[var(--retro-dark)] border border-[var(--retro-border)] rounded px-2 py-1.5 text-sm text-gray-200"
            value={localParams.audioEffect || 'low_mono'}
            onChange={(e) => updateParam('audioEffect', e.target.value)}
          >
            {AUDIO_OPTIONS.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">输出格式</label>
          <select
            className="w-full bg-[var(--retro-dark)] border border-[var(--retro-border)] rounded px-2 py-1.5 text-sm text-gray-200"
            value={localParams.outputFormat ?? presetDetail.output?.format ?? 'mp4'}
            onChange={(e) => updateParam('outputFormat', e.target.value)}
          >
            {OUTPUT_FORMAT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
      </div>
    </div>
  )
}
