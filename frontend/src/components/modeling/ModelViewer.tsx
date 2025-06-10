import { Suspense, useRef, useState, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Grid, Text, Line } from '@react-three/drei'
import * as THREE from 'three'
import { motion } from 'framer-motion'
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Move3D, 
  MousePointer,
  Plus,
  Eye,
  EyeOff
} from 'lucide-react'
import { useAppStore } from '../../store/appStore'

// Node component
const NodeComponent = ({ node, isSelected, onClick }: any) => {
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.01
      meshRef.current.rotation.y += 0.01
    }
  })

  return (
    <mesh
      ref={meshRef}
      position={[node.x, node.y, node.z]}
      onClick={(e) => {
        e.stopPropagation()
        onClick(node.id)
      }}
    >
      <sphereGeometry args={[0.1, 8, 8]} />
      <meshStandardMaterial 
        color={isSelected ? '#3b82f6' : '#64748b'} 
        emissive={isSelected ? '#1e40af' : '#000000'}
        emissiveIntensity={isSelected ? 0.3 : 0}
      />
      <Text
        position={[0, 0.3, 0]}
        fontSize={0.1}
        color="#374151"
        anchorX="center"
        anchorY="middle"
      >
        {node.id}
      </Text>
    </mesh>
  )
}

// Element component
const ElementComponent = ({ element, nodes, isSelected, onClick }: any) => {
  const startNode = nodes.find((n: any) => n.id === element.nodes[0])
  const endNode = nodes.find((n: any) => n.id === element.nodes[1])
  
  if (!startNode || !endNode) return null

  const points = [
    new THREE.Vector3(startNode.x, startNode.y, startNode.z),
    new THREE.Vector3(endNode.x, endNode.y, endNode.z)
  ]

  return (
    <Line
      points={points}
      color={isSelected ? '#3b82f6' : '#374151'}
      lineWidth={isSelected ? 3 : 2}
      onClick={(e) => {
        e.stopPropagation()
        onClick(element.id)
      }}
    />
  )
}

// Load visualization component
const LoadComponent = ({ load, nodes }: any) => {
  const node = nodes.find((n: any) => n.id === load.nodeId)
  if (!node) return null

  const maxForce = Math.max(...load.values.slice(0, 3).map(Math.abs))
  const scale = maxForce > 0 ? Math.min(maxForce / 1000, 2) : 0.5

  return (
    <group position={[node.x, node.y, node.z]}>
      {/* Force arrows */}
      {load.values.slice(0, 3).map((force: number, index: number) => {
        if (Math.abs(force) < 0.001) return null
        
        const direction = [0, 0, 0]
        direction[index] = force > 0 ? 1 : -1
        
        return (
          <group key={index} position={direction.map(d => d * 0.3) as [number, number, number]}>
            <mesh>
              <coneGeometry args={[0.05, 0.2, 8]} />
              <meshStandardMaterial color="#ef4444" />
            </mesh>
            <Text
              position={[0, 0.3, 0]}
              fontSize={0.08}
              color="#ef4444"
              anchorX="center"
              anchorY="middle"
            >
              {Math.abs(force).toFixed(0)}N
            </Text>
          </group>
        )
      })}
    </group>
  )
}

// Constraint visualization component
const ConstraintComponent = ({ constraint, nodes }: any) => {
  const node = nodes.find((n: any) => n.id === constraint.nodeId)
  if (!node) return null

  const constrainedDofs = constraint.dofs.slice(0, 3).some((dof: boolean) => dof)
  if (!constrainedDofs) return null

  return (
    <group position={[node.x, node.y, node.z]}>
      <mesh position={[0, -0.2, 0]}>
        <boxGeometry args={[0.3, 0.1, 0.3]} />
        <meshStandardMaterial color="#059669" />
      </mesh>
      {/* Support symbols */}
      {constraint.dofs.slice(0, 3).map((constrained: boolean, index: number) => {
        if (!constrained) return null
        
        const position = [0, 0, 0]
        position[index] = 0.2
        
        return (
          <mesh key={index} position={position as [number, number, number]}>
            <boxGeometry args={[0.05, 0.05, 0.05]} />
            <meshStandardMaterial color="#059669" />
          </mesh>
        )
      })}
    </group>
  )
}

