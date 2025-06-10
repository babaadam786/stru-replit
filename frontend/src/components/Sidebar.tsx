import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Home,
  Box,
  BarChart3,
  FolderOpen,
  Database,
  Bot,
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap
} from 'lucide-react'
import { useAppStore } from '../store/appStore'

const Sidebar = () => {
  const { sidebarCollapsed, setSidebarCollapsed } = useAppStore()

  const navItems = [
    { to: '/', icon: Home, label: 'Dashboard' },
    { to: '/modeling', icon: Box, label: 'Modeling' },
    { to: '/analysis', icon: BarChart3, label: 'Analysis' },
    { to: '/projects', icon: FolderOpen, label: 'Projects' },
    { to: '/materials', icon: Database, label: 'Materials' },
    { to: '/ai-assistant', icon: Bot, label: 'AI Assistant' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <div className="h-full bg-white border-r border-secondary-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-4 border-b border-secondary-200">
        <motion.div
          className="flex items-center gap-3"
          animate={{ opacity: sidebarCollapsed ? 0 : 1 }}
          transition={{ duration: 0.2 }}
        >
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          {!sidebarCollapsed && (
            <span className="font-bold text-lg text-secondary-900">
              StructuralAI
            </span>
          )}
        </motion.div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-100 text-primary-700 border border-primary-200'
                  : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100'
              }`
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            <motion.span
              animate={{ opacity: sidebarCollapsed ? 0 : 1 }}
              transition={{ duration: 0.2 }}
              className={sidebarCollapsed ? 'sr-only' : ''}
            >
              {item.label}
            </motion.span>
          </NavLink>
        ))}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-3 border-t border-secondary-200">
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="w-full flex items-center justify-center p-2 rounded-lg text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 transition-colors"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>
    </div>
  )
}

export default Sidebar