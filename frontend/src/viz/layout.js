// Positions for node diagrams. Every layout returns
// { pos: Map(id -> {x, y}), width, height } in SVG pixels.

const PAD = 30

function finish(pos, dx, dy, pad = PAD) {
  let maxX = 0
  let maxY = 0
  for (const p of pos.values()) {
    p.x = pad + p.x * dx
    p.y = pad + p.y * dy
    maxX = Math.max(maxX, p.x)
    maxY = Math.max(maxY, p.y)
  }
  return { pos, width: maxX + pad, height: maxY + pad }
}

/** Leaves get consecutive columns; parents sit centred over their children. */
export function layoutForest(roots, childrenOf, { dx = 56, dy = 64 } = {}) {
  const pos = new Map()
  const seen = new Set()
  let col = 0
  const visit = (id, depth) => {
    if (seen.has(id)) return null
    seen.add(id)
    const kids = childrenOf(id)
      .map((c) => visit(c, depth + 1))
      .filter((x) => x !== null)
    const x = kids.length ? (kids[0] + kids[kids.length - 1]) / 2 : col++
    pos.set(id, { x, y: depth })
    return x
  }
  for (const r of roots) {
    if (visit(r, 0) !== null) col += 0.5
  }
  return finish(pos, dx, dy)
}

/** Binary trees: x = in-order position, so left children stay on the left. */
export function layoutBinary(roots, leftRight, { dx = 46, dy = 62 } = {}) {
  const pos = new Map()
  const seen = new Set()
  let col = 0
  const visit = (id, depth) => {
    if (id == null || seen.has(id)) return
    seen.add(id)
    const [l, r] = leftRight(id)
    visit(l, depth + 1)
    pos.set(id, { x: col++, y: depth })
    visit(r, depth + 1)
  }
  for (const r of roots) {
    visit(r, 0)
    col += 0.6
  }
  return finish(pos, dx, dy)
}

/** Linked lists: one row per chain, following `next` from each head. */
export function layoutChains(ids, nextOf, { dx = 86, dy = 74 } = {}) {
  const all = new Set(ids)
  const incoming = new Set()
  for (const id of ids) {
    const n = nextOf(id)
    if (n != null && all.has(n)) incoming.add(n)
  }
  const pos = new Map()
  let row = 0
  const walk = (start) => {
    let col = 0
    let id = start
    while (id != null && all.has(id) && !pos.has(id)) {
      pos.set(id, { x: col++, y: row })
      id = nextOf(id)
    }
    row++
  }
  ids.filter((id) => !incoming.has(id)).forEach(walk)
  ids.filter((id) => !pos.has(id)).forEach(walk) // pure cycles have no head
  return finish(pos, dx, dy, 34)
}

/** Nodes evenly spaced around a circle. */
export function layoutCircle(ids, { min = 70 } = {}) {
  const n = ids.length
  const radius = Math.max(min, n * 13)
  const pos = new Map()
  ids.forEach((id, i) => {
    const angle = -Math.PI / 2 + (2 * Math.PI * i) / Math.max(n, 1)
    pos.set(id, {
      x: PAD + radius + radius * Math.cos(angle),
      y: PAD + radius + radius * Math.sin(angle),
    })
  })
  const size = 2 * (PAD + radius)
  return { pos, width: size, height: size }
}

/** Point on the border of a circle of radius r centred at a, towards b. */
export function edgePoint(a, b, r) {
  const dx = b.x - a.x
  const dy = b.y - a.y
  const len = Math.hypot(dx, dy) || 1
  return { x: a.x + (dx / len) * r, y: a.y + (dy / len) * r }
}
