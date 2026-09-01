function filenameFromDisposition(header, fallback) {
  if (!header) return fallback
  const star = /filename\*=UTF-8''([^;]+)/i.exec(header)
  if (star) return decodeURIComponent(star[1])
  const plain = /filename="?([^";]+)"?/i.exec(header)
  if (plain) return plain[1]
  return fallback
}

// In dev the Vite proxy forwards /api to the backend; in production set
// VITE_API_URL (e.g. https://damnpdf.up.railway.app) at build time.
const API_BASE = import.meta.env.VITE_API_URL || ''

export async function runTool({ endpoint, body, query }) {
  const url = query ? `${API_BASE}${endpoint}?${new URLSearchParams(query)}` : `${API_BASE}${endpoint}`
  const res = await fetch(url, { method: 'POST', body })

  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const data = await res.json()
      if (typeof data.detail === 'string') detail = data.detail
      else if (Array.isArray(data.detail)) detail = data.detail.map((d) => d.msg || d).join(', ')
    } catch {
      try {
        detail = (await res.text()) || detail
      } catch {
        /* keep default */
      }
    }
    throw new Error(detail)
  }

  const blob = await res.blob()
  const filename = filenameFromDisposition(
    res.headers.get('content-disposition'),
    'download',
  )
  return { blob, filename, headers: res.headers }
}
