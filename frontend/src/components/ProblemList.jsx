import { useMemo, useState } from 'react'

/** NeetCode 150 sidebar: search plus collapsible categories. */
function ProblemList({ problems, selectedId, onSelect, visited }) {
  const [query, setQuery] = useState('')
  const [collapsed, setCollapsed] = useState(() => new Set())

  const groups = useMemo(() => {
    const q = query.trim().toLowerCase()
    const out = []
    for (const p of problems) {
      if (q && !p.title.toLowerCase().includes(q) && !String(p.num).startsWith(q)) continue
      let group = out.at(-1)
      if (!group || group.category !== p.category) {
        group = { category: p.category, items: [] }
        out.push(group)
      }
      group.items.push(p)
    }
    return out
  }, [problems, query])

  const toggle = (category) =>
    setCollapsed((prev) => {
      const next = new Set(prev)
      if (next.has(category)) next.delete(category)
      else next.add(category)
      return next
    })

  return (
    <nav className="problems" aria-label="NeetCode 150 problems">
      <div className="problems-search">
        <input
          type="search"
          placeholder={`Search ${problems.length} problems…`}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <span className="problems-progress">
          {visited.size} / {problems.length} opened
        </span>
      </div>
      <div className="problems-scroll">
        {groups.map((g) => {
          const open = query || !collapsed.has(g.category)
          return (
            <div key={g.category} className="problem-group">
              <button type="button" className="problem-group-head" onClick={() => toggle(g.category)} aria-expanded={!!open}>
                <span className="chevron">{open ? '▾' : '▸'}</span>
                {g.category}
                <span className="problem-count">
                  {g.items.filter((p) => visited.has(p.id)).length}/{g.items.length}
                </span>
              </button>
              {open &&
                g.items.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    className={`problem ${p.id === selectedId ? 'is-selected' : ''}`}
                    onClick={() => onSelect(p.id)}
                  >
                    <span className={`diff-dot is-${p.difficulty.toLowerCase()}`} title={p.difficulty} />
                    <span className="problem-title">{p.title}</span>
                    {visited.has(p.id) && <span className="problem-check">✓</span>}
                  </button>
                ))}
            </div>
          )
        })}
        {!groups.length && <div className="empty">No problems match “{query}”.</div>}
      </div>
    </nav>
  )
}

export default ProblemList
