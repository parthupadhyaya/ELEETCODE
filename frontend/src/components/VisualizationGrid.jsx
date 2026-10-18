import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

const GRID = [
  ['1', '1', '0', '0', '0', '1'],
  ['1', '1', '0', '0', '1', '1'],
  ['0', '0', '1', '0', '0', '0'],
  ['0', '0', '0', '1', '1', '0'],
  ['1', '0', '0', '1', '1', '0'],
]

const STEP_MS = 350

// Row-major sweep; placeholder until real execution traces come from the backend
const SEQUENCE = GRID.flatMap((row, r) => row.map((_, c) => `${r}-${c}`))
const LAST_STEP = SEQUENCE.length - 1

const gridVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.025 } },
}

const cellVariants = {
  hidden: { opacity: 0, scale: 0.6 },
  show: { opacity: 1, scale: 1 },
}

const spring = { type: 'spring', stiffness: 400, damping: 25 }

const BUTTON =
  'rounded-md border border-line bg-raised px-3 py-1 text-fg-strong enabled:cursor-pointer enabled:hover:border-accent disabled:opacity-40'

const CELL_COLORS = {
  land: 'bg-land text-fg-strong',
  water: 'bg-panel text-muted',
  visited: 'bg-visited text-fg-strong',
}

function VisualizationGrid() {
  const [step, setStep] = useState(-1)
  const [playRequested, setPlayRequested] = useState(false)
  const playing = playRequested && step < LAST_STEP

  useEffect(() => {
    if (!playing) return
    const id = setTimeout(() => setStep((s) => s + 1), STEP_MS)
    return () => clearTimeout(id)
  }, [playing, step])

  const activeKey = SEQUENCE[step]
  const visited = new Set(SEQUENCE.slice(0, Math.max(step, 0)))

  const togglePlay = () => {
    if (playing) {
      setPlayRequested(false)
      return
    }
    if (step >= LAST_STEP) setStep(-1)
    setPlayRequested(true)
  }

  const reset = () => {
    setPlayRequested(false)
    setStep(-1)
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex items-center gap-2 border-b border-line px-4 py-2">
        <button
          type="button"
          className={`${BUTTON} border-accent bg-accent/15`}
          onClick={togglePlay}
        >
          {playing ? 'Pause' : 'Play'}
        </button>
        <button
          type="button"
          className={BUTTON}
          disabled={playing || step >= LAST_STEP}
          onClick={() => setStep((s) => s + 1)}
        >
          Step
        </button>
        <button type="button" className={BUTTON} onClick={reset}>
          Reset
        </button>
        <span className="ml-auto font-mono text-xs text-muted">
          Step {step + 1} / {SEQUENCE.length}
        </span>
      </div>

      <div className="grid flex-1 place-items-center overflow-auto p-6">
        <motion.div
          className="grid w-full max-w-[520px] gap-2"
          style={{ gridTemplateColumns: `repeat(${GRID[0].length}, 1fr)` }}
          variants={gridVariants}
          initial="hidden"
          animate="show"
        >
          {GRID.map((row, r) =>
            row.map((value, c) => {
              const key = `${r}-${c}`
              const isActive = key === activeKey
              const kind = visited.has(key) ? 'visited' : value === '1' ? 'land' : 'water'

              return (
                <motion.div key={key} className="aspect-square" variants={cellVariants} transition={spring}>
                  <motion.div
                    className={`relative grid h-full place-items-center rounded-lg border border-line font-mono text-lg font-semibold transition-colors duration-250 ${CELL_COLORS[kind]}`}
                    animate={{ scale: isActive ? 1.1 : 1 }}
                    whileHover={{ scale: 1.06 }}
                    transition={spring}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="active-cell"
                        className="pointer-events-none absolute -inset-[3px] rounded-[10px] border-2 border-active shadow-[0_0_16px_rgba(245,177,76,0.35)]"
                        transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                      />
                    )}
                    <span className="relative">{value}</span>
                    <span className="absolute right-1.5 bottom-1 font-mono text-[10px] font-normal text-muted">
                      {r},{c}
                    </span>
                  </motion.div>
                </motion.div>
              )
            }),
          )}
        </motion.div>
      </div>

      <div className="flex flex-wrap gap-4 border-t border-line px-4 py-2.5 text-xs">
        <LegendItem swatch="bg-land">Land</LegendItem>
        <LegendItem swatch="bg-panel">Water</LegendItem>
        <LegendItem swatch="bg-visited">Visited</LegendItem>
        <LegendItem swatch="border-2 border-active">Current</LegendItem>
      </div>
    </div>
  )
}

function LegendItem({ swatch, children }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <i className={`size-3 rounded-[3px] border border-line ${swatch}`} />
      {children}
    </span>
  )
}

export default VisualizationGrid
