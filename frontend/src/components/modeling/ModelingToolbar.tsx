import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  MousePointer,
  Move,
  Plus,
  Minus,
  Square,
  Circle,
  Triangle,
  Anchor,
  Zap,
  Grid3X3,
  Eye,
  EyeOff,
  Undo,
  Redo,
  Save,
  FolderOpen,
  Download,
  Upload
} from 'lucide-react'
import { useAppStore } from '../../store/appStore'

const ModelingToolbar = () => {
  const [activeTool, setActiveTool] = useState<string>('select')
  const [showGrid, setShowGrid] = useState(true)
  const [showLoads, setShowLoads] = useState(true)
  const [showConstraints, setShowConstraints] = useState(true)

  const { currentModel, clearModel, exportModel } = useAppStore()

  const tools = [
    { id: 'select', icon: MousePointer, label: 'Select', shortcut: 'S' },
    { id: 'move', icon: Move, label: 'Move', shortcut: 'M' },
    { id: 'node', icon: Circle, label: 'Add Node', shortcut: 'N' },
    { id: 'element', icon: Minus, label: 'Add Element', shortcut: 'E' },
    { id: 'load', icon: Triangle, label: 'Add Load', shortcut: 'L' },
    { id: 'constraint', icon: Anchor, label: 'Add Constraint', shortcut: 'C' },
  ]

  const viewOptions = [
    { id: 'grid', icon: Grid3X3, label: 'Grid', active: showGrid, toggle: () => setShowGrid(!showGrid) },
    { id: 'loads', icon: Triangle, label: 'Loads', active: showLoads, toggle: () => setShowLoads(!showLoads) },
    { id: 'constraints', icon: Anchor, label: 'Constraints', active: showConstraints, toggle: () => setShowConstraints(!showConstraints) },
  ]

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving model...')
  }

  const handleLoad = () => {
    // TODO: Implement load functionality
    console.log('Loading model...')
  }

  const handleExport = () => {
    const model = exportModel()
    const dataStr = JSON.stringify(model, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'structural_model.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleImport = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          try {
            const model = JSON.parse(e.target?.result as string)
            // TODO: Implement import functionality
            console.log('Importing model:', model)
          } catch (error) {
            console.error('Failed to import model:', error)
          }
        }
        reader.readAsText(file)
      }
    }
    input.click()
  }

  const handleClear = () => {
    if (confirm('Are you sure you want to clear the model? This action cannot be undone.')) {
      clearModel()
    }
  }

  return (
    <div className="h-12 bg-white border-b border-secondary-200 flex items-center justify-between px-4">
      {/* Left Section - Tools */}
      <div className="flex items-center gap-1">
        {tools.map((tool) => (
          <motion.button
            key={tool.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTool(tool.id)}
            className={`p-2 rounded-lg transition-colors ${
              activeTool === tool.id
                ? 'bg-primary-100 text-primary-700 border border-primary-200'
                : 'hover:bg-secondary-100 text-secondary-600'
            }`}
            title={`${tool.label} (${tool.shortcut})`}
          >
            <tool.icon className="w-4 h-4" />
          </motion.button>
        ))}
        
        <div className="w-px h-6 bg-secondary-300 mx-2" />
        
        {/* View Options */}
        {viewOptions.map((option) => (
          <motion.button
            key={option.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={option.toggle}
            className={`p-2 rounded-lg transition-colors ${
              option.active
                ? 'bg-green-100 text-green-700 border border-green-200'
                : 'hover:bg-secondary-100 text-secondary-600'
            }`}
            title={`Toggle ${option.label}`}
          >
            <option.icon className="w-4 h-4" />
          </motion.button>
        ))}
      </div>

      {/* Center Section - Model Info */}
      <div className="flex items-center gap-4 text-sm text-secondary-600">
        <span>Tool: {tools.find(t => t.id === activeTool)?.label}</span>
        <span>•</span>
        <span>Nodes: {currentModel.nodes.length}</span>
        <span>•</span>
        <span>Elements: {currentModel.elements.length}</span>
      </div>

      {/* Right Section - Actions */}
      <div className="flex items-center gap-1">
        <button
          className="btn btn-ghost btn-sm"
          title="Undo (Ctrl+Z)"
        >
          <Undo className="w-4 h-4" />
        </button>
        
        <button
          className="btn btn-ghost btn-sm"
          title="Redo (Ctrl+Y)"
        >
          <Redo className="w-4 h-4" />
        </button>
        
        <div className="w-px h-6 bg-secondary-300 mx-2" />
        
        <button
          onClick={handleSave}
          className="btn btn-ghost btn-sm"
          title="Save Model (Ctrl+S)"
        >
          <Save className="w-4 h-4" />
        </button>
        
        <button
          onClick={handleLoad}
          className="btn btn-ghost btn-sm"
          title="Load Model"
        >
          <FolderOpen className="w-4 h-4" />
        </button>
        
        <button
          onClick={handleExport}
          className="btn btn-ghost btn-sm"
          title="Export Model"
        >
          <Download className="w-4 h-4" />
        </button>
        
        <button
          onClick={handleImport}
          className="btn btn-ghost btn-sm"
          title="Import Model"
        >
          <Upload className="w-4 h-4" />
        </button>
        
        <div className="w-px h-6 bg-secondary-300 mx-2" />
        
        <button
          onClick={handleClear}
          className="btn btn-ghost btn-sm text-red-600 hover:bg-red-50"
          title="Clear Model"
        >
          Clear
        </button>
      </div>
    </div>
  )
}

export default ModelingToolbar