import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export interface Node {
  id: number
  x: number
  y: number
  z: number
  dofs: boolean[]
}

export interface Material {
  id: number
  name: string
  type: string
  E: number
  nu: number
  rho: number
  fy?: number
  fu?: number
}

export interface Section {
  id: number
  name: string
  A: number
  Ix: number
  Iy: number
  Iz: number
  J: number
}

export interface Element {
  id: number
  type: string
  nodes: number[]
  materialId: number
  sectionId?: number
}

export interface Load {
  id: number
  nodeId?: number
  elementId?: number
  type: string
  direction: string
  values: number[]
}

export interface Constraint {
  id: number
  nodeId: number
  dofs: boolean[]
  values: number[]
}

export interface StructuralModel {
  nodes: Node[]
  materials: Material[]
  sections: Section[]
  elements: Element[]
  loads: Load[]
  constraints: Constraint[]
}

export interface Project {
  id: string
  name: string
  description?: string
  projectType: string
  designCode: string
  location?: string
  client?: string
  engineer?: string
  tags: string[]
  createdAt: string
  updatedAt: string
  modelData?: StructuralModel
  analysisResults: string[]
}

export interface AnalysisResult {
  id: string
  type: string
  success: boolean
  timestamp: string
  results?: any
  error?: string
}

interface AppState {
  // UI State
  theme: 'light' | 'dark'
  sidebarCollapsed: boolean
  activeProject: Project | null
  
  // Model State
  currentModel: StructuralModel
  selectedNodes: number[]
  selectedElements: number[]
  
  // Analysis State
  analysisResults: Record<string, AnalysisResult>
  isAnalyzing: boolean
  
  // AI Assistant State
  aiChatHistory: Array<{
    id: string
    type: 'user' | 'assistant'
    content: string
    timestamp: string
  }>
  
  // Actions
  setTheme: (theme: 'light' | 'dark') => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setActiveProject: (project: Project | null) => void
  
  // Model Actions
  addNode: (node: Node) => void
  updateNode: (id: number, updates: Partial<Node>) => void
  removeNode: (id: number) => void
  
  addMaterial: (material: Material) => void
  updateMaterial: (id: number, updates: Partial<Material>) => void
  removeMaterial: (id: number) => void
  
  addSection: (section: Section) => void
  updateSection: (id: number, updates: Partial<Section>) => void
  removeSection: (id: number) => void
  
  addElement: (element: Element) => void
  updateElement: (id: number, updates: Partial<Element>) => void
  removeElement: (id: number) => void
  
  addLoad: (load: Load) => void
  updateLoad: (id: number, updates: Partial<Load>) => void
  removeLoad: (id: number) => void
  
  addConstraint: (constraint: Constraint) => void
  updateConstraint: (id: number, updates: Partial<Constraint>) => void
  removeConstraint: (id: number) => void
  
  // Selection Actions
  selectNodes: (nodeIds: number[]) => void
  selectElements: (elementIds: number[]) => void
  clearSelection: () => void
  
  // Analysis Actions
  setAnalysisResult: (id: string, result: AnalysisResult) => void
  setIsAnalyzing: (analyzing: boolean) => void
  
  // AI Actions
  addChatMessage: (message: { type: 'user' | 'assistant', content: string }) => void
  clearChatHistory: () => void
  
  // Model Management
  loadModel: (model: StructuralModel) => void
  clearModel: () => void
  exportModel: () => StructuralModel
}

