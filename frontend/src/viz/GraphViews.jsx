import { motion } from 'framer-motion'
import { useId } from 'react'
import { MARKER_SOLID, pointerColor } from './colors.js'
import { edgePoint, layoutBinary, layoutCircle, layoutForest } from './layout.js'
import { accessedKeys, aiKeys, aiPositions, fmt, isPrimitive, isRef, isTuple } from './model.js'

const spring = { type: 'spring', stiffness: 260, damping: 30 }
const R = 18

const NODE_VAR_RE =
  /^(node|c|course|curr|cur|u|v|src|dst|airport|ch|nei|nxt|pre|word|a|b|ra|rb|x|i|j|neighbor|city|prev|parent|start|k|root)$/

function Defs({ id }) {
  return (
    <defs>
      <marker id={`${id}-a`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" className="arrow-head" />
      </marker>
      <marker id={`${id}-hot`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" className="arrow-head is-hot" />
      </marker>
    </defs>
  )
}

function shortText(t, max = 7) {
  return t.length > max ? `${t.slice(0, max - 1)}…` : t
}

/** Primitive locals in the current frame whose value is a node of this graph. */
function nodePointers(scene, keySet) {
  const labels = {}
  for (const [name, v] of Object.entries(scene.top?.locals ?? {})) {
    if (!isPrimitive(v) || !NODE_VAR_RE.test(name)) continue
    const k = JSON.stringify(v)
    if (keySet.has(k)) (labels[k] ||= []).push(name)
  }
  return labels
}

/** Sets / dicts whose items are nodes of this graph (seen, visiting, dist, ...). */
function nodeMarkers(scene, keySet, ownId) {
  const out = []
  for (const s of scene.structures) {
    if (s.id === ownId || !['set', 'hashmap'].includes(s.kind)) continue
    const members = new Map()
    if (s.kind === 'set') {
      for (const item of s.obj.items) if (keySet.has(JSON.stringify(item))) members.set(JSON.stringify(item), null)
    } else {
      for (const [k, v] of s.obj.entries) {
        if (keySet.has(JSON.stringify(k))) members.set(JSON.stringify(k), isRef(v) ? null : fmt(v, scene.heap))
      }
    }
    if (members.size) out.push({ name: s.names[0], members, color: MARKER_SOLID[out.length % MARKER_SOLID.length] })
  }
  return out
}

/** dict adjacency list -> circle graph. Weighted edges come from (node, w) tuples. */
export function AdjacencyGraph({ obj, scene, names, id }) {
  const uid = useId().replace(/:/g, '')
  const heap = scene.heap
  const keys = []
  const keySet = new Set()
  const addKey = (v) => {
    const k = JSON.stringify(v)
    if (!keySet.has(k)) {
      keySet.add(k)
      keys.push({ k, v })
    }
  }
  const edges = []
  for (const [key, val] of obj.entries) {
    addKey(key)
    for (const item of heap[val.id]?.items ?? []) {
      const target = isTuple(item) ? item.items[0] : item
      const weight = isTuple(item) && item.items.length > 1 ? fmt(item.items[1], heap) : null
      addKey(target)
      edges.push({ from: JSON.stringify(key), to: JSON.stringify(target), weight })
    }
  }
  const edgeSet = new Set(edges.map((e) => `${e.from}>${e.to}`))
  const shown = edges.filter((e) => !(edgeSet.has(`${e.to}>${e.from}`) && e.from > e.to && !e.weight))
  const { pos, width, height } = layoutCircle(keys.map((k) => k.k), { min: 60 })
  const labels = nodePointers(scene, keySet)
  const markers = nodeMarkers(scene, keySet, id)
  const hot = accessedKeys(scene, names)
  const ai = aiKeys(scene, names)

  return (
    <div>
      <div className="diagram-scroll">
        <svg className="diagram" width={width} height={height}>
          <Defs id={uid} />
          {shown.map((e, i) => {
            const mutual = edgeSet.has(`${e.to}>${e.from}`) && !e.weight
            const a = edgePoint(pos.get(e.from), pos.get(e.to), R)
            const b = edgePoint(pos.get(e.to), pos.get(e.from), R + 2)
            const isHot = hot.has(e.from)
            return (
              <g key={i}>
                <line
                  x1={a.x}
                  y1={a.y}
                  x2={b.x}
                  y2={b.y}
                  className={`edge ${isHot ? 'is-hot' : ''}`}
                  markerEnd={mutual ? undefined : `url(#${uid}-${isHot ? 'hot' : 'a'})`}
                />
                {e.weight && (
                  <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 4} className="edge-label" textAnchor="middle">
                    {e.weight}
                  </text>
                )}
              </g>
            )
          })}
          {keys.map(({ k, v }) => {
            const p = pos.get(k)
            const marks = markers.filter((m) => m.members.has(k))
            const memo = marks.find((m) => m.members.get(k) !== null)
            return (
              <g key={k} transform={`translate(${p.x} ${p.y})`}>
                <circle
                  r={R}
                  className={`graph-node ${labels[k] ? 'is-pointed' : ''} ${hot.has(k) ? 'is-hot' : ''} ${ai.has(k) ? 'is-ai' : ''}`}
                  style={marks.length ? { fill: marks[marks.length - 1].color, fillOpacity: 0.35 } : undefined}
                />
                {marks.map((m, i) => (
                  <circle key={m.name} r={R + 3 + i * 3} className="graph-ring" style={{ stroke: m.color }} />
                ))}
                <text className="node-text" textAnchor="middle" dy="0.35em">
                  {shortText(fmt(v, heap, { raw: true }), 5)}
                </text>
                {memo && (
                  <text className="node-memo" textAnchor="middle" y={-R - 6}>
                    {memo.members.get(k)}
                  </text>
                )}
                {labels[k] && (
                  <text className="node-ptr" textAnchor="middle" y={R + 14} fill={pointerColor(labels[k][0])}>
                    {labels[k].join(', ')}
                  </text>
                )}
              </g>
            )
          })}
        </svg>
      </div>
      {markers.length > 0 && (
        <div className="legend">
          {markers.map((m) => (
            <span key={m.name}>
              <i style={{ background: m.color }} /> in {m.name}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

/** parent[] array drawn as a forest: each node points up at its parent. */
export function UnionFindForest({ items, ints, aiIndexes = [] }) {
  const uid = useId().replace(/:/g, '')
  const n = items.length
  // Node i is parent[i], so Gemini's list indices apply directly
  const ai = aiPositions(aiIndexes, n)
  const children = Array.from({ length: n }, () => [])
  const roots = []
  items.forEach((p, i) => (p === i ? roots.push(i) : children[p]?.push(i)))
  const { pos, width, height } = layoutForest(roots, (i) => children[i], { dx: 46, dy: 58 })
  const labels = {}
  for (const [name, v] of Object.entries(ints)) {
    if (/^(x|a|b|ra|rb|root|i)$/.test(name) && v >= 0 && v < n) (labels[v] ||= []).push(name)
  }
  return (
    <div className="diagram-scroll">
      <svg className="diagram" width={width} height={height + 16}>
        <Defs id={uid} />
        {items.map((p, i) => {
          if (p === i || !pos.has(i) || !pos.has(p)) return null
          const a = edgePoint(pos.get(i), pos.get(p), 15)
          const b = edgePoint(pos.get(p), pos.get(i), 17)
          return (
            <motion.line
              key={i}
              initial={false}
              animate={{ x1: a.x, y1: a.y, x2: b.x, y2: b.y }}
              transition={spring}
              className="edge"
              markerEnd={`url(#${uid}-a)`}
            />
          )
        })}
        {[...pos.entries()].map(([i, p]) => (
          <motion.g key={i} initial={false} animate={{ x: p.x, y: p.y }} transition={spring}>
            <circle r={15} className={`graph-node ${items[i] === i ? 'is-root' : ''} ${labels[i] ? 'is-pointed' : ''} ${ai.has(i) ? 'is-ai' : ''}`} />
            <text className="node-text" textAnchor="middle" dy="0.35em">
              {i}
            </text>
            {labels[i] && (
              <text className="node-ptr" textAnchor="middle" y={28} fill={pointerColor(labels[i][0])}>
                {labels[i].join(', ')}
              </text>
            )}
          </motion.g>
        ))}
      </svg>
    </div>
  )
}

/** Heap array drawn as the binary tree it represents (children of i: 2i+1, 2i+2). */
export function HeapTree({ items, heap, aiIndexes = [] }) {
  const n = items.length
  if (!n) return null
  // Tree node i is items[i], so Gemini's list indices apply directly
  const ai = aiPositions(aiIndexes, n)
  const { pos, width, height } = layoutBinary([0], (i) => [2 * i + 1 < n ? 2 * i + 1 : null, 2 * i + 2 < n ? 2 * i + 2 : null], {
    dx: 40,
    dy: 50,
  })
  return (
    <div className="diagram-scroll">
      <svg className="diagram" width={width} height={height}>
        {items.map((_, i) => {
          if (i === 0) return null
          const parent = Math.floor((i - 1) / 2)
          const a = pos.get(parent)
          const b = pos.get(i)
          return <motion.line key={i} initial={false} animate={{ x1: a.x, y1: a.y, x2: b.x, y2: b.y }} transition={spring} className="edge" />
        })}
        {items.map((v, i) => {
          const p = pos.get(i)
          return (
            <motion.g key={i} initial={false} animate={{ x: p.x, y: p.y }} transition={spring}>
              <rect x={-19} y={-12} width={38} height={24} rx={12} className={`heap-node ${i === 0 ? 'is-top' : ''} ${ai.has(i) ? 'is-ai' : ''}`} />
              <text className="node-text small" textAnchor="middle" dy="0.35em">
                {shortText(fmt(v, heap, { raw: true }), 6)}
              </text>
            </motion.g>
          )
        })}
      </svg>
    </div>
  )
}

/** Every call made so far, as a tree. The current call path is highlighted. */
export function CallTree({ tree, aiCalls = new Set() }) {
  const { nodes, roots, active, current } = tree
  // Keep big trees readable: only the most recent calls plus the active path
  const LIMIT = 120
  let ids = [...nodes.keys()]
  if (ids.length > LIMIT) {
    const recent = new Set(ids.slice(-LIMIT))
    active.forEach((id) => recent.add(id))
    ids = ids.filter((id) => recent.has(id))
  }
  const keep = new Set(ids)
  const shownRoots = ids.filter((id) => !keep.has(nodes.get(id).parent))
  const childrenOf = (id) => nodes.get(id).children.filter((c) => keep.has(c))
  const { pos, width, height } = layoutForest(shownRoots.length ? shownRoots : roots, childrenOf, { dx: 84, dy: 58 })
  const single = new Set([...nodes.values()].map((n) => n.name)).size === 1

  return (
    <div className="diagram-scroll call-tree">
      <svg className="diagram" width={width + 40} height={height + 24}>
        {ids.flatMap((id) =>
          childrenOf(id)
            .filter((c) => pos.has(c) && pos.has(id))
            .map((c) => {
              const a = pos.get(id)
              const b = pos.get(c)
              return (
                <line
                  key={`${id}-${c}`}
                  x1={a.x}
                  y1={a.y + 13}
                  x2={b.x}
                  y2={b.y - 13}
                  className={`edge ${active.has(c) ? 'is-hot' : 'is-dim'}`}
                />
              )
            }),
        )}
        {ids.map((id) => {
          const p = pos.get(id)
          if (!p) return null
          const node = nodes.get(id)
          const label = single ? node.label.slice(node.name.length) : node.label
          return (
            <g key={id} transform={`translate(${p.x} ${p.y})`}>
              <rect
                x={-40}
                y={-13}
                width={80}
                height={26}
                rx={6}
                className={`call-node ${active.has(id) ? 'is-active' : ''} ${current === id ? 'is-current' : ''} ${node.retText !== null ? 'is-done' : ''} ${aiCalls.has(id) ? 'is-ai' : ''}`}
              />
              <text className="node-text small" textAnchor="middle" dy="0.35em">
                {shortText(label, 13)}
              </text>
              {node.retText !== null && (
                <text className="call-ret" textAnchor="middle" y={25}>
                  → {shortText(node.retText, 10)}
                </text>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}