// Scene component
const Scene = () => {
  const { 
    currentModel, 
    selectedNodes, 
    selectedElements, 
    selectNodes, 
    selectElements 
  } = useAppStore()

  const handleNodeClick = (nodeId: number) => {
    selectNodes([nodeId])
    selectElements([])
  }

  const handleElementClick = (elementId: number) => {
    selectElements([elementId])
    selectNodes([])
  }

  const handleBackgroundClick = () => {
    selectNodes([])
    selectElements([])
  }

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} />
      <pointLight position={[-10, -10, -5]} intensity={0.4} />

      {/* Grid */}
      <Grid
        args={[20, 20]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#cbd5e1"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#94a3b8"
        fadeDistance={30}
        fadeStrength={1}
        followCamera={false}
        infiniteGrid={true}
      />

      {/* Background click handler */}
      <mesh onClick={handleBackgroundClick} visible={false}>
        <planeGeometry args={[1000, 1000]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>

      {/* Nodes */}
      {currentModel.nodes.map((node) => (
        <NodeComponent
          key={node.id}
          node={node}
          isSelected={selectedNodes.includes(node.id)}
          onClick={handleNodeClick}
        />
      ))}

      {/* Elements */}
      {currentModel.elements.map((element) => (
        <ElementComponent
          key={element.id}
          element={element}
          nodes={currentModel.nodes}
          isSelected={selectedElements.includes(element.id)}
          onClick={handleElementClick}
        />
      ))}

      {/* Loads */}
      {currentModel.loads.map((load) => (
        <LoadComponent
          key={load.id}
          load={load}
          nodes={currentModel.nodes}
        />
      ))}

      {/* Constraints */}
      {currentModel.constraints.map((constraint) => (
        <ConstraintComponent
          key={constraint.id}
          constraint={constraint}
          nodes={currentModel.nodes}
        />
      ))}

      {/* Controls */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        dampingFactor={0.05}
        enableDamping={true}
      />
    </>
  )
}

// Camera controls component
const CameraControls = () => {
  const { camera, gl } = useThree()
  
  const resetView = () => {
    camera.position.set(10, 10, 10)
    camera.lookAt(0, 0, 0)
  }

  const fitToView = () => {
    // TODO: Implement fit to view based on model bounds
    camera.position.set(5, 5, 5)
    camera.lookAt(0, 0, 0)
  }

  return null
}

const ModelViewer = () => {
  const [viewMode, setViewMode] = useState<'3d' | 'wireframe' | 'shaded'>('shaded')
  const [showGrid, setShowGrid] = useState(true)
  const [showLoads, setShowLoads] = useState(true)
  const [showConstraints, setShowConstraints] = useState(true)

  return (
    <div className="h-full relative">
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [10, 10, 10], fov: 50 }}
        style={{ background: '#f8fafc' }}
      >
        <Suspense fallback={null}>
          <Scene />
          <CameraControls />
        </Suspense>
      </Canvas>

      {/* Viewport Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <div className="bg-white rounded-lg shadow-lg border border-secondary-200 p-2">
          <div className="flex flex-col gap-1">
            <button
              className="btn btn-ghost btn-sm"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              className="btn btn-ghost btn-sm"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              className="btn btn-ghost btn-sm"
              title="Reset View"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              className="btn btn-ghost btn-sm"
              title="Fit to View"
            >
              <Move3D className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* View Options */}
        <div className="bg-white rounded-lg shadow-lg border border-secondary-200 p-2">
          <div className="flex flex-col gap-1">
            <button
              onClick={() => setShowGrid(!showGrid)}
              className={`btn btn-sm ${showGrid ? 'btn-primary' : 'btn-ghost'}`}
              title="Toggle Grid"
            >
              {showGrid ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>
            <button
              onClick={() => setShowLoads(!showLoads)}
              className={`btn btn-sm ${showLoads ? 'btn-primary' : 'btn-ghost'}`}
              title="Toggle Loads"
            >
              L
            </button>
            <button
              onClick={() => setShowConstraints(!showConstraints)}
              className={`btn btn-sm ${showConstraints ? 'btn-primary' : 'btn-ghost'}`}
              title="Toggle Constraints"
            >
              C
            </button>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg border border-secondary-200 px-3 py-2">
        <div className="flex items-center gap-4 text-sm text-secondary-600">
          <span>View: {viewMode}</span>
          <span>Nodes: {useAppStore.getState().currentModel.nodes.length}</span>
          <span>Elements: {useAppStore.getState().currentModel.elements.length}</span>
        </div>
      </div>

      {/* Quick Add Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="absolute bottom-4 right-4 w-12 h-12 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-lg flex items-center justify-center"
        title="Quick Add"
      >
        <Plus className="w-6 h-6" />
      </motion.button>
    </div>
  )
}

export default ModelViewer