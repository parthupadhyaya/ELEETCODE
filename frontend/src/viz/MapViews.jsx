import { AnimatePresence, motion } from 'framer-motion'
import { useState } from 'react'
import { fmt, isRef } from './model.js'

const spring = { type: 'spring', stiffness: 220, damping: 26 }

/**
 * Illustrative hash -> bucket. Python really uses open addressing, but small
 * ints hash to themselves just like this, and chaining is the easiest way to
 * picture "the key decides where the value lives".
 */
function bucketOf(key, capacity) {
  const k = JSON.stringify(key)
  if (/^-?\d+$/.test(k)) return ((Number(k) % capacity) + capacity) % capacity
  let h = 5381
  for (const ch of k) h = ((h * 33) ^ ch.charCodeAt(0)) >>> 0
  return h % capacity
}

function capacityFor(n) {
  let cap = 8
  while (cap * 0.66 < n) cap *= 2
  return cap
}

function ModeToggle({ mode, setMode }) {
  return (
    <div className="mode-toggle">
      {['table', 'buckets'].map((m) => (
        <button key={m} type="button" className={mode === m ? 'is-on' : ''} onClick={() => setMode(m)}>
          {m}
        </button>
      ))}
    </div>
  )
}

/** Value inside a hashmap row: containers become little chip rows. */
function InlineValue({ value, heap }) {
  if (isRef(value)) {
    const obj = heap[value.id]
    if (obj && ['list', 'set', 'deque'].includes(obj.t)) {
      return (
        <span className={`chips ${obj.t === 'set' ? 'is-set' : ''}`}>
          {obj.t === 'set' ? '{' : '['}
          {obj.items.map((x, i) => (
            <span key={i} className="chip">
              {fmt(x, heap, { raw: true })}
            </span>
          ))}
          {obj.t === 'set' ? '}' : ']'}
        </span>
      )
    }
  }
  return <span>{fmt(value, heap)}</span>
}

function Buckets({ entries, heap, keyState, renderValue }) {
  const capacity = capacityFor(entries.length)
  const buckets = Array.from({ length: capacity }, () => [])
  for (const e of entries) buckets[bucketOf(e.key, capacity)].push(e)
  return (
    <div className="buckets">
      {buckets.map((items, b) => (
        <div key={b} className="bucket">
          <span className="bucket-index">{b}</span>
          <span className="bucket-slot" />
          <AnimatePresence initial={false}>
            {items.map((e) => (
              <motion.span
                key={JSON.stringify(e.key)}
                layout
                className={`bucket-entry ${keyState(e.key) ?? ''}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.6 }}
                transition={spring}
              >
                <span className="bucket-arrow">→</span>
                <b>{fmt(e.key, heap)}</b>
                {renderValue && <>: {renderValue(e.value)}</>}
              </motion.span>
            ))}
          </AnimatePresence>
        </div>
      ))}
      <div className="bucket-note">bucket = hash(key) % {capacity}</div>
    </div>
  )
}

/**
 * keyStates: Map(key JSON -> 'read'|'write'|'check') for keys the current
 * line touches. aiKeys: Set of key JSON Gemini's current step points at.
 * prevObj: the same dict at the previous step.
 */
export function HashMapView({ obj, heap, prevObj, keyStates, aiKeys = new Set() }) {
  const [mode, setMode] = useState('table')
  const prev = new Map((prevObj?.entries ?? []).map(([k, v]) => [JSON.stringify(k), JSON.stringify(v)]))
  const entries = obj.entries.map(([key, value]) => {
    const k = JSON.stringify(key)
    let status = ''
    if (prevObj && !prev.has(k)) status = 'is-new'
    else if (prevObj && prev.get(k) !== JSON.stringify(value)) status = 'is-changed'
    return { key, value, k, status }
  })
  const keyState = (key) => {
    const k = JSON.stringify(key)
    const s = keyStates.get(k)
    return [s && `is-${s}`, aiKeys.has(k) && 'is-ai'].filter(Boolean).join(' ') || null
  }
  const checkedMissing = [...keyStates.entries()].filter(([k, s]) => s === 'check' && !entries.some((e) => e.k === k))

  return (
    <div className="hashmap">
      <ModeToggle mode={mode} setMode={setMode} />
      {mode === 'table' ? (
        <div className="kv">
          <div className="kv-head">
            <span>key</span>
            <span>value</span>
          </div>
          <AnimatePresence initial={false}>
            {entries.map((e) => (
              <motion.div
                key={e.k}
                layout
                className={`kv-row ${e.status} ${keyState(e.key) ?? ''}`}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 16 }}
                transition={spring}
              >
                <span className="kv-key">{fmt(e.key, heap)}</span>
                <span className="kv-value">
                  <InlineValue value={e.value} heap={heap} />
                </span>
              </motion.div>
            ))}
          </AnimatePresence>
          {!entries.length && <div className="empty">empty</div>}
        </div>
      ) : (
        <Buckets
          entries={entries}
          heap={heap}
          keyState={keyState}
          renderValue={(v) => <InlineValue value={v} heap={heap} />}
        />
      )}
      {checkedMissing.map(([k]) => (
        <div key={k} className="lookup-miss">
          looking up {fmt(JSON.parse(k), heap)} → not found
        </div>
      ))}
    </div>
  )
}

export function SetView({ obj, heap, prevObj, keyStates, aiKeys = new Set() }) {
  const [mode, setMode] = useState('table')
  const prev = new Set((prevObj?.items ?? []).map((x) => JSON.stringify(x)))
  const keyState = (key) => {
    const k = JSON.stringify(key)
    const s = keyStates.get(k)
    return [s && `is-${s}`, aiKeys.has(k) && 'is-ai'].filter(Boolean).join(' ') || null
  }
  const items = obj.items.map((key) => ({ key, k: JSON.stringify(key) }))
  const checkedMissing = [...keyStates.entries()].filter(([k, s]) => s === 'check' && !items.some((e) => e.k === k))
  return (
    <div className="set">
      <ModeToggle mode={mode} setMode={setMode} />
      {mode === 'table' ? (
        <div className="set-chips">
          <AnimatePresence initial={false}>
            {items.map((e) => (
              <motion.span
                key={e.k}
                layout
                className={`set-chip ${prevObj && !prev.has(e.k) ? 'is-new' : ''} ${keyState(e.key) ?? ''}`}
                initial={{ opacity: 0, scale: 0.4 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.4 }}
                transition={spring}
              >
                {fmt(e.key, heap, { raw: true })}
              </motion.span>
            ))}
          </AnimatePresence>
          {!items.length && <div className="empty">empty set</div>}
        </div>
      ) : (
        <Buckets entries={items} heap={heap} keyState={keyState} />
      )}
      {checkedMissing.map(([k]) => (
        <div key={k} className="lookup-miss">
          checking {fmt(JSON.parse(k), heap)} → not in set
        </div>
      ))}
    </div>
  )
}
