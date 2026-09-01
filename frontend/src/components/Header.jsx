import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { LogoMark } from './Icons'
import { TOOLS } from '../data/tools'

export default function Header() {
  const [open, setOpen] = useState(false)
  const convertTools = TOOLS.filter((t) => t.category === 'convert')

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="logo" onClick={() => setOpen(false)}>
          <LogoMark />
          <span className="logo-text">
            Damn<span>PDF</span>
          </span>
        </Link>

        <nav className="nav">
          <NavLink to="/tools/merge-pdf">MERGE PDF</NavLink>
          <NavLink to="/tools/split-pdf">SPLIT PDF</NavLink>
          <NavLink to="/tools/compress-pdf">COMPRESS PDF</NavLink>
          <div className="nav-drop">
            <button type="button" className="nav-drop-btn">
              CONVERT PDF <span className="caret">▾</span>
            </button>
            <div className="nav-menu">
              {convertTools.map((t) => (
                <Link key={t.id} to={`/tools/${t.id}`}>
                  {t.name}
                </Link>
              ))}
            </div>
          </div>
          <Link to="/">ALL PDF TOOLS</Link>
          <NavLink to="/privacy">PRIVACY</NavLink>
        </nav>

        <button
          type="button"
          className="menu-btn"
          aria-label="Open menu"
          onClick={() => setOpen((v) => !v)}
        >
          <span />
          <span />
          <span />
        </button>
      </div>

      {open && (
        <div className="mobile-nav">
          <NavLink to="/tools/merge-pdf" onClick={() => setOpen(false)}>Merge PDF</NavLink>
          <NavLink to="/tools/split-pdf" onClick={() => setOpen(false)}>Split PDF</NavLink>
          <NavLink to="/tools/compress-pdf" onClick={() => setOpen(false)}>Compress PDF</NavLink>
          {convertTools.map((t) => (
            <NavLink key={t.id} to={`/tools/${t.id}`} onClick={() => setOpen(false)}>
              {t.name}
            </NavLink>
          ))}
          <NavLink to="/privacy" onClick={() => setOpen(false)}>Privacy</NavLink>
        </div>
      )}
    </header>
  )
}
