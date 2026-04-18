import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import useStore from '../store'
import { uploadVideo } from '../services/api'

export default function UploadZone() {
  const { setVideo, setUploadProgress, setIsUploading, isUploading, video } = useStore()

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    const file = acceptedFiles[0]
    setIsUploading(true)
    setUploadProgress(0)
    try {
      const data = await uploadVideo(file, (progress) => {
        setUploadProgress(progress)
      })
      setVideo(data)
    } catch (err) {
      alert('上传失败: ' + (err.response?.data?.detail || err.message))
    } finally {
      setIsUploading(false)
    }
  }, [setVideo, setUploadProgress, setIsUploading])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm'] },
    maxFiles: 1,
    disabled: isUploading,
  })

  if (video) return null

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors
        ${isDragActive ? 'border-[var(--retro-green)] bg-[var(--retro-green)]/5' : 'border-[var(--retro-border)] hover:border-[var(--retro-amber)]'}`}
    >
      <input {...getInputProps()} />
      {isUploading ? (
        <div>
          <p className="text-[var(--retro-amber)] text-lg mb-2">上传中...</p>
          <div className="w-64 mx-auto bg-[var(--retro-gray)] rounded-full h-3">
            <div
              className="bg-[var(--retro-green)] h-3 rounded-full transition-all"
              style={{ width: `${useStore.getState().uploadProgress}%` }}
            />
          </div>
        </div>
      ) : isDragActive ? (
        <p className="text-[var(--retro-green)] text-lg">松开以上传视频</p>
      ) : (
        <div>
          <p className="text-2xl mb-2">📺</p>
          <p className="text-lg mb-1">拖拽视频文件到此处</p>
          <p className="text-sm text-gray-500">或点击选择文件 (MP4/AVI/MOV/MKV/WebM, 最大500MB)</p>
        </div>
      )}
    </div>
  )
}
