"""Base wrapper types for Blender objects with pose manipulation."""

from typing import Any, Dict, List, Optional, Union
import weakref

import bpy
import numpy as np
from mathutils import Matrix, Euler


class BlenderObject:
    """Base wrapper class for Blender objects.

    Provides name management and custom property handling for any bpy.types.Object.
    """

    # Track all instances using weak references for memory management
    _instances: weakref.WeakSet = weakref.WeakSet()

    def __init__(self, blender_object: bpy.types.Object):
        """Initialize the wrapper with a Blender object.

        Args:
            blender_object: The underlying Blender object to wrap.
        """
        self._bpy_obj = blender_object
        BlenderObject._instances.add(self)

    @property
    def bpy_object(self) -> bpy.types.Object:
        """Get the underlying Blender object."""
        return self._bpy_obj

    def is_valid(self) -> bool:
        """Check whether the contained Blender reference is valid.

        The reference might become invalid after an undo operation or deletion.

        Returns:
            True if the reference is still valid.
        """
        return str(self._bpy_obj) != "<bpy_struct, Object invalid>"

    def get_name(self) -> str:
        """Get the name of this object.

        Returns:
            The object's name.
        """
        return self._bpy_obj.name

    def set_name(self, name: str) -> None:
        """Set the name of this object.

        Args:
            name: The new name for the object.
        """
        self._bpy_obj.name = name

    def set_custom_property(self, key: str, value: Any) -> None:
        """Set a custom property on this object.

        Args:
            key: The property key.
            value: The property value.

        Raises:
            ValueError: If the key conflicts with a built-in attribute.
        """
        if hasattr(self._bpy_obj, key):
            raise ValueError(
                f"Key '{key}' conflicts with a built-in attribute. "
                "Choose a different name for your custom property."
            )
        self._bpy_obj[key] = value

    def get_custom_property(self, key: str) -> Any:
        """Get a custom property value.

        Args:
            key: The property key.

        Returns:
            The property value.

        Raises:
            KeyError: If the property doesn't exist.
        """
        return self._bpy_obj[key]

    def has_custom_property(self, key: str) -> bool:
        """Check if a custom property exists.

        Args:
            key: The property key to check.

        Returns:
            True if the property exists.
        """
        return key in self._bpy_obj

    def remove_custom_property(self, key: str) -> None:
        """Remove a custom property.

        Args:
            key: The property key to remove.
        """
        del self._bpy_obj[key]

    def get_all_custom_properties(self) -> Dict[str, Any]:
        """Get all custom properties as a dictionary.

        Returns:
            Dictionary of all custom properties.
        """
        return dict(self._bpy_obj.items())

    def clear_all_custom_properties(self) -> None:
        """Remove all custom properties from this object."""
        while len(self._bpy_obj.keys()) > 0:
            key = list(self._bpy_obj.keys())[0]
            del self._bpy_obj[key]

    def __eq__(self, other: object) -> bool:
        """Check equality based on the underlying Blender object."""
        if isinstance(other, BlenderObject):
            return self._bpy_obj == other._bpy_obj
        return False

    def __hash__(self) -> int:
        """Hash based on the underlying Blender object."""
        return hash(self._bpy_obj)


