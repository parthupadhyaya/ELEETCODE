import { useState } from 'react'
import { ArrayView, QueueView, StackView } from './ArrayView.jsx'
import { AdjacencyGraph, HeapTree, UnionFindForest } from './GraphViews.jsx'
import { GridView, IntervalsView } from './GridView.jsx'
import { HashMapView, SetView } from './MapViews.jsx'
import { accessedKeys, accessesFor, aiIndexes, aiKeys, aiTargeted, aiValue, classify, fmt, isRef, nodeKind } from './model.js'

const KIND_LABEL = {
  array: 'list',
  heap: 'heap',
  stack: 'stack',
  queue: 'queue',
  unionfind: 'union-find',
  grid: '2-D grid',
  intervals: 'intervals',
  set: 'set',
  hashmap: 'hashmap',
  graph: 'graph',
  object: 'object',
}

const BAR_NAMES = /height|price|temp|piles|stones|weight|cost|gas/i

function rowsOf(obj, heap) {
  return obj.items.map((v) => (isRef(v) ? (heap[v.id]?.items ?? []) : []))
}

function Toggle({ options, value, onChange }) {
  return (
    <div className="mode-toggle">
      {options.map((o) => (
        <button key={o} type="button" className={value === o ? 'is-on' : ''} onClick={() => onChange(o)}>
          {o}
        </button>
      ))}
    </div>
  )
}

/** The picture for one container, chosen by `kind`. */
export function StructureBody({ id, obj, kind, names, scene, prevHeap }) {
  const [view, setView] = useState(null)
  const heap = scene.heap
  const prevObj = prevHeap?.[id]
  const accesses = accessesFor(scene, names)
  const ai = aiIndexes(scene, names)

  switch (kind) {
    case 'array': {
      const numeric = obj.items.every((v) => typeof v === 'number')
      const mode = view ?? (numeric && names.some((n) => BAR_NAMES.test(n)) ? 'bars' : 'blocks')
      return (
        <>
          {numeric && obj.len > 1 && <Toggle options={['blocks', 'bars']} value={mode} onChange={setView} />}
          <ArrayView
            items={obj.items}
            heap={heap}
            ints={scene.ints}
            accesses={accesses}
            aiIndexes={ai}
            prevItems={prevObj?.items}
            bars={mode === 'bars'}
          />
        </>
      )
    }
    case 'heap':
      return (
        <>
          <ArrayView items={obj.items} heap={heap} ints={{}} accesses={accesses} aiIndexes={ai} prevItems={prevObj?.items} showPointers={false} />
          <div className="sub-label">as a binary tree (smallest on top)</div>
          <HeapTree items={obj.items} heap={heap} aiIndexes={ai} />
        </>
      )
    case 'stack':
      return <StackView items={obj.items} heap={heap} accesses={accesses} aiIndexes={ai} />
    case 'queue':
      return <QueueView items={obj.items} heap={heap} aiIndexes={ai} />
    case 'unionfind':
      return (
        <>
          <ArrayView items={obj.items} heap={heap} ints={scene.ints} accesses={accesses} aiIndexes={ai} prevItems={prevObj?.items} />
          <div className="sub-label">as a forest (each node points to its parent)</div>
          <UnionFindForest items={obj.items} ints={scene.ints} aiIndexes={ai} />
        </>
      )
    case 'grid':
      return (
        <GridView
          rows={rowsOf(obj, heap)}
          heap={heap}
          scene={scene}
          names={names}
          prevRows={prevObj && prevHeap ? rowsOf(prevObj, prevHeap) : null}
        />
      )
    case 'intervals':
      return <IntervalsView items={obj.items} heap={heap} ints={scene.ints} aiIndexes={ai} />
    case 'set':
      return <SetView obj={obj} heap={heap} prevObj={prevObj} keyStates={accessedKeys(scene, names)} aiKeys={aiKeys(scene, names)} />
    case 'hashmap':
      return <HashMapView obj={obj} heap={heap} prevObj={prevObj} keyStates={accessedKeys(scene, names)} aiKeys={aiKeys(scene, names)} />
    case 'graph': {
      const mode = view ?? 'graph'
      return (
        <>
          <Toggle options={['graph', 'table']} value={mode} onChange={setView} />
          {mode === 'graph' ? (
            <AdjacencyGraph obj={obj} scene={scene} names={names} id={id} />
          ) : (
            <HashMapView obj={obj} heap={heap} prevObj={prevObj} keyStates={accessedKeys(scene, names)} aiKeys={aiKeys(scene, names)} />
          )}
        </>
      )
    }
    case 'object':
      return <ObjectView obj={obj} names={names} scene={scene} prevHeap={prevHeap} />
    default:
      return <code>{fmt({ t: 'ref', id }, heap)}</code>
  }
}

/** A class instance (MinStack, LRUCache, ...): each attribute drawn on its own. */
function ObjectView({ obj, names, scene, prevHeap }) {
  const heap = scene.heap
  const base = names[0]
  return (
    <div className="object">
      {Object.entries(obj.attrs).map(([attr, v]) => {
        const target = isRef(v) ? heap[v.id] : null
        const path = `${base}.${attr}`
        if (target && !nodeKind(target)) {
          const kind = classify(target, heap, attr)
          return (
            <div key={attr} className="object-field is-block">
              <div className="object-name">
                .{attr} <span className="card-kind">{KIND_LABEL[kind] ?? kind}</span>
              </div>
              <StructureBody id={v.id} obj={target} kind={kind} names={[path, attr]} scene={scene} prevHeap={prevHeap} />
            </div>
          )
        }
        return (
          <div key={attr} className="object-field">
            <span className="object-name">.{attr}</span>
            <span className="object-value">{fmt(v, heap)}</span>
          </div>
        )
      })}
    </div>
  )
}

/** Gemini's value for this card's container, shown in the card header. */
function AiValueTag({ value }) {
  if (value == null) return null
  return (
    <span className="card-ai-value" title={value}>
      ✦ <code>{value}</code>
    </span>
  )
}

export function StructureCard({ structure, scene, prevHeap, changed, focus = '' }) {
  const { id, obj, kind, names } = structure
  const title = names.join(' = ')
  return (
    <section className={`card ${changed ? 'is-changed' : ''} ${aiTargeted(scene, names) ? 'is-ai' : ''} ${focus}`}>
      <header className="card-head">
        <span className="card-name">{title}</span>
        <span className="card-kind">{kind === 'object' ? obj.cls : KIND_LABEL[kind] ?? kind}</span>
        <AiValueTag value={aiValue(scene, names)} />
        {obj.len !== undefined && <span className="card-meta">len {obj.len}</span>}
      </header>
      <StructureBody id={id} obj={obj} kind={kind} names={names} scene={scene} prevHeap={prevHeap} />
    </section>
  )
}

/** A string that the code indexes into (s[l], s[r]) drawn as character blocks. */
export function StringCard({ name, value, scene, prevValue, focus = '' }) {
  const items = [...value].map((ch) => ({ t: 'str', v: ch }))
  const prevItems = prevValue === undefined ? undefined : [...prevValue].map((ch) => ({ t: 'str', v: ch }))
  return (
    <section className={`card ${aiTargeted(scene, [name]) ? 'is-ai' : ''} ${focus}`}>
      <header className="card-head">
        <span className="card-name">{name}</span>
        <span className="card-kind">string</span>
        <AiValueTag value={aiValue(scene, [name])} />
        <span className="card-meta">len {value.length}</span>
      </header>
      <ArrayView items={items} heap={scene.heap} ints={scene.ints} accesses={accessesFor(scene, [name])} aiIndexes={aiIndexes(scene, [name])} prevItems={prevItems} />
    </section>
  )
}
