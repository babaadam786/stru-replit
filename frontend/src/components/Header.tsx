import { motion } from 'framer-motion'
import {
  Bell,
  Search,
  User,
  Moon,
  Sun,
  Save,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'
import { useAppStore } from '../store/appStore'

const Header = () => {
  const { 
    theme, 
    setTheme, 
    activeProject, 
    isAnalyzing,
    currentModel 
  } = useAppStore()

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving project...')
  }

  const handleAnalyze = () => {
    // TODO: Implement analysis functionality
    console.log('Starting analysis...')
  }

  return (
    <header className="h-16 bg-white border-b border-secondary-200 flex items-center justify-between px-6">
      {/* Left Section */}
      <div className="flex items-center gap-4">
        {/* Project Info */}
        {activeProject && (
          <div className="flex items-center gap-3">
            <div>
              <h1 className="text-lg font-semibold text-secondary-900">
                {activeProject.name}
              </h1>
              <p className="text-xs text-secondary-500">
                {activeProject.projectType} • {activeProject.designCode}
              </p>
            </div>
          </div>
        )}

        {/* Model Stats */}
        <div className="flex items-center gap-4 text-sm text-secondary-600">
          <span>Nodes: {currentModel.nodes.length}</span>
          <span>Elements: {currentModel.elements.length}</span>
          <span>Materials: {currentModel.materials.length}</span>
        </div>
      </div>

      {/* Center Section - Quick Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleSave}
          className="btn btn-ghost btn-sm"
          title="Save Project"
        >
          <Save className="w-4 h-4" />
          Save
        </button>

        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing || currentModel.elements.length === 0}
          className={`btn btn-sm ${
            isAnalyzing ? 'btn-secondary' : 'btn-primary'
          }`}
          title={isAnalyzing ? 'Analysis Running' : 'Run Analysis'}
        >
          {isAnalyzing ? (
            <>
              <Pause className="w-4 h-4" />
              Running...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Analyze
            </>
          )}
        </button>

        <button
          className="btn btn-ghost btn-sm"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-400" />
          <input
            type="text"
            placeholder="Search..."
            className="input pl-10 pr-4 py-2 w-64 text-sm"
          />
        </div>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          className="btn btn-ghost btn-sm"
          title="Toggle Theme"
        >
          {theme === 'light' ? (
            <Moon className="w-4 h-4" />
          ) : (
            <Sun className="w-4 h-4" />
          )}
        </button>

        {/* Notifications */}
        <button className="btn btn-ghost btn-sm relative" title="Notifications">
          <Bell className="w-4 h-4" />
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* User Menu */}
        <div className="flex items-center gap-2">
          <button className="btn btn-ghost btn-sm" title="User Menu">
            <User className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header