import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  // /api/animate waits on Gemini, which can take a while
  timeout: 90_000,
})

// Errors read "404 Not Found" (App.jsx checks the status prefix), or the
// network error message when the backend isn't reachable
async function request(config) {
  try {
    const res = await api.request(config)
    return res.data
  } catch (err) {
    if (err.response) throw new Error(`${err.response.status} ${err.response.statusText}`, { cause: err })
    throw err
  }
}

export const fetchProblems = () => request({ url: '/problems' })

export const fetchProblem = (id) => request({ url: `/problems/${encodeURIComponent(id)}` })

/** Trace the code (fast, no Gemini). Resolves to {steps, loops, error, ...}. */
export const traceCode = (code, run) => request({ url: '/trace', method: 'POST', data: { code, run } })

/**
 * Get Gemini's animation script for the code (slow). Resolves to `animation`
 * (array of steps, or null) and `animation_error`.
 */
export const animateCode = (code, run) => request({ url: '/animate', method: 'POST', data: { code, run } })
