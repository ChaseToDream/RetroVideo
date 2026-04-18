import { useEffect } from 'react'
import Header from './components/Header'
import UploadZone from './components/UploadZone'
import PresetSelector from './components/PresetSelector'
import ParamPanel from './components/ParamPanel'
import VideoPreview from './components/VideoPreview'
import ProgressBar from './components/ProgressBar'
import useStore from './store'
import { processVideo, getPreset } from './services/api'

function App() {
  const { video, selectedPreset, customParams, setTask, setPresetDetail, task, reset } = useStore()

  useEffect(() => {
    if (video) {
      getPreset(selectedPreset).then(setPresetDetail).catch(() => setPresetDetail(null))
    }
  }, [video, selectedPreset])

  const handleProcess = async () => {
    if (!video) return
    try {
      const result = await processVideo(video.id, selectedPreset, customParams)
      setTask(result)
    } catch (err) {
      alert('处理请求失败: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleReset = () => {
    reset()
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-6">
        <UploadZone />

        {video && (
          <div className="mt-4 bg-[var(--retro-gray)] rounded-lg p-3 text-sm">
            <span className="text-[var(--retro-green)]">✓</span>{' '}
            {video.filename} ({(video.file_size / 1024 / 1024).toFixed(1)}MB
            {video.duration && `, ${video.duration.toFixed(1)}s`}
            {video.resolution && `, ${video.resolution}`})
            <button onClick={handleReset} className="ml-3 text-red-400 hover:text-red-300 text-xs">
              重新上传
            </button>
          </div>
        )}

        <PresetSelector />
        <ParamPanel />
        <VideoPreview />

        {video && !task && (
          <div className="mt-6 text-center">
            <button
              onClick={handleProcess}
              className="bg-[var(--retro-green)] text-black font-bold px-8 py-3 rounded-lg text-lg hover:brightness-110 transition-all font-mono tracking-wider"
            >
              🎬 开始转换
            </button>
          </div>
        )}

        <ProgressBar />
      </main>
      <footer className="border-t border-[var(--retro-border)] px-6 py-3 text-center text-xs text-gray-600">
        © 2026 RetroVid | 复古视频画质转换工具
      </footer>
    </div>
  )
}

export default App
