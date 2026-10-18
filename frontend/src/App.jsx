import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { animateCode, fetchProblem, fetchProblems, traceCode } from './api.js'
import CodeEditor from './components/CodeEditor.jsx'
import Controls from './components/Controls.jsx'
import ProblemList from './components/ProblemList.jsx'
import Visualizer from './components/Visualizer.jsx'
import { DEFAULT_SPEED, LEVELS, SPEEDS, holdTime } from './speeds.js'
import { currentAnimation, keySteps } from './viz/model.js'
import './App.css'

const DEFAULT_PROBLEM = 'two-sum'

const storage = {
  get(key) {
    try {
      return localStorage.getItem(key)
    } catch {
      return null
    }
  },
  set(key, value) {
    try {
      if (value === null) localStorage.removeItem(key)
      else localStorage.setItem(key, value)
    } catch {
      // Storage can be unavailable (private mode); edits just won't persist
    }
  },
}

const problemFromHash = () => decodeURIComponent(window.location.hash.slice(1)) || DEFAULT_PROBLEM

// A saved setting, or `fallback` when it's missing or no longer valid
function loadChoice(key, valid, fallback) {
  const saved = storage.get(key)
  return saved !== null && valid(saved) ? saved : fallback
}

function loadVisited() {
  try {
    return new Set(JSON.parse(storage.get('visited') ?? '[]'))
  } catch {
    return new Set()
  }
}

