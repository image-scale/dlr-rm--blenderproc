# Goal

## Project
blenderproc — a python project.

## Description
A procedural Blender pipeline for photorealistic rendering. The library provides a Python API to interact with Blender programmatically for creating synthetic training data for machine learning. It enables users to load 3D models (OBJ, PLY, blend files), set up cameras with precise intrinsics and poses, add lighting, configure materials, render RGB/depth/normal/segmentation images, and write the results to HDF5 containers. The core workflow involves initializing a scene, loading or creating objects, positioning cameras and lights, rendering, and saving outputs.

## Scope
- Core initialization and cleanup (init, clean_up)
- Base types (Struct, Entity, MeshObject, Light, Material)
- Math utilities (transformation matrices, coordinate frame conversions)
- Camera utilities (add poses, intrinsics, rotation calculations)
- Object creation (primitives, empty objects)
- Loader for OBJ files
- Renderer configuration and basic rendering
- HDF5 writer for saving rendered outputs
- Samplers (basic position/rotation sampling)
- Tests covering all implemented functionality

Note: This implementation will focus on the core functionality needed to run a basic rendering pipeline. Advanced loaders (BOP, ShapeNet, AMASS, etc.) and specialized features are outside the minimal viable scope.
