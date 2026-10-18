// Colours that identify a variable consistently across every view.

const POINTER_COLORS = ['#f5b14c', '#7c9cff', '#5fd3a8', '#f07aa8', '#b18cff', '#4cc9f0', '#ff8f5a']

const FIXED = { l: 0, left: 0, lo: 0, low: 0, start: 0, slow: 2, i: 0, r: 1, right: 1, hi: 1, high: 1, end: 1, fast: 3, j: 1, mid: 4 }

function hash(s) {
  let h = 0
  for (const ch of s) h = (h * 31 + ch.charCodeAt(0)) | 0
  return Math.abs(h)
}

export function pointerColor(name) {
  const fixed = FIXED[name]
  return POINTER_COLORS[fixed ?? hash(name) % POINTER_COLORS.length]
}

/** Fill colours for "membership" markers (seen/visiting/path/...). */
export const MARKER_COLORS = [
  'rgba(95, 211, 168, 0.32)',
  'rgba(245, 177, 76, 0.32)',
  'rgba(124, 156, 255, 0.35)',
  'rgba(240, 122, 168, 0.32)',
]
export const MARKER_SOLID = ['#5fd3a8', '#f5b14c', '#7c9cff', '#f07aa8']
