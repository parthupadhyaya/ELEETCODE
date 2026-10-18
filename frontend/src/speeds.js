// Autoplay speeds (milliseconds each step stays on screen before reading time)
export const SPEEDS = [
  { label: '0.25×', ms: 3600 },
  { label: '0.5×', ms: 2400 },
  { label: '1×', ms: 1600 },
  { label: '2×', ms: 800 },
  { label: '4×', ms: 350 },
]

export const DEFAULT_SPEED = 2

/**
 * How long autoplay holds a step: the speed's base time, stretched for long
 * narrations so there's time to read them (about 12 words fit the base time).
 */
export function holdTime(speed, narration) {
  const words = narration ? narration.split(/\s+/).length : 0
  return SPEEDS[speed].ms * Math.min(1.8, Math.max(1, words / 12))
}

/** Explanation levels: how much detail the visualizer shows around each step. */
export const LEVELS = [
  { id: 'beginner', label: 'Beginner', hint: 'Plain-English explanations, color legend, only what matters' },
  { id: 'standard', label: 'Standard', hint: 'Explanations plus the exact values each line changed' },
  { id: 'expert', label: 'Expert', hint: 'Everything, compact, nothing dimmed' },
]
