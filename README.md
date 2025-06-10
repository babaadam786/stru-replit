# StructuralAI - Advanced Structural Engineering SaaS Platform

A comprehensive web-based platform for structural engineers featuring:

## 🚀 Features

- **Advanced FEM Analysis**: Custom finite element method engine for structural analysis
- **AI-Powered Design**: Local LLM integration for intelligent design assistance
- **3D BIM Modeling**: Interactive 3D modeling and visualization
- **Advanced Detailing**: Automated structural detailing and documentation
- **Real-time Collaboration**: Multi-user project collaboration
- **Code Compliance**: Automated code checking and compliance verification

## 🏗️ Architecture

### Backend (`/backend`)
- **FastAPI**: Modern Python web framework
- **Custom FEM Engine**: Built with NumPy/SciPy for structural analysis
- **PostgreSQL**: Database for project data
- **Local LLM**: AI integration for engineering assistance
- **WebSocket**: Real-time collaboration

### Frontend (`/frontend`)
- **React 18 + TypeScript**: Modern web framework
- **Tailwind CSS**: Utility-first styling
- **Three.js**: 3D visualization and BIM modeling
- **Zustand**: State management
- **React Query**: Data fetching and caching

## 🛠️ Tech Stack

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy + PostgreSQL
- NumPy, SciPy, Matplotlib
- Transformers (Local LLM)
- WebSockets
- Docker

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Three.js + React Three Fiber
- Zustand
- React Query
- Vite

## 🚀 Quick Start

```bash
# Install dependencies
make install

# Start development servers
make dev

# Run tests
make test

# Build for production
make build
```

## 📁 Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── core/           # Core FEM engine
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── ai/             # LLM integration
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── store/          # State management
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities
│   ├── public/
│   └── package.json
├── docker-compose.yml      # Development environment
└── Makefile               # Development commands
```

## 🔧 Development

This project is designed for structural engineers who need advanced computational tools with AI assistance. The platform provides a complete workflow from conceptual design to detailed analysis and documentation.

## 📄 License

MIT License - see LICENSE file for details.