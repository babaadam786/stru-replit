import { motion } from 'framer-motion'
import { FolderOpen, Plus, Search } from 'lucide-react'

const ProjectManager = () => {
  return (
    <div className="p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-20"
      >
        <FolderOpen className="w-16 h-16 mx-auto mb-4 text-secondary-400" />
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">Project Manager</h2>
        <p className="text-secondary-600 mb-6">
          Manage your structural engineering projects and collaborate with team members
        </p>
        <div className="text-sm text-secondary-500">
          Coming soon: Project management and collaboration features
        </div>
      </motion.div>
    </div>
  )
}

export default ProjectManager