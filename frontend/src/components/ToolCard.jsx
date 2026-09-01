import { Link } from 'react-router-dom'
import { ToolIcon } from './Icons'

export default function ToolCard({ tool }) {
  return (
    <Link to={`/tools/${tool.id}`} className="tool-card">
      <ToolIcon name={tool.icon} />
      <h3>{tool.name}</h3>
      <p>{tool.description}</p>
    </Link>
  )
}
