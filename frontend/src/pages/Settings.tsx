import { motion } from 'framer-motion'
import { Settings as SettingsIcon, User, Palette } from 'lucide-react'

const Settings = () => {
  return (
    <div className="p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-20"
      >
        <SettingsIcon className="w-16 h-16 mx-auto mb-4 text-secondary-400" />
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">Settings</h2>
        <p className="text-secondary-600 mb-6">
          Configure application preferences, units, and user settings
        </p>
        <div className="text-sm text-secondary-500">
          Coming soon: Comprehensive settings and preferences
        </div>
      </motion.div>
    </div>
  )
}

export default Settings