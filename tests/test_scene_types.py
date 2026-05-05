"""Tests for scene_types module."""

import numpy as np
import pytest
import bpy

from renderkit.scene_types import BlenderObject, SceneEntity, create_empty


def cleanup_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


@pytest.fixture(autouse=True)
def clean_scene():
    """Automatically clean up the scene before each test."""
    cleanup_scene()
    yield
    cleanup_scene()


class TestBlenderObject:
    """Tests for BlenderObject class."""

    def test_wrap_blender_object(self):
        """BlenderObject should wrap a Blender object."""
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object
        wrapper = BlenderObject(cube)
        assert wrapper.bpy_object == cube

    def test_get_name(self):
        """get_name should return the object's name."""
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object
        cube.name = "TestCube"
        wrapper = BlenderObject(cube)
        assert wrapper.get_name() == "TestCube"

    def test_set_name(self):
        """set_name should change the object's name."""
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object
        wrapper = BlenderObject(cube)
        wrapper.set_name("NewName")
        assert cube.name == "NewName"
        assert wrapper.get_name() == "NewName"

    def test_set_custom_property(self):
        """set_custom_property should add a custom property."""
        bpy.ops.mesh.primitive_cube_add()
        wrapper = BlenderObject(bpy.context.object)
        wrapper.set_custom_property("my_prop", 42)
        assert wrapper.has_custom_property("my_prop")
        assert wrapper.get_custom_property("my_prop") == 42

    def test_set_custom_property_string(self):
        """Custom properties can be strings."""
        bpy.ops.mesh.primitive_cube_add()
        wrapper = BlenderObject(bpy.context.object)
        wrapper.set_custom_property("label", "hello")
        assert wrapper.get_custom_property("label") == "hello"

    def test_set_custom_property_builtin_raises(self):
        """Setting a custom property with a built-in attribute name raises ValueError."""
        bpy.ops.mesh.primitive_cube_add()
        wrapper = BlenderObject(bpy.context.object)
        with pytest.raises(ValueError, match="conflicts with a built-in attribute"):
            wrapper.set_custom_property("location", [1, 2, 3])

    def test_has_custom_property_false(self):
        """has_custom_property should return False for non-existent keys."""
        bpy.ops.mesh.primitive_cube_add()
        wrapper = BlenderObject(bpy.context.object)
        assert not wrapper.has_custom_property("nonexistent")

    def test_remove_custom_property(self):
        """remove_custom_property should delete the property."""
        bpy.ops.mesh.primitive_cube_add()
        wrapper = BlenderObject(bpy.context.object)
        wrapper.set_custom_property("temp", 100)
        assert wrapper.has_custom_property("temp")
        wrapper.remove_custom_property("temp")
        assert not wrapper.has_custom_property("temp")

    def test_get_all_custom_properties(self):
        """get_all_custom_properties should return all properties."""
        bpy.ops.mesh.primitive_cube_add()
        wrapper = BlenderObject(bpy.context.object)
        wrapper.set_custom_property("a", 1)
        wrapper.set_custom_property("b", 2)
        props = wrapper.get_all_custom_properties()
        assert props["a"] == 1
        assert props["b"] == 2

    def test_clear_all_custom_properties(self):
        """clear_all_custom_properties should remove all properties."""
        bpy.ops.mesh.primitive_cube_add()
        wrapper = BlenderObject(bpy.context.object)
        wrapper.set_custom_property("x", 1)
        wrapper.set_custom_property("y", 2)
        wrapper.clear_all_custom_properties()
        assert len(wrapper.get_all_custom_properties()) == 0

    def test_equality(self):
        """Two wrappers for the same object should be equal."""
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object
        w1 = BlenderObject(cube)
        w2 = BlenderObject(cube)
        assert w1 == w2

    def test_inequality(self):
        """Two wrappers for different objects should not be equal."""
        bpy.ops.mesh.primitive_cube_add()
        cube1 = bpy.context.object
        bpy.ops.mesh.primitive_uv_sphere_add()
        cube2 = bpy.context.object
        w1 = BlenderObject(cube1)
        w2 = BlenderObject(cube2)
        assert w1 != w2


