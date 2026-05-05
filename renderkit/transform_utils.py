"""Math utilities for 3D transformations and coordinate frame operations."""

from typing import List, Union
import numpy as np


def euler_to_rotation_matrix(euler_angles: Union[np.ndarray, List[float]]) -> np.ndarray:
    """Convert Euler angles (XYZ order) to a 3x3 rotation matrix.

    Args:
        euler_angles: Euler angles [rx, ry, rz] in radians (XYZ rotation order).

    Returns:
        3x3 rotation matrix.
    """
    euler = np.asarray(euler_angles, dtype=float)
    rx, ry, rz = euler[0], euler[1], euler[2]

    # Rotation around X axis
    cx, sx = np.cos(rx), np.sin(rx)
    Rx = np.array([
        [1, 0, 0],
        [0, cx, -sx],
        [0, sx, cx]
    ])

    # Rotation around Y axis
    cy, sy = np.cos(ry), np.sin(ry)
    Ry = np.array([
        [cy, 0, sy],
        [0, 1, 0],
        [-sy, 0, cy]
    ])

    # Rotation around Z axis
    cz, sz = np.cos(rz), np.sin(rz)
    Rz = np.array([
        [cz, -sz, 0],
        [sz, cz, 0],
        [0, 0, 1]
    ])

    # Combined rotation: Rz @ Ry @ Rx (intrinsic XYZ = extrinsic ZYX)
    return Rz @ Ry @ Rx


def create_transformation_matrix(
    translation: Union[np.ndarray, List[float]],
    rotation: Union[np.ndarray, List[float], List[List[float]]]
) -> np.ndarray:
    """Build a 4x4 homogeneous transformation matrix from translation and rotation.

    Args:
        translation: A 3D translation vector [x, y, z].
        rotation: Either a 3x3 rotation matrix or Euler angles [rx, ry, rz] in radians.

    Returns:
        4x4 transformation matrix.

    Raises:
        ValueError: If translation or rotation shapes are invalid.
    """
    trans = np.asarray(translation, dtype=float).flatten()
    rot = np.asarray(rotation, dtype=float)

    if trans.shape != (3,):
        raise ValueError(f"Translation must be a 3D vector, got shape {trans.shape}")

    # Build the 4x4 matrix
    matrix = np.eye(4)

    # Set translation in the last column
    matrix[:3, 3] = trans

    # Handle rotation
    if rot.shape == (3, 3):
        # Already a rotation matrix
        matrix[:3, :3] = rot
    elif rot.shape == (3,) or (rot.ndim == 1 and rot.size == 3):
        # Euler angles
        matrix[:3, :3] = euler_to_rotation_matrix(rot)
    else:
        raise ValueError(
            f"Rotation must be a 3x3 matrix or 3D Euler angles, got shape {rot.shape}"
        )

    return matrix


def _parse_axis(axis_str: str) -> tuple:
    """Parse an axis specifier like 'X', '-Y', 'Z' into (index, sign).

    Args:
        axis_str: Axis specifier string.

    Returns:
        Tuple of (axis_index, sign_multiplier).

    Raises:
        ValueError: If axis specifier is invalid.
    """
    axis = axis_str.strip().upper()

    if axis.startswith('-'):
        sign = -1
        axis = axis[1:]
    else:
        sign = 1

    axis_map = {'X': 0, 'Y': 1, 'Z': 2}
    if axis not in axis_map:
        raise ValueError(f"Invalid axis specifier: '{axis_str}'. Must be X, Y, Z, -X, -Y, or -Z.")

    return axis_map[axis], sign


def transform_point_coordinate_frame(
    point: Union[np.ndarray, List[float]],
    new_frame: List[str]
) -> np.ndarray:
    """Transform a 3D point to a new coordinate frame.

    The new frame is specified by a list of three axis mappings that describe
    how each axis of the new frame corresponds to the original frame.

    Example: [1, 2, 3] with frame ["X", "-Z", "Y"] becomes [1, -3, 2]

    Args:
        point: A 3D point [x, y, z].
        new_frame: List of 3 axis specifiers for the new frame, e.g., ["X", "-Z", "Y"].

    Returns:
        The point in the new coordinate frame.

    Raises:
        ValueError: If new_frame doesn't have exactly 3 elements or has invalid axes.
    """
    if len(new_frame) != 3:
        raise ValueError(f"new_frame must have exactly 3 elements, got {len(new_frame)}")

    pt = np.asarray(point, dtype=float).flatten()
    if pt.shape != (3,):
        raise ValueError(f"Point must be a 3D vector, got shape {pt.shape}")

    result = np.zeros(3)
    for i, axis_spec in enumerate(new_frame):
        idx, sign = _parse_axis(axis_spec)
        result[i] = sign * pt[idx]

    return result


def _build_frame_change_matrix(frame_spec: List[str]) -> np.ndarray:
    """Build a 4x4 transformation matrix for coordinate frame change.

    Args:
        frame_spec: List of 3 axis specifiers describing the new coordinate frame.

    Returns:
        4x4 transformation matrix that maps from original to new frame.
    """
    if len(frame_spec) != 3:
        raise ValueError(f"Frame specification must have exactly 3 elements, got {len(frame_spec)}")

    matrix = np.zeros((4, 4))
    matrix[3, 3] = 1.0

    for i, axis_spec in enumerate(frame_spec):
        idx, sign = _parse_axis(axis_spec)
        matrix[i, idx] = sign

    return matrix


def transform_matrix_target_frame(
    matrix: Union[np.ndarray, List[List[float]]],
    new_frame: List[str]
) -> np.ndarray:
    """Change the target coordinate frame of a transformation matrix.

    Given a matrix T_A^B that maps from frame A to frame B, this function changes
    the axes of B into B' to produce T_A^B'.

    Args:
        matrix: A 4x4 transformation matrix.
        new_frame: List of 3 axis specifiers for the new target frame.

    Returns:
        The transformed 4x4 matrix.
    """
    mat = np.asarray(matrix, dtype=float)
    if mat.shape != (4, 4):
        raise ValueError(f"Matrix must be 4x4, got shape {mat.shape}")

    frame_matrix = _build_frame_change_matrix(new_frame)
    return frame_matrix @ mat


def transform_matrix_source_frame(
    matrix: Union[np.ndarray, List[List[float]]],
    new_frame: List[str]
) -> np.ndarray:
    """Change the source coordinate frame of a transformation matrix.

    Given a matrix T_A^B that maps from frame A to frame B, this function changes
    the axes of A into A' to produce T_A'^B.

    Args:
        matrix: A 4x4 transformation matrix.
        new_frame: List of 3 axis specifiers for the new source frame.

    Returns:
        The transformed 4x4 matrix.
    """
    mat = np.asarray(matrix, dtype=float)
    if mat.shape != (4, 4):
        raise ValueError(f"Matrix must be 4x4, got shape {mat.shape}")

    frame_matrix = _build_frame_change_matrix(new_frame)
    frame_matrix_inv = np.linalg.inv(frame_matrix)
    return mat @ frame_matrix_inv
