export default function Header() {
  return (
    <header className="border-b border-[var(--retro-border)] px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-2xl">📼</span>
        <h1 className="text-xl font-bold text-[var(--retro-green)] tracking-wider font-mono">
          RetroVid
        </h1>
        <span className="text-xs text-gray-500 ml-2">v1.0</span>
      </div>
      <div className="text-sm text-gray-500 font-mono">
        复古视频画质转换工具
      </div>
    </header>
  )
}
