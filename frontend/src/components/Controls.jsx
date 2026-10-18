import { LEVELS, SPEEDS } from '../speeds.js'

const STEP_MODES = [
  { id: 'key', label: 'Key moments', hint: 'Stop only where something happens' },
  { id: 'line', label: 'Every line', hint: 'Stop at every line that runs' },
]

function Segmented({ label, options, value, onChange }) {
  return (
    <div className="segmented" role="radiogroup" aria-label={label}>
      <span className="segmented-label">{label}</span>
      {options.map((o) => (
        <button
          key={o.id}
          type="button"
          role="radio"
          aria-checked={value === o.id}
          className={value === o.id ? 'is-on' : ''}
          title={o.hint}
          onClick={() => onChange(o.id)}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

/**
 * Playback bar: first / back / play / forward / last, a scrubber and speed,
 * then the step mode and explanation level.
 */
function Controls({ index, total, playing, onTogglePlay, onSeek, onPrev, onNext, speed, onSpeed, stepMode, onStepMode, level, onLevel }) {
  const last = total - 1
  return (
    <div className="controls">
      <div className="controls-row">
        <div className="controls-buttons">
          <button type="button" className="btn icon" title="First step (Home)" disabled={index <= 0} onClick={() => onSeek(0)}>
            ⏮
          </button>
          <button type="button" className="btn icon" title="Step back (←)" disabled={index <= 0} onClick={onPrev}>
            ◀
          </button>
          <button type="button" className="btn btn-primary play" title="Play / pause (Space)" disabled={total < 2} onClick={onTogglePlay}>
            {playing ? '❚❚ Pause' : index >= last ? '↺ Replay' : '▶ Play'}
          </button>
          <button type="button" className="btn icon" title="Step forward (→)" disabled={index >= last} onClick={onNext}>
            ▶
          </button>
          <button type="button" className="btn icon" title="Last step (End)" disabled={index >= last} onClick={() => onSeek(last)}>
            ⏭
          </button>
        </div>
        <input
          className="scrubber"
          type="range"
          min={0}
          max={Math.max(last, 0)}
          value={index}
          onChange={(e) => onSeek(Number(e.target.value))}
          aria-label="Step"
        />
        <select className="speed" value={speed} onChange={(e) => onSpeed(Number(e.target.value))} aria-label="Speed" title="Playback speed">
          {SPEEDS.map((s, i) => (
            <option key={s.label} value={i}>
              {s.label}
            </option>
          ))}
        </select>
      </div>
      <div className="controls-row controls-options">
        <Segmented label="Play" options={STEP_MODES} value={stepMode} onChange={onStepMode} />
        <Segmented label="Explain for" options={LEVELS} value={level} onChange={onLevel} />
      </div>
    </div>
  )
}

export default Controls
