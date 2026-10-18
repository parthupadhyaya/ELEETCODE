// Turns one trace step (from backend/runner.py) into what the visualizer
// draws: primitive variables, data-structure cards, node diagrams, pointer
// arrows, the cells the current line touches, and a plain-English summary.
//
// Value encoding from the runner:
//   number | boolean | null                  plain JSON
//   {t:'str', v}  {t:'num', v:'inf'}          strings / non-finite numbers
//   {t:'tuple', items}                        tuples (inline, immutable)
//   {t:'ref', id}                             points into step.heap[id]
// Heap objects: {t:'list'|'deque'|'set', items, len}, {t:'dict', entries, len, cls},
//               {t:'obj', cls, attrs}, {t:'other', v}

export const INF_INT = 2147483647

export const isRef = (v) => v !== null && typeof v === 'object' && v.t === 'ref'
export const isTuple = (v) => v !== null && typeof v === 'object' && v.t === 'tuple'
export const isInt = (v) => typeof v === 'number' && Number.isInteger(v)
export const isPrimitive = (v) => !isRef(v) && !isTuple(v)

/** Primitive encoded value -> JS value for comparisons. */
export function plain(v) {
  if (v === null || typeof v !== 'object') return v
  if (v.t === 'str') return v.v
  if (v.t === 'num') return v.v === 'inf' ? Infinity : v.v === '-inf' ? -Infinity : Number(v.v)
  if (v.t === 'tuple') return v.items.map(plain)
  return undefined
}

export const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)

export function fmtNumber(n) {
  if (n === INF_INT) return '∞'
  if (Number.isInteger(n)) return String(n)
  return String(Math.round(n * 1e4) / 1e4)
}

/** Python-ish text for any encoded value. `raw` drops quotes around strings. */
export function fmt(v, heap, { raw = false, depth = 0 } = {}) {
  if (v === null || v === undefined) return 'None'
  if (v === true) return 'True'
  if (v === false) return 'False'
  if (typeof v === 'number') return fmtNumber(v)
  switch (v.t) {
    case 'str':
      return raw ? v.v : `'${v.v}'`
    case 'num':
      return v.v === 'inf' ? '∞' : v.v === '-inf' ? '-∞' : v.v
    case 'tuple': {
      const inner = v.items.map((x) => fmt(x, heap, { depth: depth + 1 })).join(', ')
      return `(${inner}${v.items.length === 1 ? ',' : ''})`
    }
    case 'fn':
      return `ƒ ${v.v}`
    case 'other':
      return v.v
    case 'ref':
      return fmtObject(heap?.[v.id], heap, depth)
    default:
      return '?'
  }
}

function joinItems(items, len, heap, depth, max = 8) {
  const shown = items.slice(0, max).map((x) => fmt(x, heap, { depth: depth + 1 }))
  if (len > max) shown.push('…')
  return shown.join(', ')
}

function fmtObject(obj, heap, depth) {
  if (!obj) return '…'
  if (nodeKind(obj)) return `${obj.cls}(${nodeText(obj)})`
  if (depth >= 2) return obj.t === 'dict' ? '{…}' : obj.t === 'obj' ? obj.cls : '[…]'
  switch (obj.t) {
    case 'list':
      return `[${joinItems(obj.items, obj.len, heap, depth)}]`
    case 'deque':
      return `deque([${joinItems(obj.items, obj.len, heap, depth)}])`
    case 'set':
      return obj.len ? `{${joinItems(obj.items, obj.len, heap, depth)}}` : 'set()'
    case 'dict': {
      const shown = obj.entries
        .slice(0, 5)
        .map(([k, v]) => `${fmt(k, heap, { depth: depth + 1 })}: ${fmt(v, heap, { depth: depth + 1 })}`)
      if (obj.len > 5) shown.push('…')
      return `{${shown.join(', ')}}`
    }
    case 'obj':
      return obj.cls
    default:
      return obj.v ?? '?'
  }
}

// ---------------------------------------------------------------------------
// Node objects (linked lists, trees, tries, graphs)
// ---------------------------------------------------------------------------

