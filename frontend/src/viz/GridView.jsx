import { motion } from 'framer-motion'
import { MARKER_COLORS, MARKER_SOLID } from './colors.js'
import { accessesFor, aiIndexes, aiPositions, fmt, gridCursor, isInt, isRef, isTuple, normIndex, plain } from './model.js'

const CELL_STYLES = {
  1: 'is-land',
  0: 'is-water',
  X: 'is-wall',
  O: 'is-open',
  Q: 'is-queen',
  '#': 'is-used',
  T: 'is-safe',
  '.': 'is-dot',
}

function cellClass(value) {
  const v = plain(value)
  if (typeof v === 'string') return CELL_STYLES[v] ?? ''
  if (v === true) return 'is-true'
  if (v === -1) return 'is-wall'
  return ''
}

/** Cells that sets / queues / dicts in scope contain, e.g. seen = {(0, 1)}. */
function gridMarkers(scene, rows, cols) {
  const out = []
  const inGrid = (v) =>
    isTuple(v) && v.items.length === 2 && isInt(v.items[0]) && isInt(v.items[1]) &&
    v.items[0] >= 0 && v.items[0] < rows && v.items[1] >= 0 && v.items[1] < cols
  for (const s of scene.structures) {
    const cells = new Map()
    if (s.kind === 'set' || s.kind === 'queue') {
      for (const v of s.obj.items) if (inGrid(v)) cells.set(`${v.items[0]},${v.items[1]}`, null)
    } else if (s.kind === 'hashmap') {
      for (const [k, v] of s.obj.entries) if (inGrid(k)) cells.set(`${k.items[0]},${k.items[1]}`, fmt(v, scene.heap))
    }
    if (cells.size) out.push({ name: s.names[0], cells, color: MARKER_COLORS[out.length % MARKER_COLORS.length], solid: MARKER_SOLID[out.length % MARKER_SOLID.length] })
  }
  return out
}

