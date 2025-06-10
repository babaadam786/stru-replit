import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  ChevronDown,
  ChevronRight,
  Circle,
  Minus,
  Square,
  Triangle,
  Eye,
  EyeOff,
  Edit,
  Trash2
} from 'lucide-react'
import { useAppStore } from '../../store/appStore'

const ModelTree = () => {
  const {
    currentModel,
    selectedNodes,
    selectedElements,
    selectNodes,
    selectElements,
    removeNode,
    removeElement
  } = useAppStore()

  const [expandedSections, setExpandedSections] = useState({
    nodes: true,
    elements: true,
    materials: true,
    loads: true,
    constraints: true
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const handleNodeSelect = (nodeId: number) => {
    selectNodes([nodeId])
    selectElements([])
  }

  const handleElementSelect = (elementId: number) => {
    selectElements([elementId])
    selectNodes([])
  }

  const TreeSection = ({ 
    title, 
    count, 
    isExpanded, 
    onToggle, 
    children 
  }: {
    title: string
    count: number
    isExpanded: boolean
    onToggle: () => void
    children: React.ReactNode
  }) => (
    <div className="mb-2">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-2 text-sm font-medium text-secondary-700 hover:bg-secondary-50 rounded"
      >
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
          <span>{title}</span>
          <span className="text-xs text-secondary-500 bg-secondary-100 px-2 py-0.5 rounded-full">
            {count}
          </span>
        </div>
      </button>
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="ml-4 mt-1 space-y-1"
        >
          {children}
        </motion.div>
      )}
    </div>
  )

  const NodeItem = ({ node }: { node: any }) => (
    <div
      className={`flex items-center justify-between p-2 text-sm rounded cursor-pointer transition-colors ${
        selectedNodes.includes(node.id)
          ? 'bg-primary-100 text-primary-700 border border-primary-200'
          : 'hover:bg-secondary-50'
      }`}
      onClick={() => handleNodeSelect(node.id)}
    >
      <div className="flex items-center gap-2">
        <Circle className="w-3 h-3 text-blue-500" />
        <span>Node {node.id}</span>
        <span className="text-xs text-secondary-500">
          ({node.x.toFixed(1)}, {node.y.toFixed(1)}, {node.z.toFixed(1)})
        </span>
      </div>
      <div className="flex items-center gap-1">
        <button
          onClick={(e) => {
            e.stopPropagation()
            // TODO: Edit node
          }}
          className="p-1 hover:bg-secondary-200 rounded"
          title="Edit Node"
        >
          <Edit className="w-3 h-3" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation()
            removeNode(node.id)
          }}
          className="p-1 hover:bg-red-200 rounded text-red-600"
          title="Delete Node"
        >
          <Trash2 className="w-3 h-3" />
        </button>
      </div>
    </div>
  )

  const ElementItem = ({ element }: { element: any }) => {
    const material = currentModel.materials.find(m => m.id === element.materialId)
    const section = currentModel.sections.find(s => s.id === element.sectionId)
    
    return (
      <div
        className={`flex items-center justify-between p-2 text-sm rounded cursor-pointer transition-colors ${
          selectedElements.includes(element.id)
            ? 'bg-primary-100 text-primary-700 border border-primary-200'
            : 'hover:bg-secondary-50'
        }`}
        onClick={() => handleElementSelect(element.id)}
      >
        <div className="flex items-center gap-2">
          <Minus className="w-3 h-3 text-green-500" />
          <span>{element.type} {element.id}</span>
          <span className="text-xs text-secondary-500">
            [{element.nodes.join('-')}]
          </span>
          {material && (
            <span className="text-xs text-secondary-500">
              {material.name}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation()
              // TODO: Edit element
            }}
            className="p-1 hover:bg-secondary-200 rounded"
            title="Edit Element"
          >
            <Edit className="w-3 h-3" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              removeElement(element.id)
            }}
            className="p-1 hover:bg-red-200 rounded text-red-600"
            title="Delete Element"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>
    )
  }

  const MaterialItem = ({ material }: { material: any }) => (
    <div className="flex items-center justify-between p-2 text-sm hover:bg-secondary-50 rounded">
      <div className="flex items-center gap-2">
        <Square className="w-3 h-3 text-purple-500" />
        <span>{material.name}</span>
        <span className="text-xs text-secondary-500">
          E = {(material.E / 1e9).toFixed(0)} GPa
        </span>
      </div>
      <div className="flex items-center gap-1">
        <button
          className="p-1 hover:bg-secondary-200 rounded"
          title="Edit Material"
        >
          <Edit className="w-3 h-3" />
        </button>
      </div>
    </div>
  )

  const LoadItem = ({ load }: { load: any }) => {
    const node = currentModel.nodes.find(n => n.id === load.nodeId)
    const maxForce = Math.max(...load.values.slice(0, 3).map(Math.abs))
    
    return (
      <div className="flex items-center justify-between p-2 text-sm hover:bg-secondary-50 rounded">
        <div className="flex items-center gap-2">
          <Triangle className="w-3 h-3 text-red-500" />
          <span>Load {load.id}</span>
          {node && (
            <span className="text-xs text-secondary-500">
              @ Node {node.id}
            </span>
          )}
          <span className="text-xs text-secondary-500">
            {maxForce.toFixed(0)}N
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            className="p-1 hover:bg-secondary-200 rounded"
            title="Edit Load"
          >
            <Edit className="w-3 h-3" />
          </button>
          <button
            className="p-1 hover:bg-red-200 rounded text-red-600"
            title="Delete Load"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>
    )
  }

  const ConstraintItem = ({ constraint }: { constraint: any }) => {
    const node = currentModel.nodes.find(n => n.id === constraint.nodeId)
    const constrainedDofs = constraint.dofs.filter(Boolean).length
    
    return (
      <div className="flex items-center justify-between p-2 text-sm hover:bg-secondary-50 rounded">
        <div className="flex items-center gap-2">
          <Square className="w-3 h-3 text-green-500" />
          <span>Support {constraint.id}</span>
          {node && (
            <span className="text-xs text-secondary-500">
              @ Node {node.id}
            </span>
          )}
          <span className="text-xs text-secondary-500">
            {constrainedDofs} DOF
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            className="p-1 hover:bg-secondary-200 rounded"
            title="Edit Constraint"
          >
            <Edit className="w-3 h-3" />
          </button>
          <button
            className="p-1 hover:bg-red-200 rounded text-red-600"
            title="Delete Constraint"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full p-4 overflow-y-auto scrollbar-thin">
      <div className="mb-4">
        <h3 className="font-medium text-secondary-900 mb-2">Model Tree</h3>
        <div className="text-xs text-secondary-500">
          Total: {currentModel.nodes.length + currentModel.elements.length} objects
        </div>
      </div>

      <div className="space-y-1">
        <TreeSection
          title="Nodes"
          count={currentModel.nodes.length}
          isExpanded={expandedSections.nodes}
          onToggle={() => toggleSection('nodes')}
        >
          {currentModel.nodes.length > 0 ? (
            currentModel.nodes.map(node => (
              <NodeItem key={node.id} node={node} />
            ))
          ) : (
            <div className="text-xs text-secondary-500 p-2">No nodes</div>
          )}
        </TreeSection>

        <TreeSection
          title="Elements"
          count={currentModel.elements.length}
          isExpanded={expandedSections.elements}
          onToggle={() => toggleSection('elements')}
        >
          {currentModel.elements.length > 0 ? (
            currentModel.elements.map(element => (
              <ElementItem key={element.id} element={element} />
            ))
          ) : (
            <div className="text-xs text-secondary-500 p-2">No elements</div>
          )}
        </TreeSection>

        <TreeSection
          title="Materials"
          count={currentModel.materials.length}
          isExpanded={expandedSections.materials}
          onToggle={() => toggleSection('materials')}
        >
          {currentModel.materials.length > 0 ? (
            currentModel.materials.map(material => (
              <MaterialItem key={material.id} material={material} />
            ))
          ) : (
            <div className="text-xs text-secondary-500 p-2">No materials</div>
          )}
        </TreeSection>

        <TreeSection
          title="Loads"
          count={currentModel.loads.length}
          isExpanded={expandedSections.loads}
          onToggle={() => toggleSection('loads')}
        >
          {currentModel.loads.length > 0 ? (
            currentModel.loads.map(load => (
              <LoadItem key={load.id} load={load} />
            ))
          ) : (
            <div className="text-xs text-secondary-500 p-2">No loads</div>
          )}
        </TreeSection>

        <TreeSection
          title="Constraints"
          count={currentModel.constraints.length}
          isExpanded={expandedSections.constraints}
          onToggle={() => toggleSection('constraints')}
        >
          {currentModel.constraints.length > 0 ? (
            currentModel.constraints.map(constraint => (
              <ConstraintItem key={constraint.id} constraint={constraint} />
            ))
          ) : (
            <div className="text-xs text-secondary-500 p-2">No constraints</div>
          )}
        </TreeSection>
      </div>
    </div>
  )
}

export default ModelTree