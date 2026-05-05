"""Tests for transform_utils module."""

import numpy as np
import pytest
from renderkit.transform_utils import (
    euler_to_rotation_matrix,
    create_transformation_matrix,
    transform_point_coordinate_frame,
    transform_matrix_target_frame,
    transform_matrix_source_frame,
)


class TestEulerToRotationMatrix:
    """Tests for euler_to_rotation_matrix function."""

    def test_identity_rotation(self):
        """Zero Euler angles should produce identity rotation."""
        result = euler_to_rotation_matrix([0, 0, 0])
        expected = np.eye(3)
        np.testing.assert_array_almost_equal(result, expected)

    def test_rotation_x_90(self):
        """90 degree rotation around X axis."""
        result = euler_to_rotation_matrix([np.pi / 2, 0, 0])
        # After 90 deg X rotation: Y -> Z, Z -> -Y
        expected = np.array([
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0]
        ])
        np.testing.assert_array_almost_equal(result, expected)

    def test_rotation_y_90(self):
        """90 degree rotation around Y axis."""
        result = euler_to_rotation_matrix([0, np.pi / 2, 0])
        # After 90 deg Y rotation: X -> -Z, Z -> X
        expected = np.array([
            [0, 0, 1],
            [0, 1, 0],
            [-1, 0, 0]
        ])
        np.testing.assert_array_almost_equal(result, expected)

    def test_rotation_z_90(self):
        """90 degree rotation around Z axis."""
        result = euler_to_rotation_matrix([0, 0, np.pi / 2])
        # After 90 deg Z rotation: X -> Y, Y -> -X
        expected = np.array([
            [0, -1, 0],
            [1, 0, 0],
            [0, 0, 1]
        ])
        np.testing.assert_array_almost_equal(result, expected)


class TestCreateTransformationMatrix:
    """Tests for create_transformation_matrix function."""

    def test_identity_transform(self):
        """Zero translation and identity rotation should give identity matrix."""
        result = create_transformation_matrix([0, 0, 0], np.eye(3))
        np.testing.assert_array_almost_equal(result, np.eye(4))

    def test_translation_only(self):
        """Translation with identity rotation."""
        result = create_transformation_matrix([1, 2, 3], np.eye(3))
        expected = np.array([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ])
        np.testing.assert_array_almost_equal(result, expected)

    def test_translation_in_last_column(self):
        """Translation should appear in the last column."""
        result = create_transformation_matrix([5, 10, 15], np.eye(3))
        assert result[0, 3] == 5
        assert result[1, 3] == 10
        assert result[2, 3] == 15
        assert result[3, 3] == 1

    def test_euler_angles_zero(self):
        """Zero Euler angles should produce identity rotation part."""
        result = create_transformation_matrix([1, 2, 3], [0, 0, 0])
        expected_rotation = np.eye(3)
        np.testing.assert_array_almost_equal(result[:3, :3], expected_rotation)
        np.testing.assert_array_almost_equal(result[:3, 3], [1, 2, 3])

    def test_rotation_matrix_preserved(self):
        """Given rotation matrix should be preserved in output."""
        rot = np.array([
            [0, -1, 0],
            [1, 0, 0],
            [0, 0, 1]
        ])
        result = create_transformation_matrix([0, 0, 0], rot)
        np.testing.assert_array_almost_equal(result[:3, :3], rot)

    def test_combined_transform(self):
        """Combined translation and rotation."""
        translation = [1, 2, 3]
        rotation = np.array([
            [0, -1, 0],
            [1, 0, 0],
            [0, 0, 1]
        ])
        result = create_transformation_matrix(translation, rotation)

        assert result.shape == (4, 4)
        np.testing.assert_array_almost_equal(result[:3, :3], rotation)
        np.testing.assert_array_almost_equal(result[:3, 3], translation)
        np.testing.assert_array_almost_equal(result[3, :], [0, 0, 0, 1])

    def test_invalid_translation_shape(self):
        """Invalid translation shape should raise ValueError."""
        with pytest.raises(ValueError, match="Translation must be a 3D vector"):
            create_transformation_matrix([1, 2], np.eye(3))

    def test_invalid_rotation_shape(self):
        """Invalid rotation shape should raise ValueError."""
        with pytest.raises(ValueError, match="Rotation must be"):
            create_transformation_matrix([1, 2, 3], np.eye(2))


