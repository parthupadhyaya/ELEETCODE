import { motion } from 'framer-motion'
import { useEffect, useMemo, useRef } from 'react'
import { highlightPython } from '../highlight.js'

const TAB = '    '
const LINE = 20 // px, must match .editor line-height
const PAD = 12

/**
 * Textarea with a syntax-highlighted layer underneath and markers for the
 * line about to run (activeLine), the one that just ran (prevLine), the line
 * Gemini's current narration is about (aiLine), loop iteration badges and the
 * line that raised an error.
 */
function CodeEditor({ value, onChange, onRun, activeLine, prevLine, aiLine, errorLine, loopBadges, minLines = 1 }) {
  const scrollRef = useRef(null)
  const lines = value.split('\n')
  const lineCount = Math.max(lines.length, minLines)
  const longest = Math.max(...lines.map((l) => l.length))
  const html = useMemo(() => highlightPython(value), [value])

  // Keep the active line and Gemini's line visible while stepping. If they're
  // too far apart to fit together, the active line wins: that's where
  // execution is, and a fresh Gemini step always starts on it anyway.
  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    const lineTop = (line) => (line - 1) * LINE + PAD
    const scroll = (top) => el.scrollTo({ top: Math.max(0, top), behavior: 'smooth' })

    const tops = [activeLine, aiLine].filter(Boolean).map(lineTop)
    if (!tops.length) return
    const lo = Math.min(...tops)
    const hi = Math.max(...tops)

    // Two different lines that fit on screen together: centre the pair
    if (hi > lo && hi + LINE - lo <= el.clientHeight - LINE) {
      if (lo < el.scrollTop || hi + LINE > el.scrollTop + el.clientHeight) {
        scroll((lo + hi + LINE) / 2 - el.clientHeight / 2)
      }
      return
    }

    // One line: keep a line above and room below it, a third of the way down
    const top = lineTop(activeLine ?? aiLine)
    if (top < el.scrollTop + LINE || top > el.scrollTop + el.clientHeight - 3 * LINE) {
      scroll(top - el.clientHeight / 3)
    }
  }, [activeLine, aiLine])

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      onRun?.()
      return
    }
    if (e.key !== 'Tab') return
    e.preventDefault()
    const el = e.currentTarget
    const { selectionStart: start, selectionEnd: end } = el
    onChange(value.slice(0, start) + TAB + value.slice(end))
    requestAnimationFrame(() => {
      el.selectionStart = el.selectionEnd = start + TAB.length
    })
  }

  const band = (line) => ({ top: PAD + (line - 1) * LINE })

  return (
    <div className="editor" ref={scrollRef}>
      <div className="editor-inner" style={{ height: lineCount * LINE + 2 * PAD, minWidth: `calc(${longest + 8}ch + 56px)` }}>
        <div className="editor-gutter" aria-hidden="true">
          {Array.from({ length: lineCount }, (_, i) => (
            <div
              key={i}
              className={[
                i + 1 === activeLine && 'is-active',
                i + 1 === errorLine && 'is-error',
              ]
                .filter(Boolean)
                .join(' ')}
            >
              {i + 1 === activeLine && <span className="gutter-arrow">➜</span>}
              {i + 1}
            </div>
          ))}
        </div>
        <div className="editor-code">
          {prevLine && prevLine !== activeLine && <div className="line-band is-prev" style={band(prevLine)} />}
          {activeLine && (
            <motion.div
              className="line-band is-active"
              initial={false}
              animate={band(activeLine)}
              transition={{ type: 'spring', stiffness: 600, damping: 40 }}
            />
          )}
          {errorLine && <div className="line-band is-error" style={band(errorLine)} />}
          {aiLine && (
            <motion.div
              className="line-band is-ai"
              initial={false}
              animate={band(aiLine)}
              transition={{ type: 'spring', stiffness: 600, damping: 40 }}
            />
          )}
          <pre className="editor-highlight" aria-hidden="true" dangerouslySetInnerHTML={{ __html: `${html}\n` }} />
          <textarea
            className="editor-input"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            spellCheck={false}
            autoCapitalize="off"
            autoComplete="off"
            wrap="off"
            aria-label="Solution code"
          />
          {[...(loopBadges ?? new Map()).entries()].map(([line, badge]) => (
            <span
              key={line}
              className={`loop-badge ${badge.done ? 'is-done' : ''}`}
              style={{ top: PAD + (line - 1) * LINE + 1, left: `calc(${lines[line - 1]?.length ?? 0}ch + 22px)` }}
            >
              ↻ {badge.text}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

export default CodeEditor