export function nodeKind(obj) {
  if (!obj || obj.t !== 'obj') return null
  const a = obj.attrs
  if ('next' in a && ('val' in a || 'key' in a)) return 'list'
  if (('left' in a || 'right' in a) && 'val' in a) return 'tree'
  if ('children' in a) return 'trie'
  if ('neighbors' in a) return 'graph'
  return null
}

export function nodeText(obj) {
  const a = obj.attrs
  if ('key' in a && 'val' in a) return `${fmt(a.key, null, { raw: true })}:${fmt(a.val, null, { raw: true })}`
  if ('val' in a) return fmt(a.val, null, { raw: true })
  return ''
}

// ---------------------------------------------------------------------------
// Classifying containers
// ---------------------------------------------------------------------------

const isNumeric = (v) => typeof v === 'number' || (v && v.t === 'num')

function pairOf(v, heap) {
  if (isTuple(v)) return v.items
  if (isRef(v) && heap[v.id]?.t === 'list') return heap[v.id].items
  return null
}

function looksLikeIntervals(obj, heap, name) {
  if (!/interval|meeting|merged|^res$|output|^ans$/i.test(name)) return false
  if (!obj.items.length) return false
  return obj.items.every((v) => {
    const p = pairOf(v, heap)
    return p && p.length === 2 && isNumeric(p[0]) && isNumeric(p[1]) && plain(p[0]) <= plain(p[1])
  })
}

function looksLikeGrid(obj, heap) {
  if (!obj.items.length) return false
  return obj.items.every((v) => {
    if (!isRef(v)) return false
    const row = heap[v.id]
    return row && row.t === 'list' && row.items.every(isPrimitive)
  })
}

function looksLikeGraph(obj, heap, name) {
  if (!obj.entries.length || !obj.entries.every(([k]) => isPrimitive(k))) return false
  const keys = new Set(obj.entries.map(([k]) => JSON.stringify(k)))
  let total = 0
  let hits = 0
  for (const [, v] of obj.entries) {
    if (!isRef(v)) return false
    const c = heap[v.id]
    if (!c || !['list', 'set', 'deque'].includes(c.t)) return false
    for (const item of c.items) {
      const target = isTuple(item) ? item.items[0] : item
      if (!isPrimitive(target)) return false
      total += 1
      if (keys.has(JSON.stringify(target))) hits += 1
    }
  }
  if (/graph|adj|neighbou?rs|edges/i.test(name)) return true
  return total > 0 && hits / total >= 0.5
}

/** Which view to draw a heap object with. */
export function classify(obj, heap, name) {
  if (!obj) return 'missing'
  if (nodeKind(obj)) return 'node'
  const prims = obj.items?.every(isPrimitive)
  switch (obj.t) {
    case 'list':
      if (looksLikeIntervals(obj, heap, name)) return 'intervals'
      if (looksLikeGrid(obj, heap)) return 'grid'
      if (/heap|^pq$|^small$|^large$/i.test(name)) return 'heap'
      if (/stack/i.test(name)) return 'stack'
      if (/^q$|queue/i.test(name)) return 'queue'
      if (
        prims &&
        obj.len > 1 &&
        /^(parent|par|parents|root|roots|leader)$/i.test(name) &&
        obj.items.every((v) => isInt(v) && v >= 0 && v < obj.len)
      )
        return 'unionfind'
      return 'array'
    case 'deque':
      return 'queue'
    case 'set':
      return 'set'
    case 'dict':
      return looksLikeGraph(obj, heap, name) ? 'graph' : 'hashmap'
    case 'obj':
      return 'object'
    default:
      return 'other'
  }
}

// ---------------------------------------------------------------------------
// Pointers: integer variables that index into an array/string
// ---------------------------------------------------------------------------

const POINTER_RE =
  /^(i|j|l|r|s|e|c|lo|hi|low|high|mid|left|right|start|end|begin|slow|fast|slow2|idx|index|ptr|pos|cur|curr|prev|nxt|goal|center|first|last|head|tail|pivot|read|write|pre_i|best_l|best_r|i\d|j\d|.+_(i|idx|index|ptr|pos))$/

