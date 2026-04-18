import useStore from '../store'
import { PRESET_LIST } from '../utils/constants'
import { getPreset } from '../services/api'

export default function PresetSelector() {
  const { selectedPreset, setSelectedPreset, setPresetDetail, video } = useStore()

  if (!video) return null

  const handleSelect = async (name) => {
    setSelectedPreset(name)
    try {
      const detail = await getPreset(name)
      setPresetDetail(detail)
    } catch {
      setPresetDetail(null)
    }
  }

  return (
    <div className="mt-6">
      <h3 className="text-[var(--retro-amber)] text-sm mb-3 tracking-wider">▸ 风格预设</h3>
      <div className="flex flex-wrap gap-2">
        {PRESET_LIST.map((p) => (
          <button
            key={p.name}
            onClick={() => handleSelect(p.name)}
            className={`px-4 py-2 rounded text-sm font-mono transition-all
              ${selectedPreset === p.name
                ? 'bg-[var(--retro-green)] text-black font-bold'
                : 'bg-[var(--retro-gray)] text-gray-300 hover:bg-[var(--retro-border)]'
              }`}
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>
  )
}
