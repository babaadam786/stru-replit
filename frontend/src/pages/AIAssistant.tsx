import { motion } from 'framer-motion'
import { Bot, MessageCircle, Zap } from 'lucide-react'

const AIAssistant = () => {
  return (
    <div className="p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-20"
      >
        <Bot className="w-16 h-16 mx-auto mb-4 text-secondary-400" />
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">AI Assistant</h2>
        <p className="text-secondary-600 mb-6">
          Get intelligent design assistance, code checking, and optimization suggestions
        </p>
        <div className="text-sm text-secondary-500">
          Coming soon: AI-powered engineering assistance and chat interface
        </div>
      </motion.div>
    </div>
  )
}

export default AIAssistant