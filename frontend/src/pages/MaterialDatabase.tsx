import { motion } from 'framer-motion'
import { Database, Plus, Search } from 'lucide-react'

const MaterialDatabase = () => {
  return (
    <div className="p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-20"
      >
        <Database className="w-16 h-16 mx-auto mb-4 text-secondary-400" />
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">Material Database</h2>
        <p className="text-secondary-600 mb-6">
          Browse and manage structural materials, sections, and properties
        </p>
        <div className="text-sm text-secondary-500">
          Coming soon: Comprehensive material and section database
        </div>
      </motion.div>
    </div>
  )
}

export default MaterialDatabase