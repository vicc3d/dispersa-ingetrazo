# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Victor Crespo (3dvic.com · github.com/vicc3d)
"""Scattering, with no interface: the surface as triangles, the points on
it, and the container group whose copies share their objects' geometry.

A scatter is ONE group (``component = False``) holding one placement per
copy. Every placement of the same object shares that object's mesh and only
carries its own matrix, so two thousand trees weigh one tree. The group
remembers how it was made in ``group.ext[KEY]`` (the surface included), so
it can be scattered again with other numbers.

Since 0.2 a scatter also keeps its brush strokes (each with the objects,
amount and size it was painted with; a Shift stroke takes copies away)
and its zones kept clear (plan outlines nothing goes into). Scattering
again redoes all of it from the seed, so nothing painted is lost.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from .texts import tr

KEY = "dispersa"
LAYER = "Dispersa"
FORMAT = 1

DEFAULTS = {
    "mode": "count",          # "count": number of copies; "density": per 100 m²
    "count": 50,
    "density": 4.0,
    "min_distance": 1.0,      # metres between copies (0 = no limit)
    "scale": [80.0, 120.0],   # percent, from and to
    "rotation": 360.0,        # degrees, turned at random from 0 to this
    "align": False,           # lean with the surface instead of upright
    "terrain": False,         # drop every point onto scene.terrain
    "max_slope": 40.0,        # degrees; only for the faces of groups
    "seed": 1,
    "brush": 2.0,             # brush radius, metres
    "brush_density": 4.0,     # what the brush paints, copies per 100 m²
}


# ---- The objects ---------------------------------------------------------------

def bundled_root() -> Path:
    from core.paths import app_root
    return app_root() / "resources" / "components"


def bundled_entries() -> list[dict]:
    """IngeTrazo's own 3D starters (components.json): key, name, tip and
    the thumbnail, the ones whose .igz is there."""
    root = bundled_root()
    try:
        entries = json.loads((root / "components.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    for e in entries:
        if (root / f"{e['key']}.igz").is_file():
            out.append({**e, "thumb": str(root / "thumbs" / f"{e['key']}.png")})
    return out


def model_components(scene) -> list:
    """The components placed in the model, one per definition (the first
    copy found stands for it). Scatters are left out."""
    seen, out = set(), []
    for g in scene.groups:
        if not g.is_component() or is_scatter(g):
            continue
        if id(g.mesh) in seen:
            continue
        seen.add(id(g.mesh))
        out.append(g)
    return out


def _clean_prototype(group):
    """A placement of ``group``'s definition at its own pose: shared mesh
    and subgroups, nothing of how that copy was left."""
    from PySide6.QtGui import QMatrix4x4
    from core.group import copy_group
    p = copy_group(group)
    p.xform = QMatrix4x4()
    p.component = True
    p.hidden = p.locked = False
    p.material = p.layer = p.ifc = None
    p.exploded = p.explode_offset = None
    p.axes = None
    p.ext = None
    return p


def bundled_prototype(key: str, name: str | None = None):
    """IngeTrazo's starter ``key`` read from its .igz, as a component."""
    from PySide6.QtGui import QMatrix4x4
    from core.group import Group
    from core.scene import Scene
    from formats import igz
    path = bundled_root() / f"{key}.igz"
    temp = Scene()
    igz.load_into(temp, path)
    if not temp.groups:
        raise ValueError(tr("Could not read {name}.", name=name or key))
    g = Group(temp.groups[0].mesh, name=name or key)
    g.xform = QMatrix4x4()
    g.component = True
    return g


def model_prototype(scene, name: str):
    for g in model_components(scene):
        if g.name == name:
            return _clean_prototype(g)
    return None


def anchor(proto) -> tuple:
    """Where a copy stands: the centre of the bottom of the object's box,
    in its own coordinates. The starters are drawn metres away from their
    origin, so their origin cannot be it."""
    from core.group import placement_points
    pts = placement_points(proto)
    if not len(pts):
        return (0.0, 0.0, 0.0)
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    return (float(lo[0] + hi[0]) / 2, float(lo[1] + hi[1]) / 2, float(lo[2]))


# ---- The surface -----------------------------------------------------------------

def is_scatter(group) -> bool:
    return KEY in (getattr(group, "ext", None) or {})


def surface_from_selection(selection, max_slope: float = 40.0) -> list:
    """The selected faces and groups as world triangles ``[ax, ay, az, bx,
    …, cz]``. A selected face is taken whole, turned up if it faces down;
    from a group, only what faces up at most ``max_slope`` from level —
    its roof and its floor, not its walls. Scatters are skipped."""
    from core.group import Group, iter_placements
    from core.mesh import Face
    tris = []
    for ent in selection:
        if isinstance(ent, Face):
            n = ent.normal()
            for a, b, c in ent.triangulate():
                tris.append(_tri(a, b, c, up=n.z() < 0))
        elif isinstance(ent, Group) and not is_scatter(ent):
            cos_max = math.cos(math.radians(max_slope))
            for g, m in iter_placements(ent):
                for f in g.mesh.faces:
                    for a, b, c in f.triangulate():
                        if m is not None:
                            a, b, c = m.map(a), m.map(b), m.map(c)
                        t = _tri(a, b, c)
                        n = _normal(t)
                        if n is not None and n[2] >= cos_max - 1e-9:
                            tris.append(t)
    return [t for t in tris if _area(t) > 1e-6]


def _tri(a, b, c, up=False):
    t = [a.x(), a.y(), a.z(), b.x(), b.y(), b.z(), c.x(), c.y(), c.z()]
    if up:
        t = t[0:3] + t[6:9] + t[3:6]
    return [round(v, 4) for v in t]


def _cross(t):
    ux, uy, uz = t[3] - t[0], t[4] - t[1], t[5] - t[2]
    vx, vy, vz = t[6] - t[0], t[7] - t[1], t[8] - t[2]
    return (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)


def _area(t) -> float:
    x, y, z = _cross(t)
    return 0.5 * math.sqrt(x * x + y * y + z * z)


def _normal(t):
    x, y, z = _cross(t)
    n = math.sqrt(x * x + y * y + z * z)
    return None if n < 1e-12 else (x / n, y / n, z / n)


#: Above this many faces the panel does not measure the selection as you
#: select it: ``surface_from_selection`` triangulates every face in Python
#: (about 20 µs each), so a 600 000-face group froze IngeTrazo for 20 s on
#: every selection change. Past it, the surface is measured when the button
#: is pressed.
BIG_SELECTION = 20_000


def selection_face_count(selection) -> int:
    """How many faces ``surface_from_selection`` would look at: counted from
    the shared meshes (milliseconds), without touching a face."""
    from core.group import Group, iter_placements
    from core.mesh import Face
    n = 0
    for ent in selection:
        if isinstance(ent, Face):
            n += 1
        elif isinstance(ent, Group) and not is_scatter(ent):
            n += sum(len(g.mesh.faces) for g, _m in iter_placements(ent))
    return n


def surface_area(tris) -> float:
    return sum(_area(t) for t in tris)


# ---- The points ------------------------------------------------------------------

def _terrain_normal(terrain, x, y, z):
    d = 0.5
    zx = terrain.height_at(x + d, y)
    zy = terrain.height_at(x, y + d)
    if zx is None or zy is None:
        return (0.0, 0.0, 1.0)
    nx, ny = -(zx - z) / d, -(zy - z) / d
    n = math.sqrt(nx * nx + ny * ny + 1.0)
    return (nx / n, ny / n, 1.0 / n)


def scatter_points(tris, params, terrain=None):
    """``[(point, normal)]`` spread at random over ``tris``, reproducible by
    the seed, at least ``min_distance`` apart. With ``terrain`` the points
    keep their place in plan and take the ground's height (points off the
    captured ground are left out). Returns (points, wanted)."""
    p = {**DEFAULTS, **params}
    rnd = random.Random(int(p["seed"]))
    area = surface_area(tris)
    if p["mode"] == "density":
        wanted = int(round(area * float(p["density"]) / 100.0))
    else:
        wanted = int(p["count"])
    wanted = max(0, min(wanted, 20000))
    if not tris or wanted == 0:
        return [], wanted
    # Area-weighted choice of triangle.
    acc, total = [], 0.0
    for t in tris:
        total += _area(t)
        acc.append(total)
    import bisect
    dmin = max(0.0, float(p["min_distance"]))
    cell = dmin if dmin > 0 else None
    grid: dict = {}
    out = []
    attempts = 0
    limit = wanted * 30
    while len(out) < wanted and attempts < limit:
        attempts += 1
        t = tris[min(bisect.bisect_left(acc, rnd.random() * total), len(tris) - 1)]
        r1, r2 = rnd.random(), rnd.random()
        s = math.sqrt(r1)
        u, v, w = 1 - s, s * (1 - r2), s * r2
        x = u * t[0] + v * t[3] + w * t[6]
        y = u * t[1] + v * t[4] + w * t[7]
        z = u * t[2] + v * t[5] + w * t[8]
        n = _normal(t)
        if n is not None and n[2] < 0:
            n = (-n[0], -n[1], -n[2])
        if terrain is not None:
            h = terrain.height_at(x, y)
            if h is None:
                continue
            z = h
            n = _terrain_normal(terrain, x, y, z)
        if cell is not None:
            k = (math.floor(x / cell), math.floor(y / cell), math.floor(z / cell))
            near = False
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    for m in (-1, 0, 1):
                        for q in grid.get((k[0] + i, k[1] + j, k[2] + m), ()):
                            if (q[0] - x) ** 2 + (q[1] - y) ** 2 + (q[2] - z) ** 2 < dmin * dmin:
                                near = True
                                break
                        if near:
                            break
                    if near:
                        break
                if near:
                    break
            if near:
                continue
            grid.setdefault(k, []).append((x, y, z))
        out.append(((x, y, z), n or (0.0, 0.0, 1.0)))
    return out, wanted


# ---- The scatter -------------------------------------------------------------------

def _align_matrix(n):
    """A rotation taking Z up to the normal ``n``."""
    from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D
    m = QMatrix4x4()
    q = QQuaternion.rotationTo(QVector3D(0, 0, 1), QVector3D(*n))
    m.rotate(q)
    return m


def _pick(rnd, weights):
    total = sum(weights)
    r = rnd.random() * total
    for i, w in enumerate(weights):
        r -= w
        if r < 0:
            return i
    return len(weights) - 1


# ---- Brush strokes and zones kept clear ----------------------------------------

def _seg_dist2(px, py, ax, ay, bx, by) -> float:
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L <= 1e-18 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    qx, qy = ax + t * dx - px, ay + t * dy - py
    return qx * qx + qy * qy


def near_path(path, r, x, y) -> bool:
    """Is plan point (x, y) within ``r`` of the stroke ``path``?"""
    r2 = r * r
    if len(path) == 1:
        return (path[0][0] - x) ** 2 + (path[0][1] - y) ** 2 <= r2
    for a, b in zip(path, path[1:]):
        if _seg_dist2(x, y, a[0], a[1], b[0], b[1]) <= r2:
            return True
    return False


def _path_box(path, r):
    xs = [q[0] for q in path]
    ys = [q[1] for q in path]
    return (min(xs) - r, min(ys) - r, max(xs) + r, max(ys) + r)


def stroke_surface(tris, path, r, max_slope=90.0) -> list:
    """The triangles of ``tris`` a stroke can paint on: under its band in
    plan and no steeper than ``max_slope`` (walls are not painted)."""
    x0, y0, x1, y1 = _path_box(path, r)
    cos_max = math.cos(math.radians(max_slope))
    out = []
    for t in tris:
        if (max(t[0], t[3], t[6]) < x0 or min(t[0], t[3], t[6]) > x1
                or max(t[1], t[4], t[7]) < y0 or min(t[1], t[4], t[7]) > y1):
            continue
        n = _normal(t)
        if n is None or abs(n[2]) < cos_max - 1e-9:
            continue
        if n[2] < 0:
            t = list(t[0:3]) + list(t[6:9]) + list(t[3:6])
        out.append([round(v, 4) for v in t])
    return out


def footprint(selection) -> list:
    """What the selected faces and groups cover in plan, as flat triangles
    ``[ax, ay, bx, by, cx, cy]``: a zone to keep clear. Scatters are
    skipped. Faces standing upright cover nothing and are left out."""
    from core.group import Group, iter_placements
    from core.mesh import Face
    out = []

    def add(a, b, c):
        t = [a.x(), a.y(), b.x(), b.y(), c.x(), c.y()]
        if abs((t[2] - t[0]) * (t[5] - t[1]) - (t[3] - t[1]) * (t[4] - t[0])) > 1e-6:
            out.append([round(v, 4) for v in t])

    for ent in selection:
        if isinstance(ent, Face):
            for a, b, c in ent.triangulate():
                add(a, b, c)
        elif isinstance(ent, Group) and not is_scatter(ent):
            for g, m in iter_placements(ent):
                for f in g.mesh.faces:
                    for a, b, c in f.triangulate():
                        if m is not None:
                            a, b, c = m.map(a), m.map(b), m.map(c)
                        add(a, b, c)
    return out


class _Clear:
    """Point-in-zone in plan, fast enough for thousands of points: the
    zones' triangles bucketed on a grid."""

    def __init__(self, zones):
        tris = [t for z in zones for t in z]
        self.tris = tris
        self.grid = {}
        if not tris:
            return
        xs = [v for t in tris for v in t[0::2]]
        ys = [v for t in tris for v in t[1::2]]
        span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
        self.cell = max(span / 64.0, 0.25)
        c = self.cell
        for i, t in enumerate(tris):
            for gx in range(math.floor(min(t[0::2]) / c), math.floor(max(t[0::2]) / c) + 1):
                for gy in range(math.floor(min(t[1::2]) / c), math.floor(max(t[1::2]) / c) + 1):
                    self.grid.setdefault((gx, gy), []).append(i)

    def __contains__(self, xy) -> bool:
        if not self.tris:
            return False
        x, y = xy
        for i in self.grid.get((math.floor(x / self.cell), math.floor(y / self.cell)), ()):
            ax, ay, bx, by, cx, cy = self.tris[i]
            d1 = (x - bx) * (ay - by) - (ax - bx) * (y - by)
            d2 = (x - cx) * (by - cy) - (bx - cx) * (y - cy)
            d3 = (x - ax) * (cy - ay) - (cx - ax) * (y - ay)
            neg = d1 < 0 or d2 < 0 or d3 < 0
            pos = d1 > 0 or d2 > 0 or d3 > 0
            if not (neg and pos):
                return True
        return False


class _Spread:
    """The copies so far, on a grid, to keep them ``dmin`` apart and to
    take away the ones a Shift stroke passes over."""

    def __init__(self, dmin):
        self.dmin = dmin
        self.cell = dmin if dmin > 0 else 1.0
        self.grid = {}
        self.items = []

    def _key(self, x, y, z):
        c = self.cell
        return (math.floor(x / c), math.floor(y / c), math.floor(z / c))

    def near(self, x, y, z) -> bool:
        d = self.dmin
        if d <= 0:
            return False
        k = self._key(x, y, z)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for m in (-1, 0, 1):
                    for it in self.grid.get((k[0] + i, k[1] + j, k[2] + m), ()):
                        q = it[0]
                        if (q[0] - x) ** 2 + (q[1] - y) ** 2 + (q[2] - z) ** 2 < d * d:
                            return True
        return False

    def add(self, item) -> None:
        self.items.append(item)
        self.grid.setdefault(self._key(*item[0]), []).append(item)

    def erase(self, path, r) -> None:
        x0, y0, x1, y1 = _path_box(path, r)
        keep = []
        for it in self.items:
            x, y = it[0][0], it[0][1]
            if x0 <= x <= x1 and y0 <= y <= y1 and near_path(path, r, x, y):
                self.grid[self._key(*it[0])].remove(it)
            else:
                keep.append(it)
        self.items = keep


def _sampler(tris):
    acc, total = [], 0.0
    for t in tris:
        total += _area(t)
        acc.append(total)
    import bisect

    def sample(rnd):
        t = tris[min(bisect.bisect_left(acc, rnd.random() * total), len(tris) - 1)]
        r1, r2 = rnd.random(), rnd.random()
        s = math.sqrt(r1)
        u, v, w = 1 - s, s * (1 - r2), s * r2
        x = u * t[0] + v * t[3] + w * t[6]
        y = u * t[1] + v * t[4] + w * t[7]
        z = u * t[2] + v * t[5] + w * t[8]
        n = _normal(t)
        if n is not None and n[2] < 0:
            n = (-n[0], -n[1], -n[2])
        return x, y, z, n
    return sample, total


def _choose(rnd, look):
    """Which object, how big, how turned: drawn from ``rnd`` the moment a
    copy is kept, so later strokes never reshuffle earlier copies."""
    srcs, weights, smin, smax, rot, align = look
    i = srcs[_pick(rnd, weights)]
    return i, rnd.uniform(smin, smax) / 100.0, rnd.uniform(0.0, rot), align


def _look(p, objects, sources):
    idx = [next(k for k, o in enumerate(objects) if _same_source(o, s)) for s in sources]
    weights = [max(0.0, float(s.get("weight", 1))) for s in sources]
    if sum(weights) <= 0:
        weights = [1.0] * len(sources)
    smin, smax = sorted(float(v) for v in p["scale"])
    return idx, weights, smin, smax, float(p["rotation"]), bool(p["align"])


def _drop(terrain, x, y, z, n):
    if terrain is None:
        return x, y, z, n
    h = terrain.height_at(x, y)
    if h is None:
        return None
    return x, y, h, _terrain_normal(terrain, x, y, h)


def all_points(p, objects, tris, strokes=(), clear=(), terrain=None):
    """Every copy of a scatter, in order: the surface first, then each
    stroke (painting adds, Shift takes away); nothing inside a zone kept
    clear. Returns ([(point, normal, (object, scale, angle, align))],
    wanted on the surface)."""
    p = {**DEFAULTS, **p}
    zones = _Clear(clear)
    spread = _Spread(max(0.0, float(p["min_distance"])))
    seed = int(p["seed"])
    wanted = 0
    # The surface: the same draws, in the same order, as 0.1 made them.
    if tris and p.get("sources"):
        area = surface_area(tris)
        if p["mode"] == "density":
            wanted = int(round(area * float(p["density"]) / 100.0))
        else:
            wanted = int(p["count"])
        wanted = max(0, min(wanted, 20000))
        rnd = random.Random(seed)
        pick = random.Random(seed * 7919 + 17)
        look = _look(p, objects, p["sources"])
        sample, _total = _sampler(tris)
        kept, attempts = 0, 0
        while kept < wanted and attempts < wanted * 30:
            attempts += 1
            got = _drop(terrain if p["terrain"] else None, *sample(rnd))
            if got is None:
                continue
            x, y, z, n = got
            if (x, y) in zones or spread.near(x, y, z):
                continue
            spread.add(((x, y, z), n or (0.0, 0.0, 1.0), _choose(pick, look)))
            kept += 1
    for k, st in enumerate(strokes):
        path, r = st["path"], float(st["r"])
        if not path or r <= 0:
            continue
        if st.get("erase"):
            spread.erase(path, r)
            continue
        q = {**p, **st}
        if st.get("terrain"):
            if terrain is None:
                continue
            x0, y0, x1, y1 = _path_box(path, r)
            st_tris = [[x0, y0, 0, x1, y0, 0, x1, y1, 0],
                       [x0, y0, 0, x1, y1, 0, x0, y1, 0]]
        else:
            st_tris = st.get("tris") or []
        if not st_tris or not st.get("sources"):
            continue
        sample, total = _sampler(st_tris)
        trials = min(200000, int(round(total * float(q["density"]) / 100.0)))
        rnd = random.Random(seed * 100003 + 7919 * (k + 1))
        pick = random.Random(seed * 7919 + 17 + 104729 * (k + 1))
        look = _look(q, objects, st["sources"])
        for _ in range(trials):
            x, y, z, n = sample(rnd)
            if not near_path(path, r, x, y):
                continue
            got = _drop(terrain if st.get("terrain") else None, x, y, z, n)
            if got is None:
                continue
            x, y, z, n = got
            if (x, y) in zones or spread.near(x, y, z):
                continue
            spread.add(((x, y, z), n or (0.0, 0.0, 1.0), _choose(pick, look)))
    return spread.items, wanted


def all_sources(params, strokes=()) -> list:
    """Every object the scatter uses, once: the surface's, then each
    stroke's. Copies point into this list."""
    out = []
    for s in list(params.get("sources") or []) + [
            s for st in strokes for s in (st.get("sources") or [])]:
        if not any(_same_source(o, s) for o in out):
            out.append({k: s[k] for k in s if k != "weight"})
    return out


# ---- The scatter -------------------------------------------------------------------

def build(params, prototypes, tris, terrain=None, name=None, strokes=(), clear=()):
    """The container group: one placement per point, each sharing its
    object's definition. ``prototypes`` is one component per object of
    :func:`all_sources`. Returns (group, placed, wanted)."""
    from PySide6.QtGui import QMatrix4x4, QVector3D
    from core.group import Group, copy_group
    from core.mesh import Mesh
    p = {**DEFAULTS, **params}
    strokes = [dict(st) for st in strokes]
    objects = all_sources(p, strokes)
    if not objects:
        raise ValueError(tr("Choose at least one object to scatter."))
    if len(prototypes) != len(objects):
        raise ValueError("one prototype per object")
    anchors = [anchor(pr) for pr in prototypes]
    items, wanted = all_points(p, objects, tris, strokes, clear,
                               terrain)
    kids = []
    for (pt, n, (i, s, angle, align)) in items:
        m = QMatrix4x4()
        m.translate(QVector3D(*pt))
        if align:
            m = m * _align_matrix(n)
        m.rotate(angle, 0.0, 0.0, 1.0)
        m.scale(s)
        ax, ay, az = anchors[i]
        m.translate(-ax, -ay, -az)
        g = copy_group(prototypes[i])
        g.xform = m
        g.ext = {KEY: {"src": i}}
        kids.append(g)
    box = Group(Mesh(), name=name or container_name(objects))
    box.adopt(kids)
    box.component = False
    box.layer = LAYER
    stored = {k: p[k] for k in DEFAULTS}
    stored.update({"format": FORMAT, "sources": [dict(s) for s in p.get("sources") or []],
                   "objects": objects,
                   "surface": [list(t) for t in tris], "strokes": strokes,
                   "clear": [list(map(list, z)) for z in clear],
                   "placed": len(kids), "wanted": wanted})
    box.ext = {KEY: stored}
    return box, len(kids), wanted


def container_name(sources) -> str:
    names = [s.get("name") or s.get("key") or "?" for s in sources]
    text = ", ".join(names[:3]) + ("…" if len(names) > 3 else "")
    return "Dispersa: " + text


def prototypes_for(scene, sources, old=None):
    """One component per source: taken from the copies of a scatter when
    there are some (its object may be gone from the model), otherwise
    read: a starter from its file, a model component by name."""
    # Every definition the scatters in the model already hold, the one
    # being redone first: a second scatter of trees shares the first one's
    # tree instead of reading the file again.
    known = []
    boxes = ([old] if old is not None else []) + [
        g for g in scene.groups if is_scatter(g) and g is not old]
    for box in boxes:
        e = box.ext[KEY]
        olds = e.get("objects") or e.get("sources", [])
        seen = set()
        for k in box.children or ():
            i = ((k.ext or {}).get(KEY) or {}).get("src")
            if i is None or i >= len(olds) or i in seen:
                continue
            seen.add(i)
            known.append((olds[i], k))
    out = []
    for s in sources:
        proto = next((_clean_prototype(k) for o, k in known
                      if _same_source(o, s)), None)
        if proto is None:
            if s.get("kind") == "bundled":
                proto = bundled_prototype(s["key"], s.get("name"))
            else:
                proto = model_prototype(scene, s.get("name", ""))
        if proto is None:
            raise ValueError(tr("“{name}” is no longer in the model.",
                                name=s.get("name", "?")))
        out.append(proto)
    return out


def _same_source(a, b) -> bool:
    if a.get("kind") != b.get("kind"):
        return False
    if a.get("kind") == "bundled":
        return a.get("key") == b.get("key")
    return a.get("name") == b.get("name")


def prepare(scene, params, tris=None, old=None, terrain=None,
            strokes=None, clear=None):
    """Build a scatter beside the scene, touching nothing: everything that
    can go wrong goes wrong here, before the undo step starts. With
    ``old``, its surface, strokes and zones are reused where these are
    None, and its objects' definitions are taken from its copies.
    Returns (group, placed, wanted)."""
    e = old.ext[KEY] if old is not None else {}
    if tris is None:
        if old is None:
            raise ValueError(tr("Select faces or a group to scatter on."))
        tris = e["surface"]
    if strokes is None:
        strokes = e.get("strokes") or []
    if clear is None:
        clear = e.get("clear") or []
    if not tris and not any(not st.get("erase") for st in strokes):
        raise ValueError(tr("The selection has no surface to scatter on."))
    uses_terrain = (params.get("terrain") and tris) or any(
        st.get("terrain") and not st.get("erase") for st in strokes)
    if uses_terrain and terrain is None:
        raise ValueError(tr("There is no 3D terrain yet: build it in the "
                            "Terrain tab, or untick “On the terrain”."))
    objects = all_sources(params, strokes)
    if not objects:
        raise ValueError(tr("Choose at least one object to scatter."))
    protos = prototypes_for(scene, objects, old)
    box, placed, wanted = build(params, protos, tris, terrain,
                                strokes=strokes, clear=clear)
    if old is not None:
        # A name the user gave stays; the automatic one follows the objects.
        if old.name != container_name(e.get("objects") or e.get("sources", [])):
            box.name = old.name
        box.layer = old.layer
        box.hidden = old.hidden
    return box, placed, wanted


def place(scene, box, old=None) -> None:
    """Put a prepared scatter in ``scene``, in the place of ``old`` if it
    is there (no undo: callers wrap this in ``SnapshotImport``)."""
    from core.layers import Layer
    if box.layer and not any(ly.name == box.layer for ly in scene.layers):
        scene.layers.append(Layer(box.layer))
    if old is not None and old in scene.groups:
        scene.groups[scene.groups.index(old)] = box
        scene.selection.discard(old)
    else:
        scene.groups.append(box)
    scene.version += 1


def scatter(scene, params, tris=None, old=None, terrain=None,
            strokes=None, clear=None):
    """Prepare and place at once (tests, the Python Console)."""
    box, placed, wanted = prepare(scene, params, tris, old, terrain,
                                  strokes, clear)
    place(scene, box, old)
    return box, placed, wanted
