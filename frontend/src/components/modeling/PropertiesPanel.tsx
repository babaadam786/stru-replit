import { useState } from 'react'
import { motion } from 'framer-motion'
import { Save, X, Plus } from 'lucide-react'
import { useAppStore } from '../../store/appStore'

const PropertiesPanel = () => {
  const {
    currentModel,
    selectedNodes,
    selectedElements,
    updateNode,
    updateElement,
    addNode,
    addElement,
    addMaterial,
    addSection,
    addLoad,
    addConstraint
  } = useAppStore()

  const [activeTab, setActiveTab] = useState<'selection' | 'create'>('selection')

  const selectedNode = selectedNodes.length === 1 
    ? currentModel.nodes.find(n => n.id === selectedNodes[0])
    : null

  const selectedElement = selectedElements.length === 1
    ? currentModel.elements.find(e => e.id === selectedElements[0])
    : null

  const NodeProperties = ({ node }: { node: any }) => {
    const [coords, setCoords] = useState({
      x: node.x,
      y: node.y,
      z: node.z
    })

    const handleSave = () => {
      updateNode(node.id, coords)
    }

    return (
      <div className="space-y-4">
        <h4 className="font-medium">Node {node.id} Properties</h4>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              X Coordinate (m)
            </label>
            <input
              type="number"
              step="0.1"
              value={coords.x}
              onChange={(e) => setCoords(prev => ({ ...prev, x: parseFloat(e.target.value) || 0 }))}
              className="input w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Y Coordinate (m)
            </label>
            <input
              type="number"
              step="0.1"
              value={coords.y}
              onChange={(e) => setCoords(prev => ({ ...prev, y: parseFloat(e.target.value) || 0 }))}
              className="input w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Z Coordinate (m)
            </label>
            <input
              type="number"
              step="0.1"
              value={coords.z}
              onChange={(e) => setCoords(prev => ({ ...prev, z: parseFloat(e.target.value) || 0 }))}
              className="input w-full"
            />
          </div>
        </div>

        <button
          onClick={handleSave}
          className="btn btn-primary btn-sm w-full"
        >
          <Save className="w-4 h-4 mr-2" />
          Save Changes
        </button>
      </div>
    )
  }

  const ElementProperties = ({ element }: { element: any }) => {
    const [properties, setProperties] = useState({
      materialId: element.materialId,
      sectionId: element.sectionId || 1
    })

    const handleSave = () => {
      updateElement(element.id, properties)
    }

    return (
      <div className="space-y-4">
        <h4 className="font-medium">{element.type} Element {element.id}</h4>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Material
            </label>
            <select
              value={properties.materialId}
              onChange={(e) => setProperties(prev => ({ ...prev, materialId: parseInt(e.target.value) }))}
              className="input w-full"
            >
              {currentModel.materials.map(material => (
                <option key={material.id} value={material.id}>
                  {material.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Section
            </label>
            <select
              value={properties.sectionId}
              onChange={(e) => setProperties(prev => ({ ...prev, sectionId: parseInt(e.target.value) }))}
              className="input w-full"
            >
              {currentModel.sections.map(section => (
                <option key={section.id} value={section.id}>
                  {section.name}
                </option>
              ))}
            </select>
          </div>

          <div className="text-sm text-secondary-600">
            <p>Nodes: {element.nodes.join(' → ')}</p>
            <p>Type: {element.type}</p>
          </div>
        </div>

        <button
          onClick={handleSave}
          className="btn btn-primary btn-sm w-full"
        >
          <Save className="w-4 h-4 mr-2" />
          Save Changes
        </button>
      </div>
    )
  }

  const CreateNodeForm = () => {
    const [nodeData, setNodeData] = useState({
      x: 0,
      y: 0,
      z: 0
    })

    const handleCreate = () => {
      const newId = Math.max(0, ...currentModel.nodes.map(n => n.id)) + 1
      addNode({
        id: newId,
        x: nodeData.x,
        y: nodeData.y,
        z: nodeData.z,
        dofs: [true, true, true, true, true, true]
      })
      setNodeData({ x: 0, y: 0, z: 0 })
    }

    return (
      <div className="space-y-4">
        <h4 className="font-medium">Create Node</h4>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              X Coordinate (m)
            </label>
            <input
              type="number"
              step="0.1"
              value={nodeData.x}
              onChange={(e) => setNodeData(prev => ({ ...prev, x: parseFloat(e.target.value) || 0 }))}
              className="input w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Y Coordinate (m)
            </label>
            <input
              type="number"
              step="0.1"
              value={nodeData.y}
              onChange={(e) => setNodeData(prev => ({ ...prev, y: parseFloat(e.target.value) || 0 }))}
              className="input w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Z Coordinate (m)
            </label>
            <input
              type="number"
              step="0.1"
              value={nodeData.z}
              onChange={(e) => setNodeData(prev => ({ ...prev, z: parseFloat(e.target.value) || 0 }))}
              className="input w-full"
            />
          </div>
        </div>

        <button
          onClick={handleCreate}
          className="btn btn-primary btn-sm w-full"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Node
        </button>
      </div>
    )
  }

  const CreateElementForm = () => {
    const [elementData, setElementData] = useState({
      type: 'beam',
      node1: '',
      node2: '',
      materialId: currentModel.materials[0]?.id || 1,
      sectionId: currentModel.sections[0]?.id || 1
    })

    const handleCreate = () => {
      if (!elementData.node1 || !elementData.node2) return
      
      const newId = Math.max(0, ...currentModel.elements.map(e => e.id)) + 1
      addElement({
        id: newId,
        type: elementData.type,
        nodes: [parseInt(elementData.node1), parseInt(elementData.node2)],
        materialId: elementData.materialId,
        sectionId: elementData.sectionId
      })
      setElementData(prev => ({ ...prev, node1: '', node2: '' }))
    }

    return (
      <div className="space-y-4">
        <h4 className="font-medium">Create Element</h4>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Element Type
            </label>
            <select
              value={elementData.type}
              onChange={(e) => setElementData(prev => ({ ...prev, type: e.target.value }))}
              className="input w-full"
            >
              <option value="beam">Beam</option>
              <option value="truss">Truss</option>
              <option value="frame">Frame</option>
            </select>
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Start Node
              </label>
              <select
                value={elementData.node1}
                onChange={(e) => setElementData(prev => ({ ...prev, node1: e.target.value }))}
                className="input w-full"
              >
                <option value="">Select...</option>
                {currentModel.nodes.map(node => (
                  <option key={node.id} value={node.id}>
                    Node {node.id}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                End Node
              </label>
              <select
                value={elementData.node2}
                onChange={(e) => setElementData(prev => ({ ...prev, node2: e.target.value }))}
                className="input w-full"
              >
                <option value="">Select...</option>
                {currentModel.nodes.map(node => (
                  <option key={node.id} value={node.id}>
                    Node {node.id}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Material
            </label>
            <select
              value={elementData.materialId}
              onChange={(e) => setElementData(prev => ({ ...prev, materialId: parseInt(e.target.value) }))}
              className="input w-full"
            >
              {currentModel.materials.map(material => (
                <option key={material.id} value={material.id}>
                  {material.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Section
            </label>
            <select
              value={elementData.sectionId}
              onChange={(e) => setElementData(prev => ({ ...prev, sectionId: parseInt(e.target.value) }))}
              className="input w-full"
            >
              {currentModel.sections.map(section => (
                <option key={section.id} value={section.id}>
                  {section.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleCreate}
          disabled={!elementData.node1 || !elementData.node2}
          className="btn btn-primary btn-sm w-full disabled:opacity-50"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Element
        </button>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Tab Headers */}
      <div className="flex border-b border-secondary-200">
        <button
          onClick={() => setActiveTab('selection')}
          className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'selection'
              ? 'border-primary-500 text-primary-600 bg-primary-50'
              : 'border-transparent text-secondary-600 hover:text-secondary-900'
          }`}
        >
          Properties
        </button>
        <button
          onClick={() => setActiveTab('create')}
          className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'create'
              ? 'border-primary-500 text-primary-600 bg-primary-50'
              : 'border-transparent text-secondary-600 hover:text-secondary-900'
          }`}
        >
          Create
        </button>
      </div>

      {/* Tab Content */}
      <div className="flex-1 p-4 overflow-y-auto scrollbar-thin">
        {activeTab === 'selection' && (
          <div>
            {selectedNode ? (
              <NodeProperties node={selectedNode} />
            ) : selectedElement ? (
              <ElementProperties element={selectedElement} />
            ) : (
              <div className="text-center py-8 text-secondary-500">
                <div className="w-12 h-12 mx-auto mb-3 bg-secondary-100 rounded-lg flex items-center justify-center">
                  <X className="w-6 h-6" />
                </div>
                <p>No selection</p>
                <p className="text-sm">Select a node or element to edit properties</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'create' && (
          <div className="space-y-6">
            <CreateNodeForm />
            <div className="border-t border-secondary-200 pt-6">
              <CreateElementForm />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PropertiesPanel