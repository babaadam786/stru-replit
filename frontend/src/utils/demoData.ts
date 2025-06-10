import { StructuralModel } from '../store/appStore'

export const createDemoModel = (): StructuralModel => {
  return {
    nodes: [
      { id: 1, x: 0, y: 0, z: 0, dofs: [true, true, true, true, true, true] },
      { id: 2, x: 5, y: 0, z: 0, dofs: [true, true, true, true, true, true] },
      { id: 3, x: 10, y: 0, z: 0, dofs: [true, true, true, true, true, true] },
      { id: 4, x: 0, y: 3, z: 0, dofs: [true, true, true, true, true, true] },
      { id: 5, x: 5, y: 3, z: 0, dofs: [true, true, true, true, true, true] },
      { id: 6, x: 10, y: 3, z: 0, dofs: [true, true, true, true, true, true] },
    ],
    materials: [
      {
        id: 1,
        name: 'A992 Steel',
        type: 'steel',
        E: 200e9,
        nu: 0.3,
        rho: 7850,
        fy: 345e6,
        fu: 450e6,
      },
    ],
    sections: [
      {
        id: 1,
        name: 'W12x26',
        A: 7.65e-3,
        Ix: 204e-6,
        Iy: 17.3e-6,
        Iz: 17.3e-6,
        J: 0.457e-6,
      },
    ],
    elements: [
      { id: 1, type: 'beam', nodes: [1, 2], materialId: 1, sectionId: 1 },
      { id: 2, type: 'beam', nodes: [2, 3], materialId: 1, sectionId: 1 },
      { id: 3, type: 'beam', nodes: [4, 5], materialId: 1, sectionId: 1 },
      { id: 4, type: 'beam', nodes: [5, 6], materialId: 1, sectionId: 1 },
      { id: 5, type: 'beam', nodes: [1, 4], materialId: 1, sectionId: 1 },
      { id: 6, type: 'beam', nodes: [2, 5], materialId: 1, sectionId: 1 },
      { id: 7, type: 'beam', nodes: [3, 6], materialId: 1, sectionId: 1 },
    ],
    loads: [
      {
        id: 1,
        nodeId: 5,
        type: 'force',
        direction: 'global',
        values: [0, -10000, 0, 0, 0, 0], // 10kN downward
      },
    ],
    constraints: [
      {
        id: 1,
        nodeId: 1,
        dofs: [true, true, true, true, true, true], // Fixed support
        values: [0, 0, 0, 0, 0, 0],
      },
      {
        id: 2,
        nodeId: 3,
        dofs: [true, true, true, true, true, true], // Fixed support
        values: [0, 0, 0, 0, 0, 0],
      },
    ],
  }
}