import { useState, useEffect, useRef } from 'react'
import useStore from '../store'
import { getPreview } from '../services/api'

export default function VideoPreview() {
  const { video, selectedPreset, previewUrl, setPreviewUrl, isPreviewLoading, setIsPreviewLoading } = useStore()
  const [showPreview, setShowPreview] = useState(false)
  const debounceRef = useRef(null)

  useEffect(() => {
    if (!video) return
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      setIsPreviewLoading(true)
      try {
        const url = await getPreview(video.id, selectedPreset)
        if (previewUrl) URL.revokeObjectURL(previewUrl)
        setPreviewUrl(url)
      } catch (err) {
        console.error('预览生成失败:', err)
      } finally {
        setIsPreviewLoading(false)
      }
    }, 500)
    return () => clearTimeout(debounceRef.current)
  }, [video, selectedPreset])

  if (!video) return null

  return (
    <div className="mt-6">
      <h3 className="text-[var(--retro-amber)] text-sm mb-3 tracking-wider">▸ 视频预览</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[var(--retro-gray)] rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-2">原始视频</p>
          <video
            src={`/api/v1/videos/${video.id}/preview?preset=original`}
            controls
            className="w-full rounded"
            style={{ maxHeight: '240px' }}
          />
        </div>
        <div className="bg-[var(--retro-gray)] rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-2">复古效果预览</p>
          {isPreviewLoading ? (
            <div className="flex items-center justify-center h-40 text-[var(--retro-amber)]">
              <span className="animate-pulse">生成预览中...</span>
            </div>
          ) : previewUrl ? (
            <video
              src={previewUrl}
              controls
              className="w-full rounded"
              style={{ maxHeight: '240px' }}
            />
          ) : (
            <div className="flex items-center justify-center h-40 text-gray-500">
              选择预设后生成预览
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