function App() {
  const [problems, setProblems] = useState([])
  const [backendDown, setBackendDown] = useState(false)
  const [selectedId, setSelectedId] = useState(problemFromHash)
  const [problem, setProblem] = useState(null)
  const [code, setCode] = useState('')
  const [driver, setDriver] = useState('')
  const [trace, setTrace] = useState(null)
  const [running, setRunning] = useState(false)
  const [dirty, setDirty] = useState(false)
  const [index, setIndex] = useState(0)
  const [playRequested, setPlayRequested] = useState(false)
  const [speed, setSpeed] = useState(() => Number(loadChoice('speed', (v) => SPEEDS[Number(v)], DEFAULT_SPEED)))
  // 'key' stops only where something happens; 'line' stops at every traced line
  const [stepMode, setStepMode] = useState(() => loadChoice('stepMode', (v) => v === 'key' || v === 'line', 'key'))
  const [level, setLevel] = useState(() => loadChoice('level', (v) => LEVELS.some((l) => l.id === v), 'beginner'))
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [visited, setVisited] = useState(loadVisited)
  const requestId = useRef(0)
  const [reloadKey, setReloadKey] = useState(0)

  const steps = trace?.steps ?? []
  const last = steps.length - 1
  const playing = playRequested && index < last
  const step = steps[index]
  const animation = trace?.animation
  const keys = useMemo(() => (trace ? keySteps(trace.steps, animation) : []), [trace, animation])
  const stops = stepMode === 'key' && keys.length ? keys : null
  // Neighbouring stops in the current step mode
  const nextStop = (i) => (stops ? (stops.find((k) => k > i) ?? last) : Math.min(i + 1, last))
  const prevStop = (i) => (stops ? (stops.findLast((k) => k < i) ?? 0) : Math.max(i - 1, 0))

  // Problem list
  useEffect(() => {
    fetchProblems()
      .then((list) => {
        setProblems(list)
        setBackendDown(false)
      })
      .catch(() => setBackendDown(true))
  }, [reloadKey])

  // Follow the URL hash (#two-sum) so problems are linkable
  useEffect(() => {
    const onHash = () => setSelectedId(problemFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const visualize = useCallback(async (src, run) => {
    const id = ++requestId.current
    setRunning(true)
    setPlayRequested(false)
    let result
    try {
      result = await traceCode(src, run)
      if (id !== requestId.current) return
      // Show the trace now; Gemini's animation fills in when it arrives
      setTrace({ ...result, animation: null, animation_error: null, animation_pending: result.steps.length > 0 })
      setIndex(0)
      setDirty(false)
      setBackendDown(false)
    } catch {
      if (id === requestId.current) setBackendDown(true)
    } finally {
      if (id === requestId.current) setRunning(false)
    }
    if (!result?.steps.length) return

    let ai
    try {
      ai = await animateCode(src, run)
    } catch (err) {
      ai = { animation: null, animation_error: `AI animation failed: ${err.message}` }
    }
    if (id === requestId.current) setTrace((t) => ({ ...t, ...ai, animation_pending: false }))
  }, [])

  // Load the selected problem (with any saved edits) and trace it
  useEffect(() => {
    let cancelled = false
    fetchProblem(selectedId)
      .then((p) => {
        if (cancelled) return
        const savedCode = storage.get(`code:${p.id}`) ?? p.code
        const savedRun = storage.get(`run:${p.id}`) ?? p.run
        setProblem(p)
        setCode(savedCode)
        setDriver(savedRun)
        setTrace(null)
        setVisited((prev) => {
          const next = new Set(prev).add(p.id)
          storage.set('visited', JSON.stringify([...next]))
          return next
        })
        visualize(savedCode, savedRun)
      })
      .catch((err) => {
        if (cancelled) return
        if (String(err.message).startsWith('404') && selectedId !== DEFAULT_PROBLEM) setSelectedId(DEFAULT_PROBLEM)
        else setBackendDown(true)
      })
    return () => {
      cancelled = true
    }
  }, [selectedId, visualize, reloadKey])

  // Autoplay: hold each stop long enough to read its narration
  const narration = currentAnimation(animation, index)
    .map((a) => a.narration)
    .join(' ')
  const next = nextStop(index)
  useEffect(() => {
    if (!playing) return
    const id = setTimeout(() => setIndex(next), holdTime(speed, narration))
    return () => clearTimeout(id)
  }, [playing, next, speed, narration])

  const changeSpeed = (v) => {
    setSpeed(v)
    storage.set('speed', String(v))
  }
  const changeStepMode = (v) => {
    setStepMode(v)
    storage.set('stepMode', v)
  }
  const changeLevel = (v) => {
    setLevel(v)
    storage.set('level', v)
  }

  const seek = useCallback(
    (i) => {
      setPlayRequested(false)
      setIndex(Math.max(0, Math.min(i, last)))
    },
    [last],
  )

  const togglePlay = useCallback(() => {
    if (playing) {
      setPlayRequested(false)
      return
    }
    if (index >= last) setIndex(0)
    setPlayRequested(true)
  }, [playing, index, last])

  const run = useCallback(() => visualize(code, driver), [visualize, code, driver])
  const prev = prevStop(index)
  // "Moment 4 of 13" in key-moment mode: stops passed so far, this one included
  const progress = stops
    ? { label: 'Moment', at: stops.filter((k) => k <= index).length, of: stops.length }
    : { label: 'Step', at: index + 1, of: steps.length }

  // Keyboard: ← → step, space play, Home/End, Ctrl+Enter run
  useEffect(() => {
    const onKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault()
        run()
        return
      }
      const tag = e.target.tagName
      if (tag === 'TEXTAREA' || tag === 'INPUT' || tag === 'SELECT') return
      if (e.key === 'ArrowRight') seek(next)
      else if (e.key === 'ArrowLeft') seek(prev)
      else if (e.key === 'Home') seek(0)
      else if (e.key === 'End') seek(last)
      else if (e.key === ' ') togglePlay()
      else return
      e.preventDefault()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [run, seek, togglePlay, next, prev, last])

  const selectProblem = (id) => {
    if (id === selectedId) return
    window.location.hash = id
    setSelectedId(id)
    if (window.innerWidth < 1100) setSidebarOpen(false)
  }

  const editCode = (value) => {
    setCode(value)
    setDirty(true)
    if (problem) storage.set(`code:${problem.id}`, value === problem.code ? null : value)
  }

  const editDriver = (value) => {
    setDriver(value)
    setDirty(true)
    if (problem) storage.set(`run:${problem.id}`, value === problem.run ? null : value)
  }

  const resetCode = () => {
    if (!problem) return
    storage.set(`code:${problem.id}`, null)
    storage.set(`run:${problem.id}`, null)
    setCode(problem.code)
    setDriver(problem.run)
    visualize(problem.code, problem.run)
  }

  const prevStep = index > 0 ? steps[index - 1] : null
  const sameFrame = prevStep && step && prevStep.frames.at(-1)?.id === step.frames.at(-1)?.id
  const showMarkers = trace && !dirty
  const loopBadges = new Map()
  if (showMarkers && step) {
    for (const l of step.loops ?? []) loopBadges.set(l.line, { text: l.done ? `done (${l.iter})` : `${l.iter}`, done: l.done })
  }
  const edited = problem && (code !== problem.code || driver !== problem.run)
  // Line of the trace step Gemini's current narration belongs to (taken from
  // the trace rather than the script, so a wrong `line` from Gemini can't misplace it)
  const aiTraceIndex = currentAnimation(trace?.animation, index)[0]?.trace_index
  const aiLine = aiTraceIndex === undefined ? null : steps[aiTraceIndex]?.line ?? null

  return (
    <div className={`app ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <header className="app-header">
        <button type="button" className="btn icon" onClick={() => setSidebarOpen((o) => !o)} title="Toggle problem list" aria-label="Toggle problem list">
          ☰
        </button>
        <span className="app-title">
          <span className="logo">◆</span> LeetCode Visualizer
        </span>
        {problem && (
          <span className="app-problem">
            {problem.num}. {problem.title}
            <span className={`diff is-${problem.difficulty.toLowerCase()}`}>{problem.difficulty}</span>
            <span className="app-category">{problem.category}</span>
          </span>
        )}
        <span className="spacer" />
        <button type="button" className="btn btn-primary" onClick={run} disabled={running || !problem} title="Run and visualize (Ctrl+Enter)">
          {running ? 'Running…' : '▶ Run & Visualize'}
        </button>
      </header>

      {backendDown && (
        <div className="banner">
          Can't reach the backend. Start it with <code>cd backend</code> then{' '}
          <code>venv\Scripts\uvicorn main:app --port 8000</code>
          <button type="button" className="btn" onClick={() => setReloadKey((k) => k + 1)}>
            Retry
          </button>
        </div>
      )}

      <main className="app-body">
        {sidebarOpen && (
          <aside className="sidebar">
            <ProblemList problems={problems} selectedId={selectedId} onSelect={selectProblem} visited={visited} />
          </aside>
        )}
        {sidebarOpen && <div className="sidebar-scrim" onClick={() => setSidebarOpen(false)} />}

        <section className="pane pane-editor" aria-label="Code">
          {problem && (
            <details className="description" open>
              <summary>Problem &amp; idea</summary>
              <p>{problem.description}</p>
            </details>
          )}
          <div className="pane-header">
            <span>solution.py</span>
            {edited && (
              <button type="button" className="link" onClick={resetCode}>
                reset to original
              </button>
            )}
            {dirty && trace && <span className="stale">edited, press Run to update</span>}
          </div>
          <CodeEditor
            value={code}
            onChange={editCode}
            onRun={run}
            activeLine={showMarkers && step?.event !== 'return' ? step?.line : null}
            prevLine={showMarkers && sameFrame ? prevStep.line : null}
            aiLine={showMarkers ? aiLine : null}
            errorLine={showMarkers && trace.error && index === last ? trace.error.line : null}
            loopBadges={loopBadges}
          />
          <div className="pane-header">
            <span>test input</span>
            <span className="hint">last line is the result</span>
          </div>
          <div className="driver">
            <CodeEditor value={driver} onChange={editDriver} onRun={run} />
          </div>
          <Console trace={trace} step={step} atEnd={index === last} />
        </section>

        <section className="pane pane-viz" aria-label="Visualization">
          <Controls
            index={index}
            total={steps.length}
            playing={playing}
            onTogglePlay={togglePlay}
            onSeek={seek}
            onPrev={() => seek(prev)}
            onNext={() => seek(next)}
            speed={speed}
            onSpeed={changeSpeed}
            stepMode={stepMode}
            onStepMode={changeStepMode}
            level={level}
            onLevel={changeLevel}
          />
          {trace && steps.length > 0 ? (
            <Visualizer trace={trace} index={index} progress={progress} level={level} code={code} category={problem?.category} key={`${problem?.id}:${steps.length}`} />
          ) : (
            <div className="viz-empty">
              {running ? 'Tracing your code…' : trace?.error ? 'The code stopped before running any lines. See the console for the error.' : 'Pick a problem to start.'}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

function Console({ trace, step, atEnd }) {
  if (!trace) return null
  const { error, truncated, result } = trace
  const stdout = step?.stdout ?? trace.stdout
  return (
    <div className="console">
      {error && (
        <div className="console-error">
          {error.type}: {error.message}
          {error.line ? ` (line ${error.line})` : ''}
        </div>
      )}
      {truncated && <div className="console-warn">Stopped after {trace.steps.length} steps. Try a smaller input.</div>}
      {stdout && <pre className="console-out">{stdout}</pre>}
      {result !== undefined && (
        <div className={`console-result ${atEnd ? 'is-final' : ''}`}>
          <span>Result</span> <code>{result}</code>
        </div>
      )}
    </div>
  )
}

export default App
