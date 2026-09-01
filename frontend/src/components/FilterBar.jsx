import { CATEGORIES } from '../data/tools'

export default function FilterBar({ active, onChange }) {
  return (
    <div className="filters">
      {CATEGORIES.map((c) => (
        <button
          key={c.id}
          type="button"
          className={active === c.id ? 'pill active' : 'pill'}
          onClick={() => onChange(c.id)}
        >
          {c.label}
        </button>
      ))}
    </div>
  )
}
