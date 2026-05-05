# Todo

## Plan
Build the rendering pipeline from the bottom up: start with core math utilities and base types that don't require Blender, then add Blender-dependent types and utilities, followed by camera/lighting/object manipulation, and finally rendering and output writing. Each task delivers testable functionality.

## Tasks
- [x] Task 1: Math utilities for building 4x4 transformation matrices from translation and rotation, and coordinate frame conversion utilities (transform_utils.py + tests)
- [>] Task 2: Base wrapper types for Blender objects - Struct base class with name/custom properties, Entity class with 6D pose manipulation (set/get location, rotation, scale, parent/child hierarchy) (core_types.py + tests)
- [ ] Task 3: MeshObject class for mesh objects with material management, bounding box calculations, primitive creation (cube, sphere, plane, etc.), and mesh operations (mesh_types.py + tests)
- [ ] Task 4: Light class for creating and managing point/sun/spot/area lights with energy, color, radius settings (light_types.py + tests)
- [ ] Task 5: Material class for creating and configuring PBR materials with shader nodes and texture support (material_types.py + tests)
- [ ] Task 6: Scene initialization (init) and cleanup (clean_up) functions, global storage for session state, default configurations (scene_setup.py + tests)
- [ ] Task 7: Camera utilities - add camera poses, get poses, set intrinsics from K matrix or Blender params, compute rotation from forward vector, get field of view (camera_utils.py + tests)
- [ ] Task 8: OBJ file loader that imports 3D models and returns MeshObject instances with proper material assignment (obj_loader.py + tests)
- [ ] Task 9: Basic renderer configuration and render function that produces RGB images for all camera keyframes (renderer.py + tests)
- [ ] Task 10: HDF5 writer that saves rendered images and camera parameters to .hdf5 container files (hdf5_writer.py + tests)
- [ ] Task 11: Basic samplers - uniform sampling on spheres, shells, and disks for positioning objects and cameras (samplers.py + tests)