const WINDOW_PAIRS = [
  ['l', 'r'],
  ['left', 'right'],
  ['lo', 'hi'],
  ['low', 'high'],
  ['start', 'end'],
  ['best_l', 'best_r'],
]

export const GRID_PAIRS = [
  ['r', 'c'],
  ['row', 'col'],
  ['i', 'j'],
]
const GRID_SECONDARY = [['nr', 'nc']]

export function pointersFor(length, ints) {
  const out = []
  for (const [name, value] of Object.entries(ints)) {
    if (POINTER_RE.test(name) && value >= 0 && value < length) out.push({ name, index: value })
  }
  return out
}

export function windowFor(length, ints) {
  for (const [a, b] of WINDOW_PAIRS) {
    const lo = ints[a]
    const hi = ints[b]
    if (isInt(lo) && isInt(hi) && lo <= hi && lo >= 0 && hi < length) return [lo, hi]
  }
  return null
}

export function gridCursor(rows, cols, ints) {
  const find = (pairs) => {
    for (const [a, b] of pairs) {
      const r = ints[a]
      const c = ints[b]
      if (isInt(r) && isInt(c) && r >= 0 && r < rows && c >= 0 && c < cols) return { r, c, label: `${a},${b}` }
    }
    return null
  }
  return { primary: find(GRID_PAIRS), secondary: find(GRID_SECONDARY) }
}

// ---------------------------------------------------------------------------
// Which cells does the current line read or write? (e.g. dp[i + 1][j])
// ---------------------------------------------------------------------------

function tokenize(expr) {
  const tokens = []
  const re = /\s*(\/\/|\d+|[A-Za-z_]\w*|[-+*%()])/y
  let m
  let pos = 0
  while (pos < expr.length) {
    re.lastIndex = pos
    m = re.exec(expr)
    if (!m) {
      if (/^\s*$/.test(expr.slice(pos))) break
      return null
    }
    tokens.push(m[1])
    pos = re.lastIndex
  }
  return tokens
}

/** Evaluates simple integer index expressions like "i + 1" or "(l + r) // 2". */
export function evalIndex(expr, ints) {
  const tokens = tokenize(expr)
  if (!tokens || !tokens.length) return null
  let i = 0
  const peek = () => tokens[i]
  const next = () => tokens[i++]
  const atom = () => {
    const t = next()
    if (t === undefined) throw new Error('eof')
    if (t === '(') {
      const v = sum()
      if (next() !== ')') throw new Error('paren')
      return v
    }
    if (t === '-') return -atom()
    if (/^\d+$/.test(t)) return Number(t)
    if (/^[A-Za-z_]\w*$/.test(t) && isInt(ints[t])) return ints[t]
    throw new Error('unknown')
  }
  const product = () => {
    let v = atom()
    while (['*', '//', '%'].includes(peek())) {
      const op = next()
      const rhs = atom()
      if (op === '*') v *= rhs
      else if (rhs === 0) throw new Error('div0')
      else if (op === '//') v = Math.floor(v / rhs)
      else v = ((v % rhs) + rhs) % rhs
    }
    return v
  }
  const sum = () => {
    let v = product()
    while (peek() === '+' || peek() === '-') v = next() === '+' ? v + product() : v - product()
    return v
  }
  try {
    const v = sum()
    return i === tokens.length ? v : null
  } catch {
    return null
  }
}

/**
 * What the line about to run touches:
 *   [{name, indexes: [a] | [a, b] (null when not an int), raw, slice?, write, membership?}]
 * e.g. "dp[i][j] = dp[i + 1][j]" or "if diff in seen:".
 */
export function lineAccesses(lineText, ints) {
  if (!lineText) return []
  const code = lineText.replace(/#.*$/, '')
  const assign = code.search(/(?<![=!<>])=(?!=)|[-+*/%|&^]=/)
  const out = []
  const re = /([A-Za-z_][\w.]*)((?:\s*\[[^[\]]+\])+)/g
  let m
  while ((m = re.exec(code))) {
    const parts = [...m[2].matchAll(/\[([^[\]]+)\]/g)].map((x) => x[1])
    const write = assign >= 0 && m.index < assign
    if (parts.length === 1 && parts[0].includes(':')) {
      const [a, b] = parts[0].split(':')
      const lo = a.trim() ? evalIndex(a, ints) : 0
      const hi = b.trim() ? evalIndex(b, ints) : null
      if (lo !== null) out.push({ name: m[1], indexes: [], raw: parts, slice: [lo, hi], write })
      continue
    }
    out.push({ name: m[1], indexes: parts.map((p) => evalIndex(p, ints)), raw: parts, write })
  }
  // Membership tests: "x in seen", "(r, c) not in visit". Skip for-loops and
  // comprehensions, where "in" means iteration.
  if (!/^\s*for\b|\bfor\b.*\bin\b/.test(code)) {
    for (const mm of code.matchAll(/(\([^()]*\)|[A-Za-z_][\w.]*(?:\s*[-+]\s*\w+)?|\d+)\s+(?:not\s+)?in\s+([A-Za-z_][\w.]*)/g)) {
      out.push({ name: mm[2], indexes: [evalIndex(mm[1], ints)], raw: [mm[1]], write: false, membership: true })
    }
  }
  return out
}

/**
 * JSON of the encoded key an access expression refers to (to match against
 * dict keys / set items), or null. Handles names, int expressions, tuples
 * like (r, c) and string literals.
 */
export function resolveKey(raw, locals, ints) {
  const expr = raw.trim()
  if (/^\(.*,.*\)$/.test(expr)) {
    const items = expr
      .slice(1, -1)
      .split(',')
      .map((p) => p.trim())
      .filter(Boolean)
      .map((p) => evalIndex(p, ints))
    return items.every((v) => v !== null) ? JSON.stringify({ t: 'tuple', items }) : null
  }
  const lit = expr.match(/^(['"])(.*)\1$/)
  if (lit) return JSON.stringify({ t: 'str', v: lit[2] })
  if (/^[A-Za-z_]\w*$/.test(expr) && expr in locals) return JSON.stringify(locals[expr])
  const n = evalIndex(expr, ints)
  return n === null ? null : JSON.stringify(n)
}

/** Normalize a possibly-negative index against a length (Python semantics). */
export const normIndex = (i, len) => (i < 0 ? i + len : i)

// ---------------------------------------------------------------------------
// Scene
// ---------------------------------------------------------------------------

/** Names of `def` parameters, so the call tree can show f(args). */
export function functionParams(code) {
  const params = {}
  for (const m of code.matchAll(/def\s+(\w+)\s*\(([^)]*)\)/g)) {
    params[m[1]] = m[2]
      .split(',')
      .map((p) => p.split(/[:=]/)[0].trim())
      .filter((p) => p && p !== 'self' && !p.startsWith('*'))
  }
  return params
}

/**
 * Collects everything visible at this step.
 * `strCards` = string variable names that get a character-array card
 * (those indexed somewhere in the code, e.g. s[l]).
 */
export function buildScene(step, code, strCards) {
  const heap = step.heap
  const frames = step.frames
  const top = frames[frames.length - 1]
  const topLocals = top ? top.locals : {}

  // Integers in scope (top frame wins) for pointers / index expressions
  const ints = {}
  for (const f of frames) {
    for (const [k, v] of Object.entries(f.locals)) if (isInt(v)) ints[k] = v
  }
  for (const [k, v] of Object.entries(topLocals)) if (isInt(v)) ints[k] = v

  // Primitive variables of the current frame
  const vars = Object.entries(topLocals)
    .filter(([, v]) => isPrimitive(v) || isTuple(v))
    .map(([name, value]) => ({ name, value }))

  // Containers referenced from any frame (top frame names first), plus
  // containers held in attributes of `self`
  const structures = []
  const seen = new Map()
  const addStructure = (name, ref, fromTop) => {
    const obj = heap[ref.id]
    if (!obj || nodeKind(obj)) return
    if (seen.has(ref.id)) {
      const s = seen.get(ref.id)
      if (fromTop && !s.names.includes(name)) s.names.push(name)
      return
    }
    const s = { id: ref.id, names: [name], obj, kind: classify(obj, heap, name) }
    seen.set(ref.id, s)
    structures.push(s)
  }
  for (let fi = frames.length - 1; fi >= 0; fi--) {
    const f = frames[fi]
    for (const [name, v] of Object.entries(f.locals)) {
      if (isRef(v)) addStructure(name, v, fi === frames.length - 1)
    }
  }

  // String cards
  const strings = Object.entries(topLocals)
    .filter(([name, v]) => v && v.t === 'str' && strCards.has(name) && v.v.length >= 2)
    .map(([name, v]) => ({ name, value: v.v }))

  // Node diagrams: every node object reachable from anything in scope
  const nodes = collectNodes(frames, heap)
  const nodeLabels = {}
  const label = (id, name) => {
    ;(nodeLabels[id] ||= []).includes(name) || nodeLabels[id].push(name)
  }
  for (const [name, v] of Object.entries(topLocals)) {
    if (isRef(v) && nodes.has(v.id)) label(v.id, name)
    if (name === 'self' && isRef(v) && heap[v.id]?.t === 'obj') {
      for (const [attr, av] of Object.entries(heap[v.id].attrs)) {
        if (isRef(av) && nodes.has(av.id)) label(av.id, `self.${attr}`)
      }
    }
  }

  // Sets/dicts of primitives: used to colour graph nodes and grid cells
  const markers = structures.filter(
    (s) => (s.kind === 'set' || s.kind === 'hashmap') && s.obj.len > 0,
  )

  const lineText = code.split('\n')[step.line - 1] ?? ''
  const accesses = lineAccesses(lineText, ints)

  return { heap, frames, top, ints, vars, structures, strings, nodes, nodeLabels, markers, accesses, ai: NO_AI }
}

function collectNodes(frames, heap) {
  const nodes = new Map()
  const visited = new Set()
  const stack = []
  const push = (v) => {
    if (isRef(v)) stack.push(v.id)
    else if (isTuple(v)) v.items.forEach(push)
  }
  for (const f of frames) Object.values(f.locals).forEach(push)
  while (stack.length) {
    const id = stack.pop()
    if (visited.has(id)) continue
    visited.add(id)
    const obj = heap[id]
    if (!obj) continue
    const kind = nodeKind(obj)
    if (kind) nodes.set(id, { id, kind, obj })
    if (obj.items) obj.items.forEach(push)
    if (obj.entries) obj.entries.forEach(([k, v]) => (push(k), push(v)))
    if (obj.attrs) Object.values(obj.attrs).forEach(push)
  }
  return nodes
}

/** Accesses on the current line that target `name` (e.g. "nums", "self.stack"). */
export function accessesFor(scene, names) {
  return scene.accesses.filter((a) => names.includes(a.name))
}

/** Dict keys / set items the current line touches: Map(key JSON -> 'read'|'write'|'check'). */
export function accessedKeys(scene, names) {
  const keys = new Map()
  for (const a of accessesFor(scene, names)) {
    const raw = a.raw?.[0]
    if (raw === undefined || a.slice) continue
    const key = resolveKey(raw, scene.top?.locals ?? {}, scene.ints)
    if (key) keys.set(key, a.membership ? 'check' : a.write ? 'write' : 'read')
  }
  return keys
}

// ---------------------------------------------------------------------------
// Gemini's animation script (backend/gemini.py AnimationStep)
// ---------------------------------------------------------------------------

const NO_AI = { names: new Set(), cells: [], keys: [], nodes: new Set(), calls: new Set(), values: new Map() }

/**
 * Animation entries in effect at trace step `index`: the script only covers
 * steps where something meaningful happens, so the latest entry at or before
 * `index` holds until the next one. Entries sharing a trace step all apply.
 */
export function currentAnimation(animation, index) {
  const current = animation?.findLast((a) => a.trace_index <= index)
  return current ? animation.filter((a) => a.trace_index === current.trace_index) : []
}

/**
 * Trace indices worth stopping at, ascending, always including the first and
 * last step. With Gemini's script these are the steps it narrates; without it,
 * the steps where a variable, a container or the call stack just changed
 * (skipping lines that only evaluate a condition).
 */
export function keySteps(steps, animation) {
  const last = steps.length - 1
  const keep = new Set([0, last])
  if (animation?.length) {
    for (const a of animation) if (a.trace_index >= 0 && a.trace_index <= last) keep.add(a.trace_index)
  } else {
    for (let k = 1; k <= last; k++) {
      const a = steps[k - 1]
      const b = steps[k]
      if (b.event !== 'line' || a.frames.length !== b.frames.length) keep.add(k)
      else if (!same(a.frames.at(-1)?.locals, b.frames.at(-1)?.locals) || !same(a.heap, b.heap)) keep.add(k)
    }
  }
  return [...keep].sort((x, y) => x - y)
}

/**
 * What the current animation entries point at, in the scene's terms:
 *   names  target variable names
 *   cells  [{name, path}] index paths into a target ([3] or [2, 4])
 *   keys   [{name, key}] dict keys / set members as encoded-value JSON
 *   nodes  ids of node objects (ListNode, TreeNode) a target variable holds
 *   calls  frame ids (call-tree nodes) of "call" / "return" entries: the
 *          function running at the entry's trace step
 *   values target name -> the entry's `value` (a short Python literal)
 */
export function aiFocus(entries, scene, steps) {
  if (!entries.length) return NO_AI
  const locals = scene.top?.locals ?? {}
  const focus = { names: new Set(), cells: [], keys: [], nodes: new Set(), calls: new Set(), values: new Map() }
  for (const a of entries) {
    if (a.action === 'call' || a.action === 'return') {
      const frame = steps[a.trace_index]?.frames.at(-1)
      if (frame) focus.calls.add(frame.id)
    }
    if (!a.target) continue
    focus.names.add(a.target)
    if (a.value != null && !focus.values.has(a.target)) focus.values.set(a.target, a.value)
    for (const path of a.indices) focus.cells.push({ name: a.target, path })
    for (const raw of a.keys) {
      const key = resolveKey(raw, locals, scene.ints)
      if (key) focus.keys.push({ name: a.target, key })
    }
    const v = locals[a.target]
    if (isRef(v) && scene.nodes.has(v.id)) focus.nodes.add(v.id)
  }
  return focus
}

export const aiTargeted = (scene, names) => names.some((n) => scene.ai.names.has(n))

/** Gemini's value for the container known by `names`, or undefined. */
export const aiValue = (scene, names) => names.map((n) => scene.ai.values.get(n)).find((v) => v != null)

/** Where an entry's value applies, e.g. "nums[3]" or "grid[2][4]", else the bare target. */
export function aiWhere(entry) {
  const path = entry.indices.length === 1 ? entry.indices[0] : []
  return entry.target + path.map((i) => `[${i}]`).join('')
}

/** Index paths Gemini points at inside the container known by `names`. */
export const aiIndexes = (scene, names) => scene.ai.cells.filter((c) => names.includes(c.name)).map((c) => c.path)

/** Positions in a flat sequence from 1-element index paths, normalized and in range. */
export function aiPositions(paths, length) {
  const set = new Set()
  for (const p of paths) {
    if (p.length !== 1) continue
    const i = normIndex(p[0], length)
    if (i >= 0 && i < length) set.add(i)
  }
  return set
}

/** Set of key JSON Gemini points at inside the dict/set known by `names`. */
export const aiKeys = (scene, names) => new Set(scene.ai.keys.filter((k) => names.includes(k.name)).map((k) => k.key))

// ---------------------------------------------------------------------------
// What changed between two steps (for the narration panel)
// ---------------------------------------------------------------------------

function describeContainer(name, before, after, heapBefore, heapAfter) {
  const out = []
  const f = (v, heap) => fmt(v, heap)
  if (before.t !== after.t) return [`${name} changed`]
  if (before.t === 'list' || before.t === 'deque') {
    const a = before.items
    const b = after.items
    if (b.length === a.length + 1 && same(a, b.slice(0, -1))) return [`${name}.append(${f(b.at(-1), heapAfter)})`]
    if (b.length === a.length + 1 && same(a, b.slice(1))) return [`${name}.appendleft(${f(b[0], heapAfter)})`]
    if (b.length === a.length - 1 && same(b, a.slice(0, -1))) return [`${name}.pop() → ${f(a.at(-1), heapBefore)}`]
    if (b.length === a.length - 1 && same(b, a.slice(1))) return [`${name}.popleft() → ${f(a[0], heapBefore)}`]
    if (a.length === b.length) {
      const changed = []
      for (let i = 0; i < a.length; i++) {
        if (!same(a[i], b[i])) changed.push(`${name}[${i}] = ${f(b[i], heapAfter)}`)
        else if (isRef(a[i]) && heapBefore[a[i].id] && heapAfter[a[i].id] && !same(heapBefore[a[i].id], heapAfter[a[i].id])) {
          const row = heapBefore[a[i].id]
          const rowAfter = heapAfter[a[i].id]
          if (row.items && rowAfter.items && row.items.length === rowAfter.items.length) {
            rowAfter.items.forEach((x, j) => {
              if (!same(x, row.items[j])) changed.push(`${name}[${i}][${j}] = ${f(x, heapAfter)}`)
            })
          } else {
            out.push(...describeContainer(`${name}[${i}]`, row, rowAfter, heapBefore, heapAfter))
          }
        }
      }
      if (changed.length > 4) return [`${name}: ${changed.length} cells changed`]
      if (changed.length) return changed
    }
    if (out.length) return out
    return [`${name} → ${fmtObject(after, heapAfter, 0)}`]
  }
  if (before.t === 'set') {
    const a = new Set(before.items.map((x) => JSON.stringify(x)))
    const b = new Set(after.items.map((x) => JSON.stringify(x)))
    for (const x of after.items) if (!a.has(JSON.stringify(x))) out.push(`${name}.add(${f(x, heapAfter)})`)
    for (const x of before.items) if (!b.has(JSON.stringify(x))) out.push(`${name}.remove(${f(x, heapBefore)})`)
    return out
  }
  if (before.t === 'dict') {
    const a = new Map(before.entries.map(([k, v]) => [JSON.stringify(k), v]))
    const b = new Map(after.entries.map(([k, v]) => [JSON.stringify(k), v]))
    for (const [k, v] of after.entries) {
      const key = JSON.stringify(k)
      if (!a.has(key)) out.push(`${name}[${f(k, heapAfter)}] = ${f(v, heapAfter)}`)
      else if (!same(a.get(key), v)) out.push(`${name}[${f(k, heapAfter)}]: ${f(a.get(key), heapBefore)} → ${f(v, heapAfter)}`)
      else if (isRef(v) && !same(heapBefore[v.id], heapAfter[v.id]) && heapBefore[v.id] && heapAfter[v.id]) {
        out.push(...describeContainer(`${name}[${f(k, heapAfter)}]`, heapBefore[v.id], heapAfter[v.id], heapBefore, heapAfter))
      }
    }
    for (const [k] of before.entries) if (!b.has(JSON.stringify(k))) out.push(`del ${name}[${f(k, heapBefore)}]`)
    return out.slice(0, 6)
  }
  if (before.t === 'obj') {
    for (const [attr, v] of Object.entries(after.attrs)) {
      const old = before.attrs[attr]
      if (!same(old, v)) out.push(`${name}.${attr} = ${f(v, heapAfter)}`)
      else if (isRef(v) && heapBefore[v.id] && heapAfter[v.id] && !same(heapBefore[v.id], heapAfter[v.id]) && !nodeKind(heapAfter[v.id])) {
        out.push(...describeContainer(`${name}.${attr}`, heapBefore[v.id], heapAfter[v.id], heapBefore, heapAfter))
      }
    }
    return out
  }
  return [`${name} changed`]
}

export function callText(frame, params) {
  const names = params[frame.name] ?? []
  const args = names.filter((n) => n in frame.locals).map((n) => `${n}=${fmt(frame.locals[n], null)}`)
  return `${frame.name}(${args.join(', ')})`
}

/** Short sentences describing what the previous line did. */
export function describeStep(prev, step, params) {
  if (!prev) return [`Start: ${callText(step.frames[step.frames.length - 1], params)} is called`]
  const out = []
  const prevTop = prev.frames[prev.frames.length - 1]
  const top = step.frames[step.frames.length - 1]
  if (!top) return out

  if (prev.event === 'return') {
    out.push(`${prevTop.name}() returned ${fmt(prev.ret, prev.heap)}`)
  }
  if (step.frames.length > prev.frames.length && !prev.frames.some((f) => f.id === top.id)) {
    out.push(`Called ${callText(top, params)}`)
    return out
  }
  if (step.event === 'return') {
    out.push(`return ${fmt(step.ret, step.heap)}`)
  }
  if (step.event === 'exception') {
    out.push(`Raised ${step.exc}`)
  }
  const before = prev.frames.find((f) => f.id === top.id)
  if (!before) return out
  for (const [name, v] of Object.entries(top.locals)) {
    if (!(name in before.locals)) {
      out.push(`${name} = ${fmt(v, step.heap)}`)
      continue
    }
    const old = before.locals[name]
    if (isRef(v) && isRef(old) && v.id === old.id) {
      const a = prev.heap[v.id]
      const b = step.heap[v.id]
      if (a && b && !same(a, b) && !nodeKind(b)) out.push(...describeContainer(name, a, b, prev.heap, step.heap))
      else if (a && b && nodeKind(b) && !same(a, b)) {
        for (const [attr, val] of Object.entries(b.attrs)) {
          if (!same(a.attrs[attr], val)) out.push(`${name}.${attr} = ${fmt(val, step.heap)}`)
        }
      }
    } else if (!same(old, v)) {
      out.push(isRef(v) || isRef(old) ? `${name} → ${fmt(v, step.heap)}` : `${name}: ${fmt(old, prev.heap)} → ${fmt(v, step.heap)}`)
    }
  }
  return out.slice(0, 8)
}

/** Ids of heap objects whose contents changed since the previous step. */
export function changedIds(prev, step) {
  const ids = new Set()
  if (!prev) return ids
  for (const [id, obj] of Object.entries(step.heap)) {
    if (prev.heap[id] && !same(prev.heap[id], obj)) ids.add(Number(id))
  }
  return ids
}

// ---------------------------------------------------------------------------
// Call tree (recursion) from all steps up to `upto`
// ---------------------------------------------------------------------------

export function hasRecursion(steps) {
  return steps.some((s) => {
    const names = s.frames.map((f) => f.name)
    return new Set(names).size < names.length
  })
}

export function buildCallTree(steps, upto, params) {
  const nodes = new Map()
  const roots = []
  for (let k = 0; k <= upto && k < steps.length; k++) {
    const s = steps[k]
    s.frames.forEach((f, depth) => {
      if (nodes.has(f.id)) return
      const parent = depth > 0 ? s.frames[depth - 1].id : null
      const node = { id: f.id, name: f.name, label: callText(f, params), parent, children: [], ret: undefined, retText: null }
      nodes.set(f.id, node)
      if (parent !== null && nodes.has(parent)) nodes.get(parent).children.push(f.id)
      else roots.push(f.id)
    })
    if (s.event === 'return') {
      const f = s.frames[s.frames.length - 1]
      const node = nodes.get(f.id)
      if (node) node.retText = fmt(s.ret, s.heap)
    }
  }
  const active = new Set((steps[upto]?.frames ?? []).map((f) => f.id))
  return { nodes, roots, active, current: steps[upto]?.frames.at(-1)?.id }
}