class TestSceneEntity:
    """Tests for SceneEntity class."""

    def test_set_get_position(self):
        """set_position and get_position should work correctly."""
        bpy.ops.mesh.primitive_cube_add()
        entity = SceneEntity(bpy.context.object)
        entity.set_position([1.0, 2.0, 3.0])
        pos = entity.get_position()
        np.testing.assert_array_almost_equal(pos, [1.0, 2.0, 3.0])

    def test_set_get_rotation_euler(self):
        """set_rotation_euler and get_rotation_euler should work correctly."""
        bpy.ops.mesh.primitive_cube_add()
        entity = SceneEntity(bpy.context.object)
        rotation = [np.pi / 4, np.pi / 2, np.pi]
        entity.set_rotation_euler(rotation)
        result = entity.get_rotation_euler()
        np.testing.assert_array_almost_equal(result, rotation)

    def test_set_get_scale(self):
        """set_scale and get_scale should work correctly."""
        bpy.ops.mesh.primitive_cube_add()
        entity = SceneEntity(bpy.context.object)
        entity.set_scale([2.0, 3.0, 4.0])
        scale = entity.get_scale()
        np.testing.assert_array_almost_equal(scale, [2.0, 3.0, 4.0])

    def test_set_get_transform_matrix(self):
        """set_transform_matrix and get_transform_matrix should work correctly."""
        bpy.ops.mesh.primitive_cube_add()
        entity = SceneEntity(bpy.context.object)

        # Create a simple transform: translate by [5, 0, 0]
        matrix = np.eye(4)
        matrix[:3, 3] = [5, 0, 0]

        entity.set_transform_matrix(matrix)
        result = entity.get_transform_matrix()
        np.testing.assert_array_almost_equal(result, matrix)

    def test_set_get_parent(self):
        """set_parent and get_parent should establish parent-child relationships."""
        bpy.ops.mesh.primitive_cube_add()
        parent = SceneEntity(bpy.context.object)
        parent.set_name("Parent")
        parent.set_position([0, 0, 0])

        bpy.ops.mesh.primitive_uv_sphere_add()
        child = SceneEntity(bpy.context.object)
        child.set_name("Child")
        child.set_position([1, 1, 1])

        child.set_parent(parent)

        retrieved_parent = child.get_parent()
        assert retrieved_parent is not None
        assert retrieved_parent.get_name() == "Parent"

    def test_get_children(self):
        """get_children should return all direct children."""
        bpy.ops.mesh.primitive_cube_add()
        parent = SceneEntity(bpy.context.object)
        parent.set_name("Parent")

        bpy.ops.mesh.primitive_uv_sphere_add()
        child1 = SceneEntity(bpy.context.object)
        child1.set_name("Child1")
        child1.set_parent(parent)

        bpy.ops.mesh.primitive_cone_add()
        child2 = SceneEntity(bpy.context.object)
        child2.set_name("Child2")
        child2.set_parent(parent)

        children = parent.get_children()
        assert len(children) == 2
        child_names = {c.get_name() for c in children}
        assert "Child1" in child_names
        assert "Child2" in child_names

    def test_clear_parent_preserves_position(self):
        """clear_parent should remove parent while preserving world position."""
        bpy.ops.mesh.primitive_cube_add()
        parent = SceneEntity(bpy.context.object)
        parent.set_position([10, 0, 0])

        bpy.ops.mesh.primitive_uv_sphere_add()
        child = SceneEntity(bpy.context.object)
        child.set_position([15, 5, 0])  # World position

        # Parent the child
        child.set_parent(parent)

        # Get world position before clearing
        pos_before = child.get_transform_matrix()[:3, 3]

        # Clear parent
        child.clear_parent()

        # World position should be preserved
        pos_after = child.get_transform_matrix()[:3, 3]
        np.testing.assert_array_almost_equal(pos_before, pos_after)
        assert child.get_parent() is None

    def test_no_parent_returns_none(self):
        """get_parent should return None for unparented objects."""
        bpy.ops.mesh.primitive_cube_add()
        entity = SceneEntity(bpy.context.object)
        assert entity.get_parent() is None

    def test_select_deselect(self):
        """select and deselect should work."""
        bpy.ops.mesh.primitive_cube_add()
        entity = SceneEntity(bpy.context.object)
        entity.deselect()
        assert not entity.bpy_object.select_get()
        entity.select()
        assert entity.bpy_object.select_get()

    def test_hide(self):
        """hide should control render visibility."""
        bpy.ops.mesh.primitive_cube_add()
        entity = SceneEntity(bpy.context.object)
        assert not entity.is_hidden()
        entity.hide(True)
        assert entity.is_hidden()
        entity.hide(False)
        assert not entity.is_hidden()


class TestCreateEmpty:
    """Tests for create_empty function."""

    def test_create_empty_default(self):
        """create_empty should create an empty object."""
        empty = create_empty()
        assert empty.is_empty()
        assert empty.get_name() == "empty"

    def test_create_empty_custom_name(self):
        """create_empty should accept a custom name."""
        empty = create_empty(name="MyEmpty")
        assert empty.is_empty()
        assert empty.get_name() == "MyEmpty"

    def test_create_empty_position(self):
        """Created empty should be at origin by default."""
        empty = create_empty()
        pos = empty.get_position()
        np.testing.assert_array_almost_equal(pos, [0, 0, 0])


class TestParentChildHierarchy:
    """Integration tests for parent-child relationships."""

    def test_move_parent_moves_child(self):
        """Moving a parent should move its children in world space."""
        parent = create_empty("parent")
        parent.set_position([0, 0, 0])

        child = create_empty("child")
        child.set_position([1, 0, 0])
        child.set_parent(parent)

        # Move parent
        parent.set_position([10, 0, 0])

        # Update Blender's dependency graph
        bpy.context.view_layer.update()

        # Child world position should have changed
        child_world = child.get_transform_matrix()[:3, 3]
        np.testing.assert_array_almost_equal(child_world, [11, 0, 0])

    def test_child_local_position_unchanged_after_reparent(self):
        """After reparenting, child's world position should be preserved initially."""
        parent = create_empty("parent")
        parent.set_position([5, 5, 5])

        child = create_empty("child")
        child.set_position([10, 10, 10])

        # Get world position before parenting
        world_pos_before = child.get_position().copy()

        # Parent
        child.set_parent(parent)

        # Update Blender's dependency graph
        bpy.context.view_layer.update()

        # World position should be preserved
        world_pos_after = child.get_transform_matrix()[:3, 3]
        np.testing.assert_array_almost_equal(world_pos_before, world_pos_after)
