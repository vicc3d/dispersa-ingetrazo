"""Scattering inside a real IngeTrazo scene (offscreen). Needs an IngeTrazo
checkout and its Python environment:

    INGETRAZO_SRC=~/src/ingetrazo QT_QPA_PLATFORM=offscreen \\
        <ingetrazo venv>/bin/python -m pytest tests
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import pytest

_SRC = os.environ.get("INGETRAZO_SRC")
if not _SRC or not (Path(_SRC) / "core" / "group.py").is_file():
    pytest.skip("set INGETRAZO_SRC to an IngeTrazo checkout", allow_module_level=True)
sys.path.insert(0, _SRC)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtGui import QVector3D  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from dispersa import motor  # noqa: E402

_app = QApplication.instance() or QApplication([])

TREE = {"kind": "bundled", "key": "arbol", "name": "Tree"}
BIRCH = {"kind": "bundled", "key": "abedul", "name": "Birch"}


def _square(scene, size=20.0, z=0.0, down=False):
    pts = [(0, 0), (size, 0), (size, size), (0, size)]
    if down:
        pts.reverse()
    return scene.mesh.add_face([QVector3D(x, y, z) for x, y in pts])


@pytest.fixture
def scene():
    from core.scene import Scene
    return Scene()


def _params(**kw):
    return {**motor.DEFAULTS, "sources": [TREE], **kw}


def test_surface_from_a_face_and_its_area(scene):
    f = _square(scene)
    tris = motor.surface_from_selection([f])
    assert len(tris) == 2
    assert motor.surface_area(tris) == pytest.approx(400.0)


def test_a_face_drawn_upside_down_is_turned_up(scene):
    f = _square(scene, down=True)
    assert f.normal().z() < 0
    tris = motor.surface_from_selection([f])
    assert all(motor._normal(t)[2] > 0.99 for t in tris)


def test_from_a_group_only_what_faces_up(scene):
    from core.group import Group
    from core.mesh import Mesh
    m = Mesh()
    m.add_face([QVector3D(*p) for p in [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)]])
    m.add_face([QVector3D(*p) for p in [(0, 0, 0), (0, 0, 3), (10, 0, 3), (10, 0, 0)]])
    g = Group(m)
    tris = motor.surface_from_selection([g], max_slope=40)
    assert motor.surface_area(tris) == pytest.approx(100.0)
    assert motor.surface_area(motor.surface_from_selection([g], max_slope=90)) \
        == pytest.approx(130.0)


def test_selection_face_count_does_not_triangulate(scene, monkeypatch):
    from core.group import Group
    from core.mesh import Mesh
    m = Mesh()
    m.add_face([QVector3D(*p) for p in [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)]])
    m.add_face([QVector3D(*p) for p in [(0, 0, 0), (0, 0, 3), (10, 0, 3), (10, 0, 0)]])
    g = Group(m)
    f = _square(scene)
    monkeypatch.setattr(motor, "surface_from_selection",
                        lambda *a, **k: pytest.fail("must only count"))
    assert motor.selection_face_count([g, f]) == 3
    assert motor.selection_face_count([]) == 0


def test_points_stay_on_the_surface_and_apart(scene):
    tris = motor.surface_from_selection([_square(scene, 30.0)])
    pts, wanted = motor.scatter_points(tris, _params(count=80, min_distance=2.0, seed=4))
    assert wanted == 80 and len(pts) == 80
    for (x, y, z), _n in pts:
        assert 0 <= x <= 30 and 0 <= y <= 30 and z == pytest.approx(0)
    for i, (a, _) in enumerate(pts):
        for b, _ in pts[i + 1:]:
            assert math.dist(a, b) >= 2.0 - 1e-9


def test_the_same_seed_gives_the_same_points(scene):
    tris = motor.surface_from_selection([_square(scene)])
    a, _ = motor.scatter_points(tris, _params(seed=7))
    b, _ = motor.scatter_points(tris, _params(seed=7))
    c, _ = motor.scatter_points(tris, _params(seed=8))
    assert a == b and a != c


def test_no_room_places_fewer(scene):
    tris = motor.surface_from_selection([_square(scene, 10.0)])
    pts, wanted = motor.scatter_points(tris, _params(count=500, min_distance=3.0))
    assert wanted == 500 and 0 < len(pts) < 30


def test_density_counts_by_area(scene):
    tris = motor.surface_from_selection([_square(scene, 20.0)])
    _pts, wanted = motor.scatter_points(tris, _params(mode="density", density=5,
                                                      min_distance=0))
    assert wanted == 20


class FlatHill:
    """A ground that rises 1 m every 10 m eastwards, captured from x = 0
    to x = 15 only."""
    def height_at(self, x, y):
        return None if x > 15 else 5.0 + x / 10.0


def test_on_the_terrain_points_take_its_height(scene):
    tris = motor.surface_from_selection([_square(scene, 20.0)])
    pts, _ = motor.scatter_points(tris, _params(count=40, min_distance=0),
                                  terrain=FlatHill())
    assert pts
    for (x, _y, z), n in pts:
        assert x <= 15 and z == pytest.approx(5.0 + x / 10.0)
        if x < 14.5:                    # the slope is read half a metre on
            assert n[0] < 0 and n[2] > 0.99


def test_scatter_shares_the_geometry_and_stands_on_the_base(scene):
    f = _square(scene, 40.0)
    tris = motor.surface_from_selection([f])
    box, placed, wanted = motor.scatter(scene, _params(
        sources=[TREE, {**BIRCH, "weight": 3}], count=60, min_distance=1.5),
        tris=tris)
    assert box in scene.groups and not box.is_component()
    assert placed == wanted == 60 == len(box.children)
    assert box.layer == motor.LAYER and any(ly.name == motor.LAYER for ly in scene.layers)
    meshes = {id(k.mesh) for k in box.children}
    assert len(meshes) == 2                     # two objects, sixty copies
    assert all(k.is_component() for k in box.children)
    # Birch weighs three times the tree.
    birches = sum(1 for k in box.children if k.ext[motor.KEY]["src"] == 1)
    assert birches > 30
    # Every copy stands on the face: its lowest point at z = 0, inside it.
    from core.group import world_mesh
    for k in box.children[:5]:
        zs = [p.z() for fc in world_mesh(k).faces for p in fc.vertices]
        assert min(zs) == pytest.approx(0.0, abs=1e-4)
    e = box.ext[motor.KEY]
    assert e["surface"] == tris and e["placed"] == 60 and e["seed"] == motor.DEFAULTS["seed"]


def test_scatter_again_replaces_and_keeps_the_objects(scene):
    tris = motor.surface_from_selection([_square(scene, 30.0)])
    box, _, _ = motor.scatter(scene, _params(count=20), tris=tris)
    proto_mesh = box.children[0].mesh
    i = scene.groups.index(box)
    new, placed, _ = motor.scatter(scene, _params(count=35, seed=99), old=box)
    assert box not in scene.groups and scene.groups[i] is new
    assert placed == 35
    # The copies share the very definition the old ones used: nothing re-read.
    assert new.children[0].mesh is proto_mesh


def test_a_model_component_can_be_scattered(scene):
    from PySide6.QtGui import QMatrix4x4
    from core.group import Group
    from core.mesh import Mesh
    m = Mesh()
    m.add_face([QVector3D(*p) for p in [(5, 5, 2), (6, 5, 2), (6, 6, 2), (5, 6, 2)]])
    rock = Group(m, name="Rock")
    rock.xform = QMatrix4x4()
    rock.component = True
    scene.groups.append(rock)
    assert [g.name for g in motor.model_components(scene)] == ["Rock"]
    tris = motor.surface_from_selection([_square(scene)])
    box, placed, _ = motor.scatter(scene, _params(
        sources=[{"kind": "model", "name": "Rock"}], count=10), tris=tris)
    assert placed == 10 and all(k.mesh is rock.mesh for k in box.children)
    assert motor.model_components(scene) == [rock]      # the scatter is not one


def test_terrain_asked_but_missing_says_so(scene):
    tris = motor.surface_from_selection([_square(scene)])
    with pytest.raises(ValueError):
        motor.scatter(scene, _params(terrain=True), tris=tris, terrain=None)


def test_saved_and_opened_it_keeps_sharing_and_numbers(scene, tmp_path):
    from core.scene import Scene
    from formats import igz
    tris = motor.surface_from_selection([_square(scene, 30.0)])
    motor.scatter(scene, _params(sources=[TREE], count=25), tris=tris)
    path = tmp_path / "s.igz"
    igz.save_scene(scene, path)
    back = Scene()
    igz.load_into(back, path)
    box = next(g for g in back.groups if motor.is_scatter(g))
    assert len(box.children) == 25
    assert len({id(k.mesh) for k in box.children}) == 1
    assert box.ext[motor.KEY]["placed"] == 25
    # And it scatters again from the file alone.
    new, placed, _ = motor.scatter(back, _params(sources=[TREE], count=10), old=box)
    assert placed == 10


def test_a_second_scatter_shares_the_first_ones_objects(scene):
    a, _, _ = motor.scatter(scene, _params(count=5),
                            tris=motor.surface_from_selection([_square(scene)]))
    far = scene.mesh.add_face([QVector3D(x, y, 0) for x, y in
                               [(50, 0), (60, 0), (60, 10), (50, 10)]])
    b, _, _ = motor.scatter(scene, _params(count=5),
                            tris=motor.surface_from_selection([far]))
    assert b.children[0].mesh is a.children[0].mesh
