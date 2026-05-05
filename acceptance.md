# Acceptance Criteria

(Updated before each feature implementation. Define what "done" means for each task.)

## Task 1: Math utilities for transformation matrices and coordinate frame conversions

### Acceptance Criteria
- [x] `create_transformation_matrix(translation, rotation)` builds a 4x4 homogeneous transformation matrix from a 3D translation vector and either a 3x3 rotation matrix or 3D Euler angles
- [x] Given translation=[1,2,3] and a 3x3 identity rotation, the result should have translation in the last column and identity in the 3x3 submatrix
- [x] Given Euler angles [0,0,0], the rotation part should be identity
- [x] `transform_point_coordinate_frame(point, new_frame)` converts a point to a new coordinate frame specified by axis mapping like ["X", "-Z", "Y"]
- [x] Point [1,2,3] with frame ["X", "-Z", "Y"] yields [1,-3,2]
- [x] Point [1,2,3] with frame ["-X", "-Y", "-Z"] yields [-1,-2,-3]
- [x] Invalid axis specifier raises ValueError
- [x] `transform_matrix_target_frame(matrix, new_frame)` changes the target coordinate frame of a transformation matrix
- [x] `transform_matrix_source_frame(matrix, new_frame)` changes the source coordinate frame of a transformation matrix
- [x] Frame transformation with ["X","Y","Z"] (identity frame) returns the original matrix unchanged

## Task 2: Base wrapper types (Struct, Entity) with pose manipulation

### Acceptance Criteria
- [ ] BlenderObject (Struct equivalent) wraps a bpy.types.Object and provides name get/set methods
- [ ] Custom property methods: set_custom_property(key, value), get_custom_property(key), has_custom_property(key), remove_custom_property(key), get_all_custom_properties()
- [ ] Setting a custom property with a key that is a built-in attribute raises ValueError
- [ ] SceneEntity (Entity equivalent) extends BlenderObject with 6D pose manipulation
- [ ] set_position([x,y,z]) and get_position() work correctly
- [ ] set_rotation_euler([rx,ry,rz]) and get_rotation_euler() work correctly
- [ ] set_scale([sx,sy,sz]) and get_scale() work correctly
- [ ] set_transform_matrix(4x4) and get_transform_matrix() work correctly
- [ ] set_parent(entity) and get_parent() establish parent-child relationships
- [ ] get_children() returns all direct child entities
- [ ] clear_parent() removes the parent while preserving world position
