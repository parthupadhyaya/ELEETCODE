import { motion } from 'framer-motion'
import { useId } from 'react'
import { pointerColor } from './colors.js'
import { edgePoint, layoutBinary, layoutChains, layoutCircle, layoutForest } from './layout.js'
import { fmt, isRef, nodeText } from './model.js'

const spring = { type: 'spring', stiffness: 260, damping: 30 }

const refId = (v) => (isRef(v) ? v.id : null)

function ArrowDefs({ id }) {
  return (
    <defs>
      <marker id={`${id}-arrow`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" className="arrow-head" />
      </marker>
      <marker id={`${id}-arrow-dim`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" className="arrow-head is-dim" />
      </marker>
    </defs>
  )
}

/** Variable names stacked under a node, each in its pointer colour. */
function Labels({ x, y, names }) {
  if (!names?.length) return null
  return (
    <motion.g initial={false} animate={{ x, y }} transition={spring}>
      <text className="node-ptr-arrow" textAnchor="middle" y={0}>▲</text>
      {names.map((n, i) => (
        <text key={n} className="node-ptr" textAnchor="middle" y={13 + i * 13} fill={pointerColor(n)}>
          {n}
        </text>
      ))}
    </motion.g>
  )
}

function Svg({ width, height, children, className = '' }) {
  return (
    <div className="diagram-scroll">
      <svg className={`diagram ${className}`} width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        {children}
      </svg>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Linked lists
// ---------------------------------------------------------------------------

const LW = 56
const LH = 30

export function LinkedListDiagram({ nodes, labels, changed, aiNodes = new Set() }) {
  const uid = useId().replace(/:/g, '')
  const ids = nodes.map((n) => n.id).sort((a, b) => a - b)
  const byId = new Map(nodes.map((n) => [n.id, n.obj]))
  const nextOf = (id) => {
    const t = refId(byId.get(id)?.attrs.next)
    return t !== null && byId.has(t) ? t : null
  }
  const maxLabels = Math.max(0, ...ids.map((id) => labels[id]?.length ?? 0))
  const { pos, width, height } = layoutChains(ids, nextOf, { dy: 74 + maxLabels * 12 })

  const edges = []
  for (const id of ids) {
    const obj = byId.get(id)
    for (const [attr, v] of Object.entries(obj.attrs)) {
      const t = refId(v)
      if (t === null || !byId.has(t)) continue
      if (attr !== 'next' && !['prev', 'random'].includes(attr)) continue
      edges.push({ from: id, to: t, attr })
    }
  }

  const pathFor = ({ from, to, attr }) => {
    const a = pos.get(from)
    const b = pos.get(to)
    if (attr === 'next' && a.y === b.y && b.x > a.x) {
      const x1 = a.x + LW / 2
      const x2 = b.x - LW / 2 - 2
      return `M ${x1} ${a.y} Q ${(x1 + x2) / 2} ${a.y} ${x2} ${b.y}`
    }
    // Curves: `next` back edges (cycles) and cross-row links bend below the
    // nodes; prev/random pointers bend above them
    const bend = 26 + Math.abs(a.x - b.x) * 0.12
    if (attr === 'next') {
      const y1 = a.y + LH / 2
      const y2 = b.y + LH / 2 + 2
      return `M ${a.x} ${y1} Q ${(a.x + b.x) / 2} ${Math.max(y1, y2) + bend} ${b.x} ${y2}`
    }
    const y1 = a.y - LH / 2
    const y2 = b.y - LH / 2 - 2
    return `M ${a.x} ${y1} Q ${(a.x + b.x) / 2} ${Math.min(y1, y2) - bend} ${b.x} ${y2}`
  }

  const topPad = edges.some((e) => e.attr !== 'next') ? 44 : 0

  return (
    <Svg width={width + 40} height={height + maxLabels * 12 + 10 + topPad}>
      <ArrowDefs id={uid} />
      <g transform={`translate(0 ${topPad})`}>
      {edges.map((e) => (
        <motion.path
          key={`${e.from}-${e.attr}`}
          initial={false}
          animate={{ d: pathFor(e) }}
          transition={spring}
          className={`edge ${e.attr !== 'next' ? 'is-dim' : ''}`}
          markerEnd={`url(#${uid}-${e.attr !== 'next' ? 'arrow-dim' : 'arrow'})`}
        />
      ))}
      {ids.map((id) => {
        const p = pos.get(id)
        const obj = byId.get(id)
        const isNone = 'next' in obj.attrs && obj.attrs.next === null
        return (
          <motion.g key={id} initial={false} animate={{ x: p.x, y: p.y }} transition={spring}>
            <rect
              x={-LW / 2}
              y={-LH / 2}
              width={LW}
              height={LH}
              rx={7}
              className={`list-node ${changed.has(id) ? 'is-changed' : ''} ${labels[id]?.length ? 'is-pointed' : ''} ${aiNodes.has(id) ? 'is-ai' : ''}`}
            />
            <text className="node-text" textAnchor="middle" dy="0.35em">
              {nodeText(obj)}
            </text>
            {isNone && (
              <text className="none-text" x={LW / 2 + 6} dy="0.35em">
                → ∅
              </text>
            )}
          </motion.g>
        )
      })}
      {ids.map((id) => {
        const p = pos.get(id)
        return <Labels key={id} x={p.x} y={p.y + LH / 2 + 10} names={labels[id]} />
      })}
      </g>
    </Svg>
  )
}

// ---------------------------------------------------------------------------
// Binary trees
// ---------------------------------------------------------------------------

const TR = 17

export function TreeDiagram({ nodes, labels, changed, aiNodes = new Set() }) {
  const byId = new Map(nodes.map((n) => [n.id, n.obj]))
  const child = (id, side) => {
    const t = refId(byId.get(id)?.attrs[side])
    return t !== null && byId.has(t) ? t : null
  }
  const childIds = new Set()
  for (const id of byId.keys()) {
    for (const side of ['left', 'right']) {
      const c = child(id, side)
      if (c !== null) childIds.add(c)
    }
  }
  const roots = [...byId.keys()].filter((id) => !childIds.has(id)).sort((a, b) => a - b)
  const maxLabels = Math.max(0, ...[...byId.keys()].map((id) => labels[id]?.length ?? 0))
  const { pos, width, height } = layoutBinary(roots, (id) => [child(id, 'left'), child(id, 'right')], {
    dy: 62 + Math.min(maxLabels, 2) * 8,
  })

  const edges = []
  for (const id of byId.keys()) {
    for (const side of ['left', 'right']) {
      const c = child(id, side)
      if (c !== null && pos.has(id) && pos.has(c)) edges.push({ from: id, to: c, side })
    }
  }

  return (
    <Svg width={width} height={height + 20 + maxLabels * 13}>
      {edges.map((e) => {
        const a = edgePoint(pos.get(e.from), pos.get(e.to), TR)
        const b = edgePoint(pos.get(e.to), pos.get(e.from), TR)
        return (
          <motion.line
            key={`${e.from}-${e.side}`}
            initial={false}
            animate={{ x1: a.x, y1: a.y, x2: b.x, y2: b.y }}
            transition={spring}
            className="edge"
          />
        )
      })}
      {[...pos.entries()].map(([id, p]) => (
        <motion.g key={id} initial={false} animate={{ x: p.x, y: p.y }} transition={spring}>
          <circle
            r={TR}
            className={`tree-node ${changed.has(id) ? 'is-changed' : ''} ${labels[id]?.length ? 'is-pointed' : ''} ${aiNodes.has(id) ? 'is-ai' : ''}`}
          />
          <text className="node-text" textAnchor="middle" dy="0.35em">
            {nodeText(byId.get(id))}
          </text>
        </motion.g>
      ))}
      {[...pos.entries()].map(([id, p]) => (
        <Labels key={id} x={p.x} y={p.y + TR + 10} names={labels[id]} />
      ))}
    </Svg>
  )
}

// ---------------------------------------------------------------------------
// Tries
// ---------------------------------------------------------------------------

export function TrieDiagram({ nodes, labels, heap, changed, aiNodes = new Set() }) {
  const byId = new Map(nodes.map((n) => [n.id, n.obj]))
  const childrenOf = (id) => {
    const dict = heap[refId(byId.get(id)?.attrs.children)]
    if (!dict?.entries) return []
    return dict.entries
      .map(([k, v]) => ({ ch: fmt(k, null, { raw: true }), id: refId(v) }))
      .filter((c) => c.id !== null && byId.has(c.id))
  }
  const childIds = new Set()
  for (const id of byId.keys()) childrenOf(id).forEach((c) => childIds.add(c.id))
  const roots = [...byId.keys()].filter((id) => !childIds.has(id)).sort((a, b) => a - b)
  const { pos, width, height } = layoutForest(roots, (id) => childrenOf(id).map((c) => c.id), { dx: 42, dy: 56 })

  const isEnd = (obj) => obj.attrs.end === true || (obj.attrs.word && obj.attrs.word !== null)

  return (
    <Svg width={width + 20} height={height + 40}>
      {[...pos.keys()].flatMap((id) =>
        childrenOf(id)
          .filter((c) => pos.has(c.id))
          .map((c) => {
            const a = pos.get(id)
            const b = pos.get(c.id)
            const p1 = edgePoint(a, b, 11)
            const p2 = edgePoint(b, a, 11)
            return (
              <g key={`${id}-${c.ch}`}>
                <motion.line initial={false} animate={{ x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y }} transition={spring} className="edge" />
                <motion.text
                  initial={false}
                  animate={{ x: (a.x + b.x) / 2 - 7, y: (a.y + b.y) / 2 }}
                  transition={spring}
                  className="edge-label"
                  textAnchor="middle"
                >
                  {c.ch}
                </motion.text>
              </g>
            )
          }),
      )}
      {[...pos.entries()].map(([id, p]) => {
        const obj = byId.get(id)
        const word = obj.attrs.word
        return (
          <motion.g key={id} initial={false} animate={{ x: p.x, y: p.y }} transition={spring}>
            <circle
              r={11}
              className={`trie-node ${isEnd(obj) ? 'is-end' : ''} ${changed.has(id) ? 'is-changed' : ''} ${labels[id]?.length ? 'is-pointed' : ''} ${aiNodes.has(id) ? 'is-ai' : ''}`}
            />
            {word && word.t === 'str' && (
              <text className="trie-word" textAnchor="middle" y={24}>
                {word.v}
              </text>
            )}
          </motion.g>
        )
      })}
      {[...pos.entries()].map(([id, p]) => (
        <Labels key={id} x={p.x + 18} y={p.y - 4} names={labels[id]} />
      ))}
    </Svg>
  )
}

// ---------------------------------------------------------------------------
// Graph nodes with `neighbors` lists (Clone Graph)
// ---------------------------------------------------------------------------

export function NodeGraphDiagram({ nodes, labels, heap, changed, aiNodes = new Set() }) {
  const uid = useId().replace(/:/g, '')
  const byId = new Map(nodes.map((n) => [n.id, n.obj]))
  const neighbors = (id) => (heap[refId(byId.get(id)?.attrs.neighbors)]?.items ?? []).map(refId).filter((t) => byId.has(t))

  // Lay out each connected component as its own circle, side by side
  const comp = new Map()
  for (const start of [...byId.keys()].sort((a, b) => a - b)) {
    if (comp.has(start)) continue
    const stack = [start]
    while (stack.length) {
      const id = stack.pop()
      if (comp.has(id)) continue
      comp.set(id, start)
      for (const n of neighbors(id)) stack.push(n)
      for (const [other] of byId) if (neighbors(other).includes(id)) stack.push(other)
    }
  }
  const groups = [...new Set(comp.values())].map((root) => [...comp.keys()].filter((id) => comp.get(id) === root))
  const pos = new Map()
  let offset = 0
  let height = 0
  for (const g of groups) {
    const lay = layoutCircle(g, { min: 50 })
    for (const [id, p] of lay.pos) pos.set(id, { x: p.x + offset, y: p.y })
    offset += lay.width
    height = Math.max(height, lay.height)
  }

  const edges = []
  for (const id of byId.keys()) {
    for (const t of neighbors(id)) {
      const mutual = neighbors(t).includes(id)
      if (mutual && t < id) continue
      edges.push({ from: id, to: t, mutual })
    }
  }

  return (
    <Svg width={offset} height={height + 20}>
      <ArrowDefs id={uid} />
      {edges.map((e) => {
        const a = edgePoint(pos.get(e.from), pos.get(e.to), 17)
        const b = edgePoint(pos.get(e.to), pos.get(e.from), 19)
        return (
          <line
            key={`${e.from}-${e.to}`}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            className="edge"
            markerEnd={e.mutual ? undefined : `url(#${uid}-arrow)`}
          />
        )
      })}
      {[...pos.entries()].map(([id, p]) => (
        <g key={id} transform={`translate(${p.x} ${p.y})`}>
          <circle r={17} className={`tree-node ${changed.has(id) ? 'is-changed' : ''} ${labels[id]?.length ? 'is-pointed' : ''} ${aiNodes.has(id) ? 'is-ai' : ''}`} />
          <text className="node-text" textAnchor="middle" dy="0.35em">
            {nodeText(byId.get(id))}
          </text>
          <text className="node-id" textAnchor="middle" y={-22}>
            #{id}
          </text>
        </g>
      ))}
      {[...pos.entries()].map(([id, p]) => (
        <Labels key={id} x={p.x} y={p.y + 27} names={labels[id]} />
      ))}
    </Svg>
  )
}