export function GridView({ rows, heap, scene, names, prevRows }) {
  const R = rows.length
  const C = Math.max(0, ...rows.map((r) => r.length))
  const { primary, secondary } = gridCursor(R, C, scene.ints)
  const markers = gridMarkers(scene, R, C)

  const touched = new Map()
  const touchedRows = new Map()
  for (const a of accessesFor(scene, names)) {
    if (a.membership) continue
    const kind = a.write ? 'write' : 'read'
    if (a.indexes.length === 2 && a.indexes.every((v) => v !== null)) {
      const r = normIndex(a.indexes[0], R)
      const c = normIndex(a.indexes[1], C)
      touched.set(`${r},${c}`, kind)
    } else if (a.indexes.length === 1 && a.indexes[0] !== null) {
      touchedRows.set(normIndex(a.indexes[0], R), kind)
    }
  }

  // Cells (or whole rows) Gemini's current step points at
  const aiCells = new Set()
  const aiRows = new Set()
  for (const path of aiIndexes(scene, names)) {
    if (path.length === 2) aiCells.add(`${normIndex(path[0], R)},${normIndex(path[1], C)}`)
    else if (path.length === 1) aiRows.add(normIndex(path[0], R))
  }

  const numbers = rows.flat().map(plain).filter((v) => typeof v === 'number' && Number.isFinite(v) && v !== 2147483647)
  const maxNum = numbers.length ? Math.max(...numbers.map(Math.abs)) : 0
  const allNumeric = numbers.length === rows.flat().length && maxNum > 0
  const cellSize = C > 10 ? 28 : 34

  return (
    <div className="grid-wrap">
      <div className="grid" style={{ gridTemplateColumns: `18px repeat(${C}, ${cellSize}px)` }}>
        <span />
        {Array.from({ length: C }, (_, c) => (
          <span key={c} className={`grid-head ${primary?.c === c ? 'is-on' : ''}`}>{c}</span>
        ))}
        {rows.map((row, r) => [
          <span key={`h${r}`} className={`grid-head ${primary?.r === r ? 'is-on' : ''}`}>{r}</span>,
          ...Array.from({ length: C }, (_, c) => {
            const value = row[c]
            if (value === undefined) return <span key={`${r},${c}`} />
            const key = `${r},${c}`
            const text = fmt(value, heap, { raw: true })
            const prev = prevRows?.[r]?.[c]
            const changed = prevRows && prev !== undefined && JSON.stringify(prev) !== JSON.stringify(value)
            const isCursor = primary && primary.r === r && primary.c === c
            const isSecondary = secondary && secondary.r === r && secondary.c === c
            const access = touched.get(key) ?? touchedRows.get(r)
            const marks = markers.filter((m) => m.cells.has(key))
            const v = plain(value)
            const heat = allNumeric && typeof v === 'number' ? Math.min(1, Math.abs(v) / maxNum) : 0
            const cls = [
              'gcell',
              cellClass(value),
              access && `is-${access}`,
              isCursor && 'is-cursor',
              isSecondary && 'is-secondary',
              (aiCells.has(key) || aiRows.has(r)) && 'is-ai',
            ]
              .filter(Boolean)
              .join(' ')
            return (
              <motion.div
                key={`${key}:${text}`}
                className={cls}
                style={{
                  '--heat': heat,
                  backgroundColor: marks[0]?.color,
                }}
                initial={changed ? { scale: 1.35 } : false}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 18 }}
                title={marks.map((m) => m.name).join(', ')}
              >
                {allNumeric && <span className="gcell-heat" />}
                <span className="gcell-text">{text.length > 5 ? `${text.slice(0, 4)}…` : text}</span>
                {marks.length > 0 && (
                  <span className="gcell-marks">
                    {marks.map((m) => (
                      <i key={m.name} style={{ background: m.solid }} />
                    ))}
                  </span>
                )}
                {marks.find((m) => m.cells.get(key) !== null && m.cells.get(key) !== undefined) && (
                  <span className="gcell-memo">{marks.find((m) => m.cells.get(key))?.cells.get(key)}</span>
                )}
              </motion.div>
            )
          }),
        ])}
      </div>
      {(markers.length > 0 || primary) && (
        <div className="legend">
          {primary && (
            <span>
              <i className="legend-cursor" /> ({primary.label}) = ({primary.r}, {primary.c})
            </span>
          )}
          {secondary && (
            <span>
              <i className="legend-secondary" /> (nr, nc) = ({secondary.r}, {secondary.c})
            </span>
          )}
          {markers.map((m) => (
            <span key={m.name}>
              <i style={{ background: m.solid }} /> in {m.name}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

function pair(v, heap) {
  const items = isTuple(v) ? v.items : isRef(v) ? heap[v.id]?.items : null
  return items ? items.map(plain) : [0, 0]
}

/** Intervals drawn as bars on a number line. */
export function IntervalsView({ items, heap, ints, aiIndexes = [] }) {
  const pairs = items.map((v) => pair(v, heap))
  // [i] is interval i and [i, 0] / [i, 1] one of its endpoints: either way, bar i
  const ai = aiPositions(aiIndexes.map((p) => p.slice(0, 1)), pairs.length)
  const lo = Math.min(...pairs.map((p) => p[0]))
  const hi = Math.max(...pairs.map((p) => p[1]))
  const span = Math.max(1, hi - lo)
  const W = 320
  const ROW = 22
  const x = (v) => 30 + ((v - lo) / span) * W
  const ticks = span <= 24 ? Array.from({ length: span + 1 }, (_, k) => lo + k) : Array.from({ length: 7 }, (_, k) => Math.round(lo + (span * k) / 6))
  const current = isInt(ints.i) ? ints.i : null
  return (
    <svg className="intervals" width={W + 60} height={pairs.length * ROW + 34}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={x(t)} x2={x(t)} y1={4} y2={pairs.length * ROW + 10} className="tick-line" />
          <text x={x(t)} y={pairs.length * ROW + 26} className="tick-text">{t}</text>
        </g>
      ))}
      {pairs.map(([a, b], i) => (
        <g key={i}>
          <text x={4} y={14 + i * ROW} className="tick-text" textAnchor="start">{i}</text>
          <motion.rect
            initial={false}
            animate={{ x: x(a), width: Math.max(4, x(b) - x(a)) }}
            y={4 + i * ROW}
            height={ROW - 8}
            rx={4}
            className={`interval-bar ${current === i ? 'is-current' : ''} ${ai.has(i) ? 'is-ai' : ''}`}
          />
          <text x={x(a) + 4} y={16 + i * ROW} className="interval-text" textAnchor="start">
            [{a}, {b}]
          </text>
        </g>
      ))}
    </svg>
  )
}
