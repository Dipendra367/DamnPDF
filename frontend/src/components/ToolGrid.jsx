import ToolCard from './ToolCard'

export default function ToolGrid({ tools }) {
  return (
    <div className="tool-grid">
      {tools.map((tool) => (
        <ToolCard key={tool.id} tool={tool} />
      ))}
    </div>
  )
}
