import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ModelingWorkspace from './pages/ModelingWorkspace'
import AnalysisResults from './pages/AnalysisResults'
import ProjectManager from './pages/ProjectManager'
import MaterialDatabase from './pages/MaterialDatabase'
import AIAssistant from './pages/AIAssistant'
import Settings from './pages/Settings'
import { useAppStore } from './store/appStore'

function App() {
  const { theme } = useAppStore()

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="modeling" element={<ModelingWorkspace />} />
          <Route path="analysis" element={<AnalysisResults />} />
          <Route path="projects" element={<ProjectManager />} />
          <Route path="materials" element={<MaterialDatabase />} />
          <Route path="ai-assistant" element={<AIAssistant />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </div>
  )
}

export default App