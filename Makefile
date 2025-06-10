# StructuralAI Development Makefile

.PHONY: help install dev build test clean backend frontend

# Default target
help:
	@echo "StructuralAI Development Commands:"
	@echo ""
	@echo "  install     Install all dependencies"
	@echo "  dev         Start development servers"
	@echo "  backend     Start backend server only"
	@echo "  frontend    Start frontend server only"
	@echo "  build       Build for production"
	@echo "  test        Run tests"
	@echo "  clean       Clean build artifacts"
	@echo "  demo        Create demo data and start servers"
	@echo ""

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install --legacy-peer-deps
	@echo "Dependencies installed successfully!"

# Start development servers
dev:
	@echo "Starting StructuralAI development servers..."
	@echo "Backend will be available at: http://localhost:12000"
	@echo "Frontend will be available at: http://localhost:12001"
	@echo ""
	@echo "Press Ctrl+C to stop all servers"
	@make -j2 backend frontend

# Start backend only
backend:
	@echo "Starting backend server..."
	cd backend && python -m app.main

# Start frontend only  
frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

# Build for production
build:
	@echo "Building frontend for production..."
	cd frontend && npm run build
	@echo "Build completed!"

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest
	@echo "Running frontend tests..."
	cd frontend && npm run test
	@echo "All tests completed!"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean completed!"

# Create demo data and start servers
demo:
	@echo "Creating demo structural model..."
	cd backend && python -c "
import sys
sys.path.append('.')
from app.core.fem_engine import *

# Create demo model
engine = FEMEngine()

# Add materials
steel = Material(id=1, name='A992 Steel', E=200e9, nu=0.3, rho=7850, fy=345e6, fu=450e6)
engine.add_material(steel)

# Add sections  
section = Section(id=1, name='W12x26', A=7.65e-3, Ix=204e-6, Iy=17.3e-6, Iz=17.3e-6, J=0.457e-6)
engine.add_section(section)

# Add nodes for a simple frame
nodes = [
    Node(id=1, x=0, y=0, z=0),
    Node(id=2, x=5, y=0, z=0), 
    Node(id=3, x=10, y=0, z=0),
    Node(id=4, x=0, y=3, z=0),
    Node(id=5, x=5, y=3, z=0),
    Node(id=6, x=10, y=3, z=0)
]
for node in nodes:
    engine.add_node(node)

# Add elements
elements = [
    Element(id=1, type=ElementType.BEAM, nodes=[1, 2], material_id=1, section_id=1),
    Element(id=2, type=ElementType.BEAM, nodes=[2, 3], material_id=1, section_id=1),
    Element(id=3, type=ElementType.BEAM, nodes=[4, 5], material_id=1, section_id=1),
    Element(id=4, type=ElementType.BEAM, nodes=[5, 6], material_id=1, section_id=1),
    Element(id=5, type=ElementType.BEAM, nodes=[1, 4], material_id=1, section_id=1),
    Element(id=6, type=ElementType.BEAM, nodes=[2, 5], material_id=1, section_id=1),
    Element(id=7, type=ElementType.BEAM, nodes=[3, 6], material_id=1, section_id=1)
]
for element in elements:
    engine.add_element(element)

# Add constraints (fixed supports)
constraints = [
    Constraint(id=1, node_id=1, dofs=[True, True, True, True, True, True]),
    Constraint(id=2, node_id=3, dofs=[True, True, True, True, True, True])
]
for constraint in constraints:
    engine.add_constraint(constraint)

# Add loads
loads = [
    Load(id=1, node_id=5, values=[0, -10000, 0, 0, 0, 0])  # 10kN downward
]
for load in loads:
    engine.add_load(load)

print('Demo model created successfully!')
print(f'Nodes: {len(engine.nodes)}')
print(f'Elements: {len(engine.elements)}')
print(f'Materials: {len(engine.materials)}')
"
	@echo "Demo data created! Starting development servers..."
	@make dev

# Development shortcuts
install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install --legacy-peer-deps

# Docker commands (for future use)
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Linting and formatting
lint:
	@echo "Linting backend..."
	cd backend && python -m black . --check
	cd backend && python -m isort . --check-only
	@echo "Linting frontend..."
	cd frontend && npm run lint

format:
	@echo "Formatting backend..."
	cd backend && python -m black .
	cd backend && python -m isort .
	@echo "Formatting frontend..."
	cd frontend && npm run lint --fix