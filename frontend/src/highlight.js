// Tiny Python syntax highlighter for the editor overlay. Returns HTML.

const KEYWORDS = new Set(
  'and as assert break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield None True False'.split(' '),
)
const BUILTINS = new Set(
  'len range enumerate zip min max sum sorted reversed abs int str float list dict set tuple print map filter any all ord chr divmod isinstance super self deque defaultdict Counter heapq math bisect float'.split(' '),
)

const TOKEN = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_]\w*)/g

const escape = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

export function highlightPython(code) {
  let out = ''
  let last = 0
  let prevWord = ''
  for (const m of code.matchAll(TOKEN)) {
    out += escape(code.slice(last, m.index))
    last = m.index + m[0].length
    const text = escape(m[0])
    if (m[1]) out += `<span class="tok-comment">${text}</span>`
    else if (m[2]) out += `<span class="tok-string">${text}</span>`
    else if (m[3]) out += `<span class="tok-number">${text}</span>`
    else if (KEYWORDS.has(m[4])) out += `<span class="tok-keyword">${text}</span>`
    else if (prevWord === 'def' || prevWord === 'class') out += `<span class="tok-def">${text}</span>`
    else if (BUILTINS.has(m[4])) out += `<span class="tok-builtin">${text}</span>`
    else out += text
    if (m[4]) prevWord = m[4]
  }
  return out + escape(code.slice(last))
}
