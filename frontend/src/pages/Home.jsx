import { useState } from 'react'
import Hero from '../components/Hero'
import FilterBar from '../components/FilterBar'
import ToolGrid from '../components/ToolGrid'
import { TOOLS } from '../data/tools'

export default function Home() {
  const [category, setCategory] = useState('all')
  const tools =
    category === 'all' ? TOOLS : TOOLS.filter((t) => t.category === category)

  return (
    <main className="page">
      <Hero />
      <FilterBar active={category} onChange={setCategory} />
      <ToolGrid tools={tools} />
    </main>
  )
}
