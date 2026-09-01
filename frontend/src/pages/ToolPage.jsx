import { useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getTool } from '../data/tools'
import { runTool } from '../api'
import { ToolIcon } from '../components/Icons'

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function ToolPage() {
  const { id } = useParams()
  const tool = getTool(id)
  const inputRef = useRef(null)

  const [files, setFiles] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [drag, setDrag] = useState(false)

  const [splitMode, setSplitMode] = useState('individual')
  const [ranges, setRanges] = useState('')
  const [compressLevel, setCompressLevel] = useState('recommended')
  const [jpgMode, setJpgMode] = useState('page')
  const [excelLayout, setExcelLayout] = useState('multiple')

  const minFiles = tool?.minFiles || 1

  const ready = useMemo(() => {
    if (!tool) return false
    if (files.length < minFiles) return false
    if (tool.extra === 'split' && splitMode === 'range' && !ranges.trim()) return false
    return true
  }, [tool, files, minFiles, splitMode, ranges])

  if (!tool) {
    return (
      <main className="page tool-page">
        <h1>Tool not found</h1>
        <p>This is not part of DamnPDF v1.</p>
        <Link to="/" className="btn-ghost">Back to all tools</Link>
      </main>
    )
  }

  function addFiles(list) {
    const next = Array.from(list)
    setResult(null)
    setError('')
    setFiles(tool.multiple ? [...files, ...next] : next.slice(0, 1))
  }

  function removeFile(index) {
    setFiles(files.filter((_, i) => i !== index))
  }

  async function process() {
    setBusy(true)
    setError('')
    setResult(null)
    try {
      const body = new FormData()
      if (tool.multiple) {
        files.forEach((f) => body.append(tool.fileField, f))
      } else {
        body.append(tool.fileField, files[0])
      }

      let query
      if (tool.extra === 'split') {
        body.append('mode', splitMode)
        if (splitMode === 'range') body.append('ranges', ranges.trim())
      }
      if (tool.extra === 'compress') body.append('level', compressLevel)
      if (tool.extra === 'jpg') body.append('mode', jpgMode)
      if (tool.extra === 'excel') query = { layout: excelLayout }

      const out = await runTool({ endpoint: tool.endpoint, body, query })
      const url = URL.createObjectURL(out.blob)
      setResult({ url, filename: out.filename, size: out.blob.size })
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="page tool-page">
      <div className="tool-hero">
        <ToolIcon name={tool.icon} />
        <h1>{tool.name}</h1>
        <p>{tool.description}</p>
      </div>

      <div
        className={`dropzone ${drag ? 'dragging' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDrag(true)
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDrag(false)
          addFiles(e.dataTransfer.files)
        }}
      >
        <p className="drop-title">Drop files here</p>
        <p className="drop-sub">or</p>
        <button type="button" className="btn-red" onClick={() => inputRef.current?.click()}>
          {tool.cta}
        </button>
        <input
          ref={inputRef}
          type="file"
          hidden
          accept={tool.accept}
          multiple={tool.multiple}
          onChange={(e) => addFiles(e.target.files)}
        />
      </div>

      {files.length > 0 && (
        <ul className="file-list">
          {files.map((f, i) => (
            <li key={`${f.name}-${i}`}>
              <span>
                {f.name} <em>{formatSize(f.size)}</em>
              </span>
              <button type="button" onClick={() => removeFile(i)}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}

      {tool.extra === 'split' && (
        <div className="options">
          <label>
            <input
              type="radio"
              name="split-mode"
              checked={splitMode === 'individual'}
              onChange={() => setSplitMode('individual')}
            />
            Split into individual pages
          </label>
          <label>
            <input
              type="radio"
              name="split-mode"
              checked={splitMode === 'range'}
              onChange={() => setSplitMode('range')}
            />
            Extract page range
          </label>
          {splitMode === 'range' && (
            <input
              className="text-input"
              placeholder="e.g. 1-3,5,7-9"
              value={ranges}
              onChange={(e) => setRanges(e.target.value)}
            />
          )}
        </div>
      )}

      {tool.extra === 'compress' && (
        <div className="options">
          {[
            ['extreme', 'Extreme compression'],
            ['recommended', 'Recommended'],
            ['less', 'Less compression, better quality'],
          ].map(([value, label]) => (
            <label key={value}>
              <input
                type="radio"
                name="compress"
                checked={compressLevel === value}
                onChange={() => setCompressLevel(value)}
              />
              {label}
            </label>
          ))}
        </div>
      )}

      {tool.extra === 'jpg' && (
        <div className="options">
          <label>
            <input
              type="radio"
              name="jpg"
              checked={jpgMode === 'page'}
              onChange={() => setJpgMode('page')}
            />
            Convert each page to JPG
          </label>
          <label>
            <input
              type="radio"
              name="jpg"
              checked={jpgMode === 'extract'}
              onChange={() => setJpgMode('extract')}
            />
            Extract embedded images
          </label>
        </div>
      )}

      {tool.extra === 'excel' && (
        <div className="options">
          <label>
            <input
              type="radio"
              name="excel"
              checked={excelLayout === 'multiple'}
              onChange={() => setExcelLayout('multiple')}
            />
            One sheet per table
          </label>
          <label>
            <input
              type="radio"
              name="excel"
              checked={excelLayout === 'one'}
              onChange={() => setExcelLayout('one')}
            />
            All tables in one sheet
          </label>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      <div className="actions">
        <button type="button" className="btn-red" disabled={!ready || busy} onClick={process}>
          {busy ? 'Working…' : tool.name}
        </button>
        {result && (
          <a className="btn-ghost" href={result.url} download={result.filename}>
            Download {result.filename} ({formatSize(result.size)})
          </a>
        )}
      </div>
    </main>
  )
}