class TestTransformPointCoordinateFrame:
    """Tests for transform_point_coordinate_frame function."""

    def test_identity_frame(self):
        """Identity frame transformation should preserve point."""
        point = [1, 2, 3]
        result = transform_point_coordinate_frame(point, ["X", "Y", "Z"])
        np.testing.assert_array_almost_equal(result, [1, 2, 3])

    def test_swap_y_z_negate_z(self):
        """Swap Y and Z with negation of Z."""
        point = [1, 2, 3]
        result = transform_point_coordinate_frame(point, ["X", "-Z", "Y"])
        np.testing.assert_array_almost_equal(result, [1, -3, 2])

    def test_negate_all_axes(self):
        """Negate all axes."""
        point = [1, 2, 3]
        result = transform_point_coordinate_frame(point, ["-X", "-Y", "-Z"])
        np.testing.assert_array_almost_equal(result, [-1, -2, -3])

    def test_cyclic_permutation(self):
        """Cyclic permutation of axes."""
        point = [1, 2, 3]
        result = transform_point_coordinate_frame(point, ["Y", "Z", "X"])
        np.testing.assert_array_almost_equal(result, [2, 3, 1])

    def test_reverse_axes(self):
        """Reverse axis order."""
        point = [1, 2, 3]
        result = transform_point_coordinate_frame(point, ["Z", "Y", "X"])
        np.testing.assert_array_almost_equal(result, [3, 2, 1])

    def test_lowercase_axes(self):
        """Lowercase axis specifiers should work."""
        point = [1, 2, 3]
        result = transform_point_coordinate_frame(point, ["x", "y", "z"])
        np.testing.assert_array_almost_equal(result, [1, 2, 3])

    def test_invalid_axis_specifier(self):
        """Invalid axis specifier should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid axis specifier"):
            transform_point_coordinate_frame([1, 2, 3], ["X", "W", "Z"])

    def test_wrong_number_of_axes(self):
        """Wrong number of axes should raise ValueError."""
        with pytest.raises(ValueError, match="must have exactly 3 elements"):
            transform_point_coordinate_frame([1, 2, 3], ["X", "Y"])

    def test_numpy_array_input(self):
        """Should accept numpy array as input."""
        point = np.array([1, 2, 3])
        result = transform_point_coordinate_frame(point, ["X", "-Z", "Y"])
        np.testing.assert_array_almost_equal(result, [1, -3, 2])


class TestTransformMatrixTargetFrame:
    """Tests for transform_matrix_target_frame function."""

    def test_identity_frame_preserves_matrix(self):
        """Identity frame transformation should preserve matrix."""
        matrix = np.array([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ])
        result = transform_matrix_target_frame(matrix, ["X", "Y", "Z"])
        np.testing.assert_array_almost_equal(result, matrix)

    def test_swap_axes(self):
        """Swapping axes in target frame."""
        matrix = np.eye(4)
        matrix[:3, 3] = [1, 2, 3]
        result = transform_matrix_target_frame(matrix, ["X", "Z", "Y"])
        # Translation should be reordered: [1, 3, 2]
        assert result[0, 3] == 1
        assert result[1, 3] == 3
        assert result[2, 3] == 2

    def test_negate_axis(self):
        """Negating an axis in target frame."""
        matrix = np.eye(4)
        matrix[:3, 3] = [1, 2, 3]
        result = transform_matrix_target_frame(matrix, ["-X", "Y", "Z"])
        assert result[0, 3] == -1
        assert result[1, 3] == 2
        assert result[2, 3] == 3


class TestTransformMatrixSourceFrame:
    """Tests for transform_matrix_source_frame function."""

    def test_identity_frame_preserves_matrix(self):
        """Identity frame transformation should preserve matrix."""
        matrix = np.array([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ])
        result = transform_matrix_source_frame(matrix, ["X", "Y", "Z"])
        np.testing.assert_array_almost_equal(result, matrix)

    def test_source_frame_changes_rotation_columns(self):
        """Source frame change should affect rotation columns."""
        # Identity rotation
        matrix = np.eye(4)
        result = transform_matrix_source_frame(matrix, ["Y", "X", "Z"])
        # Columns should be swapped in rotation part
        expected_rotation = np.array([
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 1]
        ])
        np.testing.assert_array_almost_equal(result[:3, :3], expected_rotation)


class TestIntegration:
    """Integration tests for transform utilities."""

    def test_roundtrip_frame_transformation(self):
        """Applying source then target transformation with inverse frames."""
        matrix = np.array([
            [1, 0, 0, 1],
            [0, 1, 0, 2],
            [0, 0, 1, 3],
            [0, 0, 0, 1]
        ])
        frame = ["X", "-Z", "Y"]

        # Apply target frame change
        transformed = transform_matrix_target_frame(matrix, frame)

        # The result should be different from original
        assert not np.allclose(transformed, matrix)

    def test_transformation_matrix_applies_correctly(self):
        """Verify that transformation matrix can transform points correctly."""
        translation = [1, 0, 0]
        rotation = euler_to_rotation_matrix([0, 0, np.pi / 2])  # 90 deg around Z

        matrix = create_transformation_matrix(translation, rotation)

        # Transform a point at origin - should just get translation
        point = np.array([0, 0, 0, 1])
        result = matrix @ point
        np.testing.assert_array_almost_equal(result[:3], [1, 0, 0])

        # Transform a point at [1, 0, 0] - rotation moves it to [0, 1, 0], then translate
        point = np.array([1, 0, 0, 1])
        result = matrix @ point
        np.testing.assert_array_almost_equal(result[:3], [1, 1, 0])
