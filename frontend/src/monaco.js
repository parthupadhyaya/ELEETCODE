import { loader } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'
import EditorWorker from 'monaco-editor/editor/editor.worker?worker'

// Bundle Monaco with Vite instead of letting @monaco-editor/react pull it from a CDN.
// Python has no language worker, so the base editor worker covers everything.
self.MonacoEnvironment = {
  getWorker: () => new EditorWorker(),
}

loader.config({ monaco })