class SceneEntity(BlenderObject):
    """Wrapper for scene objects with 6D pose manipulation.

    Extends BlenderObject with methods for position, rotation, scale,
    and parent-child relationship management.
    """

    def __init__(self, blender_object: bpy.types.Object):
        """Initialize the scene entity.

        Args:
            blender_object: The underlying Blender object.
        """
        super().__init__(blender_object)

    def set_position(self, position: Union[List[float], np.ndarray]) -> None:
        """Set the world position of this entity.

        Args:
            position: The [x, y, z] position in world coordinates.
        """
        self._bpy_obj.location = position

    def get_position(self) -> np.ndarray:
        """Get the world position of this entity.

        Returns:
            The [x, y, z] position as a numpy array.
        """
        return np.array(self._bpy_obj.location)

    def set_rotation_euler(self, rotation: Union[List[float], np.ndarray]) -> None:
        """Set the rotation using Euler angles in XYZ order.

        Args:
            rotation: The [rx, ry, rz] rotation in radians.
        """
        self._bpy_obj.rotation_mode = 'XYZ'
        self._bpy_obj.rotation_euler = rotation

    def get_rotation_euler(self) -> np.ndarray:
        """Get the rotation as Euler angles.

        Returns:
            The [rx, ry, rz] rotation in radians as a numpy array.
        """
        return np.array(self._bpy_obj.rotation_euler)

    def set_rotation_matrix(self, rotation_matrix: Union[np.ndarray, List[List[float]]]) -> None:
        """Set the rotation using a 3x3 rotation matrix.

        Args:
            rotation_matrix: A 3x3 rotation matrix.
        """
        mat = Matrix(rotation_matrix)
        euler = mat.to_euler('XYZ')
        self.set_rotation_euler(euler)

    def get_rotation_matrix(self) -> np.ndarray:
        """Get the rotation as a 3x3 matrix.

        Returns:
            The 3x3 rotation matrix as a numpy array.
        """
        euler = Euler(self._bpy_obj.rotation_euler)
        return np.array(euler.to_matrix())

    def set_scale(self, scale: Union[List[float], np.ndarray]) -> None:
        """Set the scale of this entity.

        Args:
            scale: The [sx, sy, sz] scale factors.
        """
        self._bpy_obj.scale = scale

    def get_scale(self) -> np.ndarray:
        """Get the scale of this entity.

        Returns:
            The [sx, sy, sz] scale factors as a numpy array.
        """
        return np.array(self._bpy_obj.scale)

    def set_transform_matrix(self, matrix: Union[np.ndarray, List[List[float]]]) -> None:
        """Set the local-to-world transformation matrix.

        Args:
            matrix: A 4x4 transformation matrix.
        """
        self._bpy_obj.matrix_world = Matrix(matrix)

    def get_transform_matrix(self) -> np.ndarray:
        """Get the local-to-world transformation matrix.

        This method computes the full transform by traversing the parent hierarchy.

        Returns:
            The 4x4 transformation matrix as a numpy array.
        """
        obj = self._bpy_obj
        # Start with local transform (matrix_basis)
        world_matrix = obj.matrix_basis.copy()

        # Walk up the parent hierarchy
        while obj.parent is not None:
            # Apply parent inverse and parent's basis
            world_matrix = obj.parent.matrix_basis @ obj.matrix_parent_inverse @ world_matrix
            obj = obj.parent

        return np.array(world_matrix)

    def set_parent(self, parent: Optional["SceneEntity"]) -> None:
        """Set the parent of this entity.

        The world position will be preserved after parenting.

        Args:
            parent: The new parent entity, or None to clear the parent.
        """
        if parent is None:
            self.clear_parent()
            return

        # If already has a parent, clear it first
        if self._bpy_obj.parent is not None:
            self.clear_parent()

        # Set the new parent
        self._bpy_obj.parent = parent._bpy_obj
        # Preserve world position by setting the parent inverse
        self._bpy_obj.matrix_parent_inverse = Matrix(parent.get_transform_matrix()).inverted()

    def get_parent(self) -> Optional["SceneEntity"]:
        """Get the parent of this entity.

        Returns:
            The parent entity, or None if there is no parent.
        """
        if self._bpy_obj.parent is None:
            return None
        return SceneEntity(self._bpy_obj.parent)

    def clear_parent(self) -> None:
        """Remove the parent while preserving the world position."""
        if self._bpy_obj.parent is None:
            return

        # Store current world matrix
        world_matrix = self.get_transform_matrix()
        # Clear parent
        self._bpy_obj.parent = None
        # Restore world position
        self.set_transform_matrix(world_matrix)

    def get_children(self) -> List["SceneEntity"]:
        """Get all direct children of this entity.

        Returns:
            List of child entities.
        """
        return [SceneEntity(child) for child in self._bpy_obj.children]

    def select(self) -> None:
        """Select this entity in the viewport."""
        self._bpy_obj.select_set(True)

    def deselect(self) -> None:
        """Deselect this entity in the viewport."""
        self._bpy_obj.select_set(False)

    def is_empty(self) -> bool:
        """Check if this entity is an empty object (no geometry).

        Returns:
            True if this is an empty object.
        """
        return self._bpy_obj.type == "EMPTY"

    def hide(self, hide_render: bool = True) -> None:
        """Hide this entity from rendering.

        Args:
            hide_render: Whether to hide in renders.
        """
        self._bpy_obj.hide_render = hide_render

    def is_hidden(self) -> bool:
        """Check if this entity is hidden from rendering.

        Returns:
            True if hidden from rendering.
        """
        return self._bpy_obj.hide_render

    def delete(self) -> None:
        """Delete this entity from the scene."""
        bpy.data.objects.remove(self._bpy_obj, do_unlink=True)


def create_empty(name: str = "empty") -> SceneEntity:
    """Create an empty object in the scene.

    Args:
        name: The name for the empty object.

    Returns:
        The created SceneEntity.
    """
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD')
    empty = bpy.context.object
    empty.name = name
    return SceneEntity(empty)
