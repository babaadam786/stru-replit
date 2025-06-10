import { motion } from 'framer-motion'
import {
  Plus,
  FolderOpen,
  BarChart3,
  Zap,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/appStore'
import { createDemoModel } from '../utils/demoData'

const Dashboard = () => {
  const navigate = useNavigate()
  const { analysisResults, currentModel, loadModel } = useAppStore()

  const loadDemoModel = () => {
    const demo = createDemoModel()
    loadModel(demo)
    navigate('/modeling')
  }

  const recentAnalyses = Object.values(analysisResults)
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 5)

  const stats = [
    {
      label: 'Active Projects',
      value: '3',
      change: '+2',
      icon: FolderOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      label: 'Analyses Completed',
      value: Object.keys(analysisResults).length.toString(),
      change: '+5',
      icon: BarChart3,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      label: 'Model Elements',
      value: currentModel.elements.length.toString(),
      change: '+12',
      icon: Zap,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      label: 'AI Queries',
      value: '24',
      change: '+8',
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ]

  const quickActions = [
    {
      title: 'New Project',
      description: 'Start a new structural engineering project',
      icon: Plus,
      action: () => navigate('/projects'),
      color: 'bg-primary-600 hover:bg-primary-700'
    },
    {
      title: 'Open Modeling',
      description: 'Create and edit structural models',
      icon: FolderOpen,
      action: () => navigate('/modeling'),
      color: 'bg-green-600 hover:bg-green-700'
    },
    {
      title: 'Run Analysis',
      description: 'Perform structural analysis',
      icon: BarChart3,
      action: () => navigate('/analysis'),
      color: 'bg-blue-600 hover:bg-blue-700'
    },
    {
      title: 'AI Assistant',
      description: 'Get AI-powered engineering help',
      icon: Zap,
      action: () => navigate('/ai-assistant'),
      color: 'bg-purple-600 hover:bg-purple-700'
    }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-gradient-to-r from-primary-600 to-accent-600 rounded-xl p-8 text-white"
      >
        <h1 className="text-3xl font-bold mb-2">Welcome to StructuralAI</h1>
        <p className="text-primary-100 text-lg">
          Advanced structural engineering with AI-powered analysis and design assistance
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {stats.map((stat, index) => (
          <div key={stat.label} className="card">
            <div className="card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-secondary-600">
                    {stat.label}
                  </p>
                  <p className="text-2xl font-bold text-secondary-900">
                    {stat.value}
                  </p>
                  <p className="text-sm text-green-600 font-medium">
                    {stat.change} this week
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          </div>
        ))}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="card"
        >
          <div className="card-header">
            <h2 className="text-lg font-semibold">Quick Actions</h2>
          </div>
          <div className="card-content space-y-3">
            {quickActions.map((action, index) => (
              <button
                key={action.title}
                onClick={action.action}
                className={`w-full p-4 rounded-lg text-white text-left transition-colors ${action.color}`}
              >
                <div className="flex items-center gap-3">
                  <action.icon className="w-6 h-6" />
                  <div>
                    <h3 className="font-medium">{action.title}</h3>
                    <p className="text-sm opacity-90">{action.description}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Recent Analyses */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="card"
        >
          <div className="card-header">
            <h2 className="text-lg font-semibold">Recent Analyses</h2>
          </div>
          <div className="card-content">
            {recentAnalyses.length > 0 ? (
              <div className="space-y-3">
                {recentAnalyses.map((analysis) => (
                  <div
                    key={analysis.id}
                    className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      {analysis.success ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                      )}
                      <div>
                        <p className="font-medium text-sm">
                          {analysis.type.charAt(0).toUpperCase() + analysis.type.slice(1)} Analysis
                        </p>
                        <p className="text-xs text-secondary-500">
                          {new Date(analysis.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`status-indicator ${
                        analysis.success ? 'status-success' : 'status-error'
                      }`}
                    >
                      {analysis.success ? 'Success' : 'Failed'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-secondary-500">
                <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No analyses yet</p>
                <p className="text-sm">Run your first analysis to see results here</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Current Model Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="card"
      >
        <div className="card-header">
          <h2 className="text-lg font-semibold">Current Model Overview</h2>
        </div>
        <div className="card-content">
          {currentModel.nodes.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-primary-600">
                  {currentModel.nodes.length}
                </p>
                <p className="text-sm text-secondary-600">Nodes</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {currentModel.elements.length}
                </p>
                <p className="text-sm text-secondary-600">Elements</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {currentModel.materials.length}
                </p>
                <p className="text-sm text-secondary-600">Materials</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">
                  {currentModel.loads.length}
                </p>
                <p className="text-sm text-secondary-600">Loads</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">
                  {currentModel.constraints.length}
                </p>
                <p className="text-sm text-secondary-600">Constraints</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-secondary-500">
              <FolderOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No model loaded</p>
              <p className="text-sm">Start modeling to see your structure here</p>
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => navigate('/modeling')}
                  className="btn btn-primary btn-sm"
                >
                  Start Modeling
                </button>
                <button
                  onClick={loadDemoModel}
                  className="btn btn-secondary btn-sm"
                >
                  Load Demo
                </button>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}

export default Dashboard