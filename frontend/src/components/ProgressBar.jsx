import { useEffect, useRef } from 'react'
import useStore from '../store'
import { getTaskProgress, getDownloadUrl } from '../services/api'

export default function ProgressBar() {
  const { task, taskProgress, setTaskProgress } = useStore()
  const intervalRef = useRef(null)

  useEffect(() => {
    if (!task || !task.task_id) return
    if (task.status === 'completed' || task.status === 'failed') return

    intervalRef.current = setInterval(async () => {
      try {
        const progress = await getTaskProgress(task.task_id)
        setTaskProgress(progress)
        if (progress.status === 'completed' || progress.status === 'failed') {
          clearInterval(intervalRef.current)
        }
      } catch {
        clearInterval(intervalRef.current)
      }
    }, 2000)

    return () => clearInterval(intervalRef.current)
  }, [task])

  if (!task) return null

  const progress = taskProgress?.progress ?? (task.status === 'completed' ? 100 : 0)
  const status = taskProgress?.status ?? task.status
  const step = taskProgress?.current_step ?? ''

  return (
    <div className="mt-6 bg-[var(--retro-gray)] rounded-lg p-4">
      <h3 className="text-[var(--retro-amber)] text-sm mb-3 tracking-wider">▸ 处理进度</h3>
      <div className="w-full bg-[var(--retro-dark)] rounded-full h-4 mb-2">
        <div
          className={`h-4 rounded-full transition-all duration-500 ${
            status === 'failed' ? 'bg-red-500' : 'bg-[var(--retro-green)]'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="flex justify-between text-sm">
        <span className={status === 'failed' ? 'text-red-400' : 'text-gray-300'}>
          {status === 'completed' ? '✅ 处理完成' : status === 'failed' ? '❌ 处理失败' : `${progress}% — ${step}`}
        </span>
        {status === 'completed' && (
          <a
            href={getDownloadUrl(task.task_id)}
            className="text-[var(--retro-green)] hover:underline font-bold"
            download
          >
            ⬇ 下载
          </a>
        )}
      </div>
    </div>
  )
}
