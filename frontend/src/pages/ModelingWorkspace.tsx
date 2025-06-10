import { useState } from 'react'
import { motion } from 'framer-motion'
import SplitPane from 'react-split-pane'
import ModelViewer from '../components/modeling/ModelViewer'
import ModelTree from '../components/modeling/ModelTree'
import PropertiesPanel from '../components/modeling/PropertiesPanel'
import ModelingToolbar from '../components/modeling/ModelingToolbar'
import { useAppStore } from '../store/appStore'

const ModelingWorkspace = () => {
  const [activeTab, setActiveTab] = useState<'model' | 'properties' | 'materials'>('model')
  const { currentModel } = useAppStore()

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <ModelingToolbar />

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <SplitPane
          split="vertical"
          minSize={250}
          maxSize={400}
          defaultSize={300}
          resizerStyle={{
            background: '#e2e8f0',
            width: '4px',
            cursor: 'col-resize',
          }}
        >
          {/* Left Panel */}
          <div className="h-full bg-white border-r border-secondary-200 flex flex-col">
            {/* Tab Headers */}
            <div className="flex border-b border-secondary-200">
              {[
                { key: 'model', label: 'Model' },
                { key: 'properties', label: 'Properties' },
                { key: 'materials', label: 'Materials' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.key
                      ? 'border-primary-500 text-primary-600 bg-primary-50'
                      : 'border-transparent text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-hidden">
              {activeTab === 'model' && <ModelTree />}
              {activeTab === 'properties' && <PropertiesPanel />}
              {activeTab === 'materials' && (
                <div className="p-4">
                  <h3 className="font-medium mb-3">Materials</h3>
                  <div className="space-y-2">
                    {currentModel.materials.map((material) => (
                      <div
                        key={material.id}
                        className="p-3 bg-secondary-50 rounded-lg"
                      >
                        <p className="font-medium text-sm">{material.name}</p>
                        <p className="text-xs text-secondary-600">
                          E = {(material.E / 1e9).toFixed(0)} GPa
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - 3D Viewer */}
          <SplitPane
            split="vertical"
            minSize={400}
            maxSize={-250}
            defaultSize={-300}
            resizerStyle={{
              background: '#e2e8f0',
              width: '4px',
              cursor: 'col-resize',
            }}
          >
            {/* 3D Viewport */}
            <div className="h-full bg-secondary-100 relative">
              <ModelViewer />
            </div>

            {/* Right Properties Panel */}
            <div className="h-full bg-white border-l border-secondary-200">
              <PropertiesPanel />
            </div>
          </SplitPane>
        </SplitPane>
      </div>
    </div>
  )
}

export default ModelingWorkspace