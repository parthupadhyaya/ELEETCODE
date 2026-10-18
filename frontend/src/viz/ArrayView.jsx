import { AnimatePresence, motion } from 'framer-motion'
import { aiPositions, fmt, normIndex, plain, pointersFor, same, windowFor } from './model.js'
import { pointerColor } from './colors.js'

const spring = { type: 'spring', stiffness: 220, damping: 26 }
const GAP = 6

function cellWidth(texts) {
  const longest = Math.max(1, ...texts.map((t) => t.length))
  return Math.min(160, Math.max(48, longest * 10 + 22))
}

/** Equal values keep the same key, so sorts/pops/shifts animate as moves. */
function itemKeys(texts) {
  const seen = {}
  return texts.map((t) => {
    seen[t] = (seen[t] ?? 0) + 1
    return `${t}#${seen[t]}`
  })
}

function accessMap(accesses, length) {
  const map = new Map()
  for (const a of accesses) {
    const kind = a.write ? 'write' : 'read'
    if (a.slice) {
      const [lo, hi] = a.slice
      const end = Math.min(hi ?? length, length)
      for (let i = Math.max(lo, 0); i < end; i++) map.set(i, kind)
    } else if (a.indexes.length === 1 && a.indexes[0] !== null && !a.membership) {
      const i = normIndex(a.indexes[0], length)
      if (i >= 0 && i < length) map.set(i, kind)
    }
  }
  return map
}

function PointerRow({ pointers, width }) {
  const byIndex = new Map()
  for (const p of pointers) {
    if (!byIndex.has(p.index)) byIndex.set(p.index, [])
    byIndex.get(p.index).push(p.name)
  }
  if (!byIndex.size) return null
  const depth = Math.max(...[...byIndex.values()].map((v) => v.length))
  return (
    <div className="ptr-row" style={{ height: 22 + depth * 18 }}>
      {[...byIndex.entries()].map(([index, names]) => (
        <motion.div
          key={names.join(',')}
          className="ptr"
          initial={false}
          animate={{ x: index * (width + GAP) + width / 2 }}
          transition={spring}
        >
          <span className="ptr-arrow">▲</span>
          {names.map((n) => (
            <span key={n} className="ptr-name" style={{ color: pointerColor(n) }}>
              {n}
            </span>
          ))}
        </motion.div>
      ))}
    </div>
  )
}

/** Row of blocks with index labels, pointer arrows, and a sliding-window band. */
export function ArrayView({ items, heap, ints, accesses = [], aiIndexes = [], prevItems, bars = false, showPointers = true }) {
  const texts = items.map((v) => fmt(v, heap, { raw: true }))
  const keys = itemKeys(texts)
  const width = cellWidth(texts)
  const touched = accessMap(accesses, items.length)
  const ai = aiPositions(aiIndexes, items.length)
  const pointers = showPointers ? pointersFor(items.length, ints) : []
  const win = showPointers ? windowFor(items.length, ints) : null
  const values = items.map(plain)
  const numeric = bars && values.every((v) => typeof v === 'number' && Number.isFinite(v))
  const maxAbs = numeric ? Math.max(1, ...values.map((v) => Math.abs(v))) : 1

  if (!items.length) return <div className="empty">empty</div>

  return (
    <div className="array" style={{ '--cell': `${width}px` }}>
      <div className="array-track">
        {win && (
          <motion.div
            className="window-band"
            initial={false}
            animate={{
              x: win[0] * (width + GAP) - 4,
              width: (win[1] - win[0] + 1) * (width + GAP) - GAP + 8,
            }}
            transition={spring}
          />
        )}
        <div className="array-cells">
          <AnimatePresence initial={false} mode="popLayout">
            {items.map((v, i) => {
              const changed = prevItems && i < prevItems.length && !same(prevItems[i], v)
              const access = touched.get(i)
              const cls = ['cell', access && `is-${access}`, changed && 'is-changed', ai.has(i) && 'is-ai']
                .filter(Boolean)
                .join(' ')
              return (
                <motion.div
                  key={keys[i]}
                  layout
                  className="cell-wrap"
                  initial={{ opacity: 0, y: -14, scale: 0.7 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 14, scale: 0.7 }}
                  transition={spring}
                >
                  {numeric && (
                    <div className="bar-slot">
                      <motion.div
                        className={`bar ${values[i] < 0 ? 'is-neg' : ''}`}
                        initial={false}
                        animate={{ height: `${(Math.abs(values[i]) / maxAbs) * 100}%` }}
                        transition={spring}
                      />
                    </div>
                  )}
                  <div className={cls}>{texts[i]}</div>
                  <div className="cell-index">{i}</div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>
      </div>
      {showPointers && <PointerRow pointers={pointers} width={width} />}
    </div>
  )
}

/** Vertical stack: top of the stack is drawn at the top. */
export function StackView({ items, heap, accesses = [], aiIndexes = [] }) {
  const texts = items.map((v) => fmt(v, heap, { raw: true }))
  const touched = accessMap(accesses, items.length)
  const ai = aiPositions(aiIndexes, items.length)
  return (
    <div className="stack">
      <div className="stack-label">top</div>
      <div className="stack-body">
        <AnimatePresence initial={false}>
          {texts
            .map((t, i) => ({ t, i }))
            .reverse()
            .map(({ t, i }) => (
              <motion.div
                key={`${i}:${t}`}
                layout
                className={`stack-item ${i === items.length - 1 ? 'is-top' : ''} ${touched.get(i) ? `is-${touched.get(i)}` : ''} ${ai.has(i) ? 'is-ai' : ''}`}
                initial={{ opacity: 0, y: -24 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -24, transition: { duration: 0.15 } }}
                transition={spring}
              >
                <span className="stack-index">{i}</span>
                {t}
              </motion.div>
            ))}
        </AnimatePresence>
        {!items.length && <div className="empty">empty</div>}
      </div>
      <div className="stack-base" />
    </div>
  )
}

/** Queue / deque: front on the left, back on the right. */
export function QueueView({ items, heap, aiIndexes = [] }) {
  const texts = items.map((v) => fmt(v, heap, { raw: true }))
  const keys = itemKeys(texts)
  const ai = aiPositions(aiIndexes, items.length)
  return (
    <div className="queue">
      <span className="queue-end">front</span>
      <div className="queue-body">
        <AnimatePresence initial={false} mode="popLayout">
          {texts.map((t, i) => (
            <motion.div
              key={keys[i]}
              layout
              className={`queue-item ${ai.has(i) ? 'is-ai' : ''}`}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -24 }}
              transition={spring}
            >
              {t}
            </motion.div>
          ))}
        </AnimatePresence>
        {!items.length && <div className="empty">empty</div>}
      </div>
      <span className="queue-end">back</span>
    </div>
  )
}
