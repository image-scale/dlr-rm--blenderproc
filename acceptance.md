# Acceptance Criteria

(Updated before each feature implementation. Define what "done" means for each task.)

## Task 1: Math utilities for transformation matrices and coordinate frame conversions

### Acceptance Criteria
- [ ] `create_transformation_matrix(translation, rotation)` builds a 4x4 homogeneous transformation matrix from a 3D translation vector and either a 3x3 rotation matrix or 3D Euler angles
- [ ] Given translation=[1,2,3] and a 3x3 identity rotation, the result should have translation in the last column and identity in the 3x3 submatrix
- [ ] Given Euler angles [0,0,0], the rotation part should be identity
- [ ] `transform_point_coordinate_frame(point, new_frame)` converts a point to a new coordinate frame specified by axis mapping like ["X", "-Z", "Y"]
- [ ] Point [1,2,3] with frame ["X", "-Z", "Y"] yields [1,-3,2]
- [ ] Point [1,2,3] with frame ["-X", "-Y", "-Z"] yields [-1,-2,-3]
- [ ] Invalid axis specifier raises ValueError
- [ ] `transform_matrix_target_frame(matrix, new_frame)` changes the target coordinate frame of a transformation matrix
- [ ] `transform_matrix_source_frame(matrix, new_frame)` changes the source coordinate frame of a transformation matrix
- [ ] Frame transformation with ["X","Y","Z"] (identity frame) returns the original matrix unchanged
