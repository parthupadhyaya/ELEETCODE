import { useEffect, useMemo, useRef } from 'react'
import { XTerm } from '@pablo-lion/xterm-react'
import { FitAddon } from '@xterm/addon-fit'

const OPTIONS = {
  fontFamily: "ui-monospace, 'Cascadia Code', Consolas, monospace",
  fontSize: 12,
  cursorBlink: true,
  convertEol: true,
  theme: {
    background: '#0d0f14',
    foreground: '#a3abbd',
    cursor: '#7c9cff',
    selectionBackground: '#252a36',
  },
}

// `ref` receives the XTerm instance, which exposes write()/writeln()/clear()
function Terminal({ ref }) {
  const containerRef = useRef(null)
  const xtermRef = useRef(null)
  const fitAddon = useMemo(() => new FitAddon(), [])
  const addons = useMemo(() => [fitAddon], [fitAddon])

  useEffect(() => {
    const xterm = xtermRef.current
    if (!xterm) return

    xterm.writeln('\x1b[38;2;124;156;255mLeetCode Visualizer\x1b[0m console')
    xterm.writeln('\x1b[38;2;93;101;120mOutput from your solution will appear here.\x1b[0m')

    // Refit whenever the pane changes size
    const observer = new ResizeObserver(() => fitAddon.fit())
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [fitAddon])

  const setRefs = (instance) => {
    xtermRef.current = instance
    if (typeof ref === 'function') ref(instance)
    else if (ref) ref.current = instance
  }

  return (
    <div ref={containerRef} className="h-full min-h-0 overflow-hidden px-3 py-2">
      <XTerm ref={setRefs} className="h-full" options={OPTIONS} addons={addons} />
    </div>
  )
}

export default Terminal