const createEmptyModel = (): StructuralModel => ({
  nodes: [],
  materials: [],
  sections: [],
  elements: [],
  loads: [],
  constraints: []
})

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial State
        theme: 'light',
        sidebarCollapsed: false,
        activeProject: null,
        currentModel: createEmptyModel(),
        selectedNodes: [],
        selectedElements: [],
        analysisResults: {},
        isAnalyzing: false,
        aiChatHistory: [],
        
        // UI Actions
        setTheme: (theme) => set({ theme }),
        setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
        setActiveProject: (project) => set({ activeProject: project }),
        
        // Model Actions
        addNode: (node) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            nodes: [...state.currentModel.nodes, node]
          }
        })),
        
        updateNode: (id, updates) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            nodes: state.currentModel.nodes.map(node =>
              node.id === id ? { ...node, ...updates } : node
            )
          }
        })),
        
        removeNode: (id) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            nodes: state.currentModel.nodes.filter(node => node.id !== id),
            elements: state.currentModel.elements.filter(element =>
              !element.nodes.includes(id)
            ),
            loads: state.currentModel.loads.filter(load => load.nodeId !== id),
            constraints: state.currentModel.constraints.filter(constraint =>
              constraint.nodeId !== id
            )
          },
          selectedNodes: state.selectedNodes.filter(nodeId => nodeId !== id)
        })),
        
        addMaterial: (material) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            materials: [...state.currentModel.materials, material]
          }
        })),
        
        updateMaterial: (id, updates) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            materials: state.currentModel.materials.map(material =>
              material.id === id ? { ...material, ...updates } : material
            )
          }
        })),
        
        removeMaterial: (id) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            materials: state.currentModel.materials.filter(material => material.id !== id),
            elements: state.currentModel.elements.filter(element =>
              element.materialId !== id
            )
          }
        })),
        
        addSection: (section) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            sections: [...state.currentModel.sections, section]
          }
        })),
        
        updateSection: (id, updates) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            sections: state.currentModel.sections.map(section =>
              section.id === id ? { ...section, ...updates } : section
            )
          }
        })),
        
        removeSection: (id) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            sections: state.currentModel.sections.filter(section => section.id !== id),
            elements: state.currentModel.elements.filter(element =>
              element.sectionId !== id
            )
          }
        })),
        
        addElement: (element) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            elements: [...state.currentModel.elements, element]
          }
        })),
        
        updateElement: (id, updates) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            elements: state.currentModel.elements.map(element =>
              element.id === id ? { ...element, ...updates } : element
            )
          }
        })),
        
        removeElement: (id) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            elements: state.currentModel.elements.filter(element => element.id !== id),
            loads: state.currentModel.loads.filter(load => load.elementId !== id)
          },
          selectedElements: state.selectedElements.filter(elementId => elementId !== id)
        })),
        
        addLoad: (load) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            loads: [...state.currentModel.loads, load]
          }
        })),
        
        updateLoad: (id, updates) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            loads: state.currentModel.loads.map(load =>
              load.id === id ? { ...load, ...updates } : load
            )
          }
        })),
        
        removeLoad: (id) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            loads: state.currentModel.loads.filter(load => load.id !== id)
          }
        })),
        
        addConstraint: (constraint) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            constraints: [...state.currentModel.constraints, constraint]
          }
        })),
        
        updateConstraint: (id, updates) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            constraints: state.currentModel.constraints.map(constraint =>
              constraint.id === id ? { ...constraint, ...updates } : constraint
            )
          }
        })),
        
        removeConstraint: (id) => set((state) => ({
          currentModel: {
            ...state.currentModel,
            constraints: state.currentModel.constraints.filter(constraint => constraint.id !== id)
          }
        })),
        
        // Selection Actions
        selectNodes: (nodeIds) => set({ selectedNodes: nodeIds }),
        selectElements: (elementIds) => set({ selectedElements: elementIds }),
        clearSelection: () => set({ selectedNodes: [], selectedElements: [] }),
        
        // Analysis Actions
        setAnalysisResult: (id, result) => set((state) => ({
          analysisResults: { ...state.analysisResults, [id]: result }
        })),
        
        setIsAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),
        
        // AI Actions
        addChatMessage: (message) => set((state) => ({
          aiChatHistory: [
            ...state.aiChatHistory,
            {
              id: Date.now().toString(),
              ...message,
              timestamp: new Date().toISOString()
            }
          ]
        })),
        
        clearChatHistory: () => set({ aiChatHistory: [] }),
        
        // Model Management
        loadModel: (model) => set({ currentModel: model }),
        clearModel: () => set({ currentModel: createEmptyModel() }),
        exportModel: () => get().currentModel,
      }),
      {
        name: 'structurai-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
          currentModel: state.currentModel,
          aiChatHistory: state.aiChatHistory,
        }),
      }
    ),
    { name: 'StructuralAI Store' }
  )
)