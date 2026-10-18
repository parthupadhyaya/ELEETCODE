import { AnimatePresence, motion } from 'framer-motion'
import { useEffect, useMemo, useRef, useState } from 'react'
import { CallTree } from '../viz/GraphViews.jsx'
import { LinkedListDiagram, NodeGraphDiagram, TreeDiagram, TrieDiagram } from '../viz/NodeDiagrams.jsx'
import { StringCard, StructureCard } from '../viz/Structure.jsx'
import {
  accessesFor,
  aiFocus,
  aiTargeted,
  aiWhere,
  buildCallTree,
  buildScene,
  callText,
  changedIds,
  currentAnimation,
  describeStep,
  fmt,
  functionParams,
  hasRecursion,
  isInt,
  same,
} from '../viz/model.js'

const NODE_TITLES = { list: 'Linked list', tree: 'Binary tree', trie: 'Trie', graph: 'Graph nodes' }

// How each Gemini action is labelled and coloured in the caption
const ACTIONS = {
  highlight: { label: 'Look', tone: 'accent' },
  compare: { label: 'Compare', tone: 'active' },
  assign: { label: 'Set', tone: 'write' },
  swap: { label: 'Swap', tone: 'pink' },
  insert: { label: 'Add', tone: 'write' },
  remove: { label: 'Remove', tone: 'error' },
  visit: { label: 'Visit', tone: 'read' },
  pointer_move: { label: 'Move', tone: 'accent' },
  call: { label: 'Call', tone: 'purple' },
  return: { label: 'Return', tone: 'purple' },
  done: { label: 'Done', tone: 'write' },
  error: { label: 'Error', tone: 'error' },
}

/** A sentence for steps Gemini hasn't narrated (or while its script loads). */
function fallbackCaption(step, lineText, changes) {
  const fn = step.frames.at(-1)?.name
  if (step.event === 'exception') return { tone: 'error', label: 'Error', text: `Something went wrong: ${step.exc}` }
  if (step.event === 'return') return { tone: 'purple', label: 'Return', text: `${fn}() is finished and gives back ${fmt(step.ret, step.heap)}.` }
  if (changes[0]?.startsWith('Start')) return { tone: 'purple', label: 'Start', text: changes[0].replace('Start: ', 'We begin by calling ').replace(' is called', '.') }
  return { tone: 'accent', label: 'Run', text: null, code: lineText }
}

/**
 * The big explanation at the top: Gemini's narration for this step when it has
 * one, otherwise a plain sentence built from the trace.
 */
function Caption({ step, lineText, entries, changes, level, pending, error, hasAnimation }) {
  const fallback = entries.length ? null : fallbackCaption(step, lineText, changes)
  return (
    <div className={`caption ${level === 'expert' ? 'is-compact' : ''}`}>
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={entries.length ? `ai:${entries[0].trace_index}` : `fb:${step.line}:${step.event}:${changes.join('|')}`}
          className="caption-body"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.25 }}
        >
          {entries.length ? (
            entries.map((a, i) => {
              const meta = ACTIONS[a.action] ?? ACTIONS.highlight
              return (
                <p key={i} className="caption-line">
                  <span className={`caption-tag tone-${meta.tone}`}>{meta.label}</span>
                  <span className="caption-text">{a.narration}</span>
                  {level !== 'beginner' && a.value != null && (
                    <span className="ai-value" title={a.value}>
                      {a.target && <span className="ai-where">{aiWhere(a)}</span>}
                      <code>{a.value}</code>
                    </span>
                  )}
                </p>
              )
            })
          ) : (
            <p className="caption-line">
              <span className={`caption-tag tone-${fallback.tone}`}>{fallback.label}</span>
              <span className="caption-text">
                {fallback.text ?? (
                  <>
                    Running line {step.line}: <code>{fallback.code}</code>
                  </>
                )}
              </span>
            </p>
          )}
        </motion.div>
      </AnimatePresence>
      {pending && <div className="caption-status">✦ Writing step-by-step explanations…</div>}
      {!pending && !hasAnimation && error && level !== 'beginner' && <div className="caption-status">✦ {error}</div>}
    </div>
  )
}

function Narration({ step, progress, lines, changes, loopsInfo, level, animation, animationError, animationPending, aiEntries }) {
  const lineText = (lines[step.line - 1] ?? '').trim()
  return (
    <div className="narration">
      <div className="narration-head">
        <span className="badge">
          {progress.label} {progress.at} of {progress.of}
        </span>
        {step.event === 'return' ? (
          <span>
            <b>{step.frames.at(-1)?.name}</b> returns <code>{fmt(step.ret, step.heap)}</code>
          </span>
        ) : step.event === 'exception' ? (
          <span className="is-error">Exception: {step.exc}</span>
        ) : (
          <span className="narration-line">
            line {step.line} <code>{lineText}</code>
          </span>
        )}
      </div>
      <Caption
        step={step}
        lineText={lineText}
        entries={aiEntries}
        changes={changes}
        level={level}
        pending={animationPending}
        error={animationError}
        hasAnimation={!!animation}
      />
      {level !== 'beginner' && changes.length > 0 && (
        <ul className="changes">
          {changes.map((c, i) => (
            <motion.li key={`${c}-${i}`} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }}>
              <code>{c}</code>
            </motion.li>
          ))}
        </ul>
      )}
      {loopsInfo.length > 0 && (
        <div className="loops">
          {loopsInfo.map((l) => (
            <div key={l.line} className={`loop ${l.done ? 'is-done' : ''}`}>
              <span className="loop-icon">↻</span>
              {level !== 'beginner' && <code>{l.head}</code>}
              <span className="loop-iter">
                {l.done
                  ? `loop finished after ${l.iter} round${l.iter === 1 ? '' : 's'}`
                  : level === 'beginner'
                    ? `loop, round ${l.iter}`
                    : `iteration ${l.iter}`}
              </span>
              {!l.done && l.targets.length > 0 && <span className="loop-vars">{l.targets.join(', ')}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function savedLegendOpen() {
  try {
    return localStorage.getItem('legendOpen') === '1'
  } catch {
    return false
  }
}

/** What the highlight colours mean: a one-line toggle that remembers its state. */
function Legend() {
  const [open, setOpen] = useState(savedLegendOpen)
  const toggle = (e) => {
    const next = e.currentTarget.open
    setOpen(next)
    try {
      localStorage.setItem('legendOpen', next ? '1' : '0')
    } catch {
      // Storage unavailable: the legend just won't remember
    }
  }
  return (
    <details className="viz-legend" open={open} onToggle={toggle}>
      <summary>ⓘ What do the colors mean?</summary>
      <div className="viz-legend-items">
        <span>
          <i className="sw sw-read" /> being read by this line
        </span>
        <span>
          <i className="sw sw-write" /> being written by this line
        </span>
        <span>
          <i className="sw sw-changed" /> value just changed
        </span>
        <span>
          <i className="sw sw-ai" /> what the explanation is about
        </span>
        <span>
          <b className="sw-ptr">▲ i</b> index variable pointing at a cell
        </span>
        <span>
          <i className="sw sw-window" /> range between two pointers
        </span>
      </div>
    </details>
  )
}

function Bits({ value, prev }) {
  const width = Math.max(8, Math.ceil(Math.log2(Math.max(value, prev ?? 0, 1) + 1) / 4) * 4)
  const bits = value.toString(2).padStart(width, '0').slice(-width)
  const prevBits = prev === undefined ? bits : prev.toString(2).padStart(width, '0').slice(-width)
  return (
    <span className="bits">
      {[...bits].map((b, i) => (
        <span key={i} className={`bit ${b === '1' ? 'is-one' : ''} ${prevBits[i] !== b ? 'is-flipped' : ''}`}>
          {b}
        </span>
      ))}
    </span>
  )
}

function Variables({ vars, prevLocals, heap, showBits, aiNames }) {
  if (!vars.length) return null
  return (
    <section className="card">
      <header className="card-head">
        <span className="card-name">Variables</span>
      </header>
      <div className="vars">
        {vars.map(({ name, value }) => {
          const text = fmt(value, heap)
          const isNew = prevLocals && !(name in prevLocals)
          const changed = prevLocals && name in prevLocals && !same(prevLocals[name], value)
          return (
            <motion.div
              key={`${name}:${text}`}
              className={`var ${changed ? 'is-changed' : ''} ${isNew ? 'is-new' : ''} ${aiNames.has(name) ? 'is-ai' : ''}`}
              initial={changed || isNew ? { scale: 1.12 } : false}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
            >
              <span className="var-name">{name}</span>
              <span className="var-value">{text}</span>
              {showBits && isInt(value) && value >= 0 && value < 2 ** 32 && (
                <Bits value={value} prev={isInt(prevLocals?.[name]) ? prevLocals[name] : undefined} />
              )}
            </motion.div>
          )
        })}
      </div>
    </section>
  )
}

function CallStack({ frames, params }) {
  return (
    <section className="card">
      <header className="card-head">
        <span className="card-name">Call stack</span>
        <span className="card-meta">{frames.length} frame{frames.length === 1 ? '' : 's'}</span>
      </header>
      <div className="frames">
        <AnimatePresence initial={false}>
          {[...frames].reverse().map((f, i) => (
            <motion.div
              key={f.id}
              layout
              className={`frame ${i === 0 ? 'is-top' : ''}`}
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <code>{callText(f, params)}</code>
              <span className="frame-line">line {f.line}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </section>
  )
}

export default function Visualizer({ trace, index, progress, level, code, category }) {
  const steps = trace.steps
  const step = steps[index]
  const prev = index > 0 ? steps[index - 1] : null
  const lines = useMemo(() => code.split('\n'), [code])
  const params = useMemo(() => functionParams(code), [code])
  // Strings the code indexes into (s[i]) get a character-block card
  const strCards = useMemo(() => new Set([...code.matchAll(/\b([A-Za-z_]\w*)\[/g)].map((m) => m[1])), [code])
  const recursive = useMemo(() => hasRecursion(steps), [steps])
  const loopDefs = useMemo(() => new Map((trace.loops ?? []).map((l) => [l.line, l])), [trace])
  const scrollRef = useRef(null)

  // Keep the spotlighted container on screen as the steps move
  useEffect(() => {
    const card = scrollRef.current?.querySelector('.card.is-focus')
    card?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }, [index])

  if (!step) return null
  const scene = buildScene(step, code, strCards)
  const aiEntries = currentAnimation(trace.animation, index)
  scene.ai = aiFocus(aiEntries, scene, steps)
  const changed = changedIds(prev, step)
  const changes = describeStep(prev, step, params)
  const prevTop = prev?.frames.find((f) => f.id === scene.top?.id)

  const loopsInfo = (step.loops ?? [])
    .map((l) => {
      const def = loopDefs.get(l.line)
      if (!def) return null
      const targets = (def.targets ?? [])
        .filter((t) => t in (scene.top?.locals ?? {}))
        .map((t) => `${t} = ${fmt(scene.top.locals[t], step.heap)}`)
      return { ...l, head: def.head, targets }
    })
    .filter(Boolean)

  const nodeGroups = {}
  for (const n of scene.nodes.values()) (nodeGroups[n.kind] ||= []).push(n)

  const callTree = recursive ? buildCallTree(steps, index, params) : null

  // Spotlight: when this step touches some containers, dim the rest so the eye
  // goes to where the action is (not in expert mode, which shows all evenly)
  const involved = (names, id) => changed.has(id) || accessesFor(scene, names).length > 0 || aiTargeted(scene, names)
  const anyInvolved =
    scene.structures.some((st) => involved(st.names, st.id)) || scene.strings.some((st) => involved([st.name], null))
  const focus = (names, id) => {
    if (level === 'expert' || !anyInvolved) return ''
    return involved(names, id) ? 'is-focus' : 'is-dim'
  }
  const showStack = level !== 'beginner' || step.frames.length > 1

  return (
    <div className={`visualizer level-${level}`}>
      <Narration
        step={step}
        progress={progress}
        lines={lines}
        changes={changes}
        loopsInfo={loopsInfo}
        level={level}
        animation={trace.animation}
        animationError={trace.animation_error}
        animationPending={trace.animation_pending}
        aiEntries={aiEntries}
      />

      <div className="viz-scroll" ref={scrollRef}>
        <Legend />

        {scene.strings.map((st) => (
          <StringCard
            key={st.name}
            name={st.name}
            value={st.value}
            scene={scene}
            prevValue={prevTop?.locals[st.name]?.v}
            focus={focus([st.name], null)}
          />
        ))}

        {Object.entries(nodeGroups).map(([kind, nodes]) => {
          const props = { nodes, labels: scene.nodeLabels, heap: step.heap, changed, aiNodes: scene.ai.nodes }
          return (
            <section key={kind} className="card">
              <header className="card-head">
                <span className="card-name">{NODE_TITLES[kind]}</span>
                <span className="card-meta">{nodes.length} nodes</span>
              </header>
              {kind === 'list' && <LinkedListDiagram {...props} />}
              {kind === 'tree' && <TreeDiagram {...props} />}
              {kind === 'trie' && <TrieDiagram {...props} />}
              {kind === 'graph' && <NodeGraphDiagram {...props} />}
            </section>
          )
        })}

        {scene.structures.map((st) => (
          <StructureCard
            key={st.id}
            structure={st}
            scene={scene}
            prevHeap={prev?.heap}
            changed={changed.has(st.id)}
            focus={focus(st.names, st.id)}
          />
        ))}

        <Variables
          vars={scene.vars}
          prevLocals={prevTop?.locals}
          heap={step.heap}
          showBits={category === 'Bit Manipulation'}
          aiNames={scene.ai.names}
        />

        {callTree && (
          <section className="card">
            <header className="card-head">
              <span className="card-name">Recursion tree</span>
              <span className="card-meta">{callTree.nodes.size} calls so far</span>
            </header>
            <CallTree tree={callTree} aiCalls={scene.ai.calls} />
          </section>
        )}

        {showStack && <CallStack frames={step.frames} params={params} />}
      </div>
    </div>
  )
}
