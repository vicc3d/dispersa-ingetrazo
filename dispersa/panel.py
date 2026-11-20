# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Victor Crespo (3dvic.com · github.com/vicc3d)
"""The Dispersa tab, in boxes that follow the work: choose a way (scatter
over a selection, or paint with the brush), then the objects, where or
the brush, how many, the variation, the zones kept clear, and one button.
Selecting a scatter brings its numbers back to change them."""
from __future__ import annotations

import random

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDoubleSpinBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QSpinBox, QToolButton,
    QVBoxLayout, QWidget)

from . import motor
from .icons import icon
from .texts import tr

_STYLE = """
QFrame#card { background: palette(base); border: 1px solid palette(midlight);
              border-radius: 10px; }
QLabel#title { font-weight: bold; }
QLabel#step { border: 1px solid palette(highlight); color: palette(highlight);
              border-radius: 9px; font-weight: bold;
              min-width: 18px; max-width: 18px; min-height: 18px; max-height: 18px;
              qproperty-alignment: AlignCenter; font-size: 11px; }
QLabel#big { font-size: 17px; font-weight: bold; }
QDoubleSpinBox#bigspin { font-size: 15px; font-weight: bold; padding: 2px; }
QLabel#hint { color: palette(placeholder-text); font-size: 11px; }
QFrame#tile { border: 1px solid palette(midlight); border-radius: 8px;
              background: palette(base); }
QFrame#tile[on="true"] { border: 2px solid palette(highlight); }
QLabel#badge { color: palette(highlight); font-weight: bold; font-size: 11px; }
QToolButton#seg { border: none; border-radius: 6px; padding: 6px 4px; }
QToolButton#seg:checked { background: palette(highlight);
                          color: palette(highlighted-text); font-weight: bold; }
QFrame#segbar { background: palette(base); border: 1px solid palette(midlight);
                border-radius: 8px; }
QPushButton#primary { background: palette(highlight); color: palette(highlighted-text);
                      border: none; border-radius: 7px; padding: 9px; font-weight: bold; }
QPushButton#primary:disabled { background: transparent; color: palette(placeholder-text);
                               border: 1px solid palette(midlight); }
QPushButton#primary:checked { background: palette(dark); }
QToolButton#tiny { border: 1px solid palette(midlight); border-radius: 4px;
                   padding: 0px; min-width: 16px; min-height: 16px; }
QToolButton#action { border: 1px solid palette(midlight); border-radius: 8px;
                     padding: 6px; background: palette(base); }
"""


def _core_tr(text: str) -> str:
    try:
        from core.i18n import tr as core_tr
        return core_tr(text)
    except Exception:                    # noqa: BLE001
        return text


def _card(step, title, icon_key=None):
    """A box of the bento: a numbered (or plain) title and its content."""
    frame = QFrame()
    frame.setObjectName("card")
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(10, 8, 10, 10)
    lay.setSpacing(6)
    head = QHBoxLayout()
    head.setSpacing(6)
    if step:
        num = QLabel(str(step))
        num.setObjectName("step")
        head.addWidget(num)
    elif icon_key:
        pic = QLabel()
        pic.setPixmap(icon(icon_key).pixmap(16, 16))
        head.addWidget(pic)
    label = QLabel(title)
    label.setObjectName("title")
    head.addWidget(label)
    head.addStretch(1)
    if step and icon_key:
        pic = QLabel()
        pic.setPixmap(icon(icon_key).pixmap(16, 16))
        head.addWidget(pic)
    lay.addLayout(head)
    frame.title = label
    frame.head = head
    return frame, lay


def _row(icon_key, text, widget):
    """An icon, a few words and the control, on one line."""
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(6)
    pic = QLabel()
    pic.setPixmap(icon(icon_key).pixmap(16, 16))
    h.addWidget(pic)
    lab = QLabel(text)
    h.addWidget(lab, 1)
    if widget is not None:
        h.addWidget(widget)
    return w


class ObjectTile(QFrame):
    """One object: its picture and name; click to choose it. Chosen, it
    shows how often it comes out against the others (×1 … ×100)."""
    changed = Signal()

    def __init__(self, src, thumb, tip):
        super().__init__()
        self.setObjectName("tile")
        self.src = src
        self.setToolTip(tip)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(92)
        v = QVBoxLayout(self)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(2)
        pic = QLabel()
        pic.setAlignment(Qt.AlignCenter)
        ic = QIcon(thumb) if thumb else icon("model")
        pic.setPixmap(ic.pixmap(40, 40))
        v.addWidget(pic)
        name = QLabel(src["name"])
        name.setAlignment(Qt.AlignCenter)
        name.setObjectName("hint")
        name.setMinimumWidth(10)
        v.addWidget(name)
        row = QHBoxLayout()
        row.setSpacing(2)
        self.less, self.more = QToolButton(), QToolButton()
        for b, t in ((self.less, "−"), (self.more, "+")):
            b.setObjectName("tiny")
            b.setText(t)
            b.setAutoRaise(True)
        self.badge = QLabel()
        self.badge.setObjectName("badge")
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setToolTip(tr("How often this object comes out, against the others"))
        row.addWidget(self.less)
        row.addWidget(self.badge, 1)
        row.addWidget(self.more)
        v.addLayout(row)
        self.less.clicked.connect(lambda: self.set_weight(self.weight - 1))
        self.more.clicked.connect(lambda: self.set_weight(self.weight + 1))
        self.weight = 1
        self.checked = False
        self._paint()

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.LeftButton:
            self.set_checked(not self.checked)
            self.changed.emit()
        super().mousePressEvent(ev)

    def set_checked(self, on: bool) -> None:
        self.checked = bool(on)
        self._paint()

    def set_weight(self, w: int) -> None:
        self.weight = max(1, min(100, int(w)))
        self._paint()

    def _paint(self) -> None:
        self.setProperty("on", "true" if self.checked else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.badge.setText(f"×{self.weight}" if self.checked else "")
        for b in (self.less, self.more):
            b.setVisible(self.checked)


class ScatterPanel(QWidget):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self._editing = None             # the scatter being edited, if any
        self._last = None                # the last scatter made or edited
        self._tool = None                # the brush, made when first used
        self._busy = False               # scattering: the button waits
        self._sel_key = None
        self._tris = []
        self._pending = None             # a big selection, measured on the button
        self._stale = False              # the model changed while hidden
        self.tiles = []
        self.setStyleSheet(_STYLE)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        lay = QVBoxLayout(body)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # The two ways
        bar = QFrame()
        bar.setObjectName("segbar")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(3, 3, 3, 3)
        bl.setSpacing(3)
        self.way = QButtonGroup(self)
        self.way_scatter, self.way_brush = QToolButton(), QToolButton()
        for b, key, text, tip in (
                (self.way_scatter, "scatter", tr("Scatter"),
                 tr("Spread copies over the selected faces, a group or the terrain")),
                (self.way_brush, "brush", tr("Brush"),
                 tr("Paint copies by hand where you drag"))):
            b.setObjectName("seg")
            b.setCheckable(True)
            b.setIcon(icon(key))
            b.setIconSize(QSize(18, 18))
            b.setText(text)
            b.setToolTip(tip)
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            b.setSizePolicy(b.sizePolicy().horizontalPolicy().Expanding,
                            b.sizePolicy().verticalPolicy())
            self.way.addButton(b)
            bl.addWidget(b, 1)
        self.way_scatter.setChecked(True)
        self.way.buttonToggled.connect(lambda _b, _on: self._way_changed())
        lay.addWidget(bar)

        # 1 · Objects
        card, cl = _card(1, tr("Objects"), "objects")
        self.grid = QGridLayout()
        self.grid.setSpacing(6)
        cl.addLayout(self.grid)
        lay.addWidget(card)

        # Shared controls, moved between boxes with the way
        self.terrain = QCheckBox()
        self.terrain.setToolTip(tr("Drop every copy onto the 3D terrain of the "
                                   "Terrain tab, inside the selected area"))
        self.distance = QDoubleSpinBox()
        self.distance.setRange(0.0, 100.0)
        self.distance.setDecimals(2)
        self.distance.setSingleStep(0.25)
        self.distance.setSuffix(" m")
        self.distance.setToolTip(tr("The least distance from one copy to the next "
                                    "(0 = no limit)"))
        self.terrain_row = _row("terrain", tr("On the terrain"), self.terrain)
        self.distance_row = _row("spacing", tr("Spacing"), self.distance)

        # 2 · Where  +  3 · How many   (scatter)
        self.scatter_box = QWidget()
        duo = QHBoxLayout(self.scatter_box)
        duo.setContentsMargins(0, 0, 0, 0)
        duo.setSpacing(8)
        card, cl = _card(2, tr("Where"))
        self.where_big = QLabel("—")
        self.where_big.setObjectName("big")
        cl.addWidget(self.where_big)
        self.where = QLabel()
        self.where.setObjectName("hint")
        self.where.setWordWrap(True)
        cl.addWidget(self.where)
        self.where_layout = cl
        self.max_slope = QDoubleSpinBox()
        self.max_slope.setRange(0.0, 90.0)
        self.max_slope.setDecimals(0)
        self.max_slope.setSuffix(" °")
        self.max_slope.setToolTip(tr("From a group, only the faces this close to "
                                     "level (its floors and roofs, not its walls)"))
        self.max_slope.valueChanged.connect(lambda _v: self._refresh_selection(True))
        cl.addWidget(_row("slope", tr("Steepest"), self.max_slope))
        cl.addStretch(1)
        duo.addWidget(card, 1)
        card, cl = _card(3, tr("How many"))
        self.amount = QDoubleSpinBox()
        self.amount.setObjectName("bigspin")
        self.mode = QComboBox()
        self.mode.addItem(tr("copies"), "count")
        self.mode.addItem(tr("per 100 m²"), "density")
        self.mode.currentIndexChanged.connect(self._mode_changed)
        cl.addWidget(self.amount)
        cl.addWidget(self.mode)
        self.count_layout = cl
        cl.addStretch(1)
        duo.addWidget(card, 1)
        lay.addWidget(self.scatter_box)

        # 2 · Brush   (brush)
        self.brush_box, cl = _card(2, tr("Brush"), "brush")
        g = QGridLayout()
        g.setSpacing(4)
        self.brush = QDoubleSpinBox()
        self.brush.setRange(0.1, 100.0)
        self.brush.setDecimals(2)
        self.brush.setSingleStep(0.5)
        self.brush.setSuffix(" m")
        self.brush.setToolTip(tr("The brush's radius"))
        self.brush_density = QDoubleSpinBox()
        self.brush_density.setRange(0.01, 1000.0)
        self.brush_density.setDecimals(2)
        self.brush_density.setSingleStep(0.5)
        self.brush_density.setToolTip(tr("How thick the brush paints, with the "
                                         "objects and the variation"))
        for col, (text, w) in enumerate(((tr("Size"), self.brush),
                                         (tr("Copies per 100 m²"), self.brush_density))):
            lab = QLabel(text)
            lab.setObjectName("hint")
            g.addWidget(lab, 0, col)
            g.addWidget(w, 1, col)
        cl.addLayout(g)
        self.brush_layout = cl
        keys = QLabel(tr("Drag: paint · <b>Shift</b>: take away · <b>[ ]</b>: size "
                         "· <b>Esc</b>: stop"))
        keys.setObjectName("hint")
        keys.setWordWrap(True)
        cl.addWidget(keys)
        lay.addWidget(self.brush_box)

        # Variation
        self.var_card, cl = _card(4, tr("Variation"), "variation")
        self.smin, self.smax = QSpinBox(), QSpinBox()
        for s in (self.smin, self.smax):
            s.setRange(1, 1000)
            s.setSingleStep(5)
            s.setSuffix(" %")
        sz = QWidget()
        h = QHBoxLayout(sz)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(4)
        h.addWidget(self.smin)
        h.addWidget(QLabel(tr("to")))
        h.addWidget(self.smax)
        cl.addWidget(_row("size", tr("Size"), sz))
        self.rotation = QDoubleSpinBox()
        self.rotation.setRange(0.0, 360.0)
        self.rotation.setDecimals(0)
        self.rotation.setSuffix(" °")
        self.rotation.setToolTip(tr("Each copy turns at random, from 0 up to "
                                    "this angle"))
        cl.addWidget(_row("turn", tr("Turn up to"), self.rotation))
        self.align = QCheckBox()
        self.align.setToolTip(tr("Copies follow the slope (stones, grass) "
                                 "instead of standing upright (trees, people)"))
        cl.addWidget(_row("slope", tr("Lean with the surface"), self.align))
        seed = QWidget()
        h = QHBoxLayout(seed)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(4)
        self.seed = QSpinBox()
        self.seed.setRange(0, 999999)
        self.seed.setToolTip(tr("The same seed gives the same scatter"))
        new_seed = QToolButton()
        new_seed.setIcon(icon("seed"))
        new_seed.setToolTip(tr("Another random arrangement"))
        new_seed.clicked.connect(self._new_seed)
        h.addWidget(self.seed)
        h.addWidget(new_seed)
        cl.addWidget(_row("seed", tr("Seed"), seed))
        self.var_layout = cl
        lay.addWidget(self.var_card)

        # Keep clear
        card, cl = _card(None, tr("Keep clear"), "clear")
        self.zones = QLabel()
        self.zones.setObjectName("hint")
        card.head.addWidget(self.zones)
        note = QLabel(tr("Nothing goes inside what you select, seen from above: "
                         "a path, a house, a pond."))
        note.setObjectName("hint")
        note.setWordWrap(True)
        cl.addWidget(note)
        two = QHBoxLayout()
        two.setSpacing(6)
        self.clear_btn, self.free_btn = QToolButton(), QToolButton()
        for b, key, text in ((self.clear_btn, "plus", tr("Keep this clear")),
                             (self.free_btn, "erase", tr("Free all"))):
            b.setObjectName("action")
            b.setIcon(icon(key))
            b.setIconSize(QSize(18, 18))
            b.setText(text)
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            b.setSizePolicy(b.sizePolicy().horizontalPolicy().Expanding,
                            b.sizePolicy().verticalPolicy())
            two.addWidget(b, 1)
        self.clear_btn.setToolTip(tr("Keep the selection clear"))
        self.free_btn.setToolTip(tr("Free all zones"))
        self.clear_btn.clicked.connect(self.keep_clear)
        self.free_btn.clicked.connect(self.free_zones)
        cl.addLayout(two)
        lay.addWidget(card)

        # Editing, the button, what happened
        self.editing = QLabel()
        self.editing.setWordWrap(True)
        self.editing.setObjectName("hint")
        lay.addWidget(self.editing)
        self.go = QPushButton()
        self.go.setObjectName("primary")
        self.go.setIcon(icon("scatter"))
        self.go.setDefault(True)
        self.go.clicked.connect(self.run)
        lay.addWidget(self.go)
        self.paint_btn = QPushButton(tr("Paint"))
        self.paint_btn.setObjectName("primary")
        self.paint_btn.setIcon(icon("brush"))
        self.paint_btn.setCheckable(True)
        self.paint_btn.setToolTip(tr("Drag over faces (or the terrain, with “On "
                                     "the terrain”) to add copies; Shift+drag "
                                     "takes them away. [ and ] change the size."))
        self.paint_btn.toggled.connect(self._paint_toggled)
        lay.addWidget(self.paint_btn)
        self.brush_note = QLabel()
        self.brush_note.setObjectName("hint")
        self.brush_note.setAlignment(Qt.AlignCenter)
        self.brush_note.setWordWrap(True)
        lay.addWidget(self.brush_note)
        self.status = QLabel()
        self.status.setWordWrap(True)
        lay.addWidget(self.status)
        lay.addStretch(1)

        self.set_params(motor.DEFAULTS)
        self.fill_objects()
        self._way_changed()
        # IngeTrazo says nothing to extensions when the selection changes:
        # look at it while the tab is on screen (a few objects, cheap).
        self._timer = QTimer(self)
        self._timer.setInterval(400)
        self._timer.timeout.connect(self._tick)
        self._timer.start()
        app.on_document_changed(self._document_changed)
        self._refresh_selection(True)

    # ---- the two ways -----------------------------------------------------------

    def way_name(self) -> str:
        return "brush" if self.way_brush.isChecked() else "scatter"

    def set_way(self, name: str) -> None:
        (self.way_brush if name == "brush" else self.way_scatter).setChecked(True)

    def _way_changed(self) -> None:
        brush = self.way_name() == "brush"
        self.scatter_box.setVisible(not brush)
        self.brush_box.setVisible(brush)
        self.go.setVisible(not brush)
        self.paint_btn.setVisible(brush)
        self.brush_note.setVisible(brush)
        # Shared rows go where they mean something in this way.
        if brush:
            self.brush_layout.insertWidget(2, self.terrain_row)
            self.var_layout.insertWidget(3, self.distance_row)
            self.var_card.findChild(QLabel, "step").setText("3")
        else:
            self.where_layout.insertWidget(3, self.terrain_row)
            self.count_layout.insertWidget(3, self.distance_row)
            self.var_card.findChild(QLabel, "step").setText("4")
            if self.paint_btn.isChecked():
                self.paint_btn.setChecked(False)
        self._show_mode()

    # ---- objects --------------------------------------------------------------

    def fill_objects(self, chosen=None) -> None:
        """The model's components first, then IngeTrazo's starters. ``chosen``
        (a list of sources) ticks those and sets their share."""
        explicit = chosen is not None
        if chosen is None:
            chosen = self.sources() if self.tiles else []
        rows = []
        for g in motor.model_components(self.app.scene):
            rows.append(({"kind": "model", "name": g.name}, None, tr("In the model")))
        for e in motor.bundled_entries():
            rows.append(({"kind": "bundled", "key": e["key"],
                          "name": _core_tr(e["name"])}, e["thumb"],
                         _core_tr(e.get("tip", e["name"]))))
        # A source of the scatter being edited whose object left the model
        # (its copies still carry it) stays on the list.
        for s in chosen:
            if not any(motor._same_source(s, r[0]) for r in rows):
                rows.insert(0, ({k: s[k] for k in s if k != "weight"}, None,
                                tr("In the model")))
        sig = [(r[0].get("kind"), r[0].get("key"), r[0].get("name")) for r in rows]
        if sig == getattr(self, "_rows_sig", None) and not explicit:
            return                       # the same list: keep ticks as they are
        if sig == getattr(self, "_rows_sig", None):
            for t in self.tiles:         # same tiles: only the choice changes
                pick = next((c for c in chosen if motor._same_source(c, t.src)), None)
                t.set_checked(pick is not None)
                t.set_weight(int(pick.get("weight", 1)) if pick else 1)
            return
        self._rows_sig = sig
        for t in self.tiles:
            self.grid.removeWidget(t)
            t.deleteLater()
        self.tiles = []
        for i, (src, thumb, tip) in enumerate(rows):
            t = ObjectTile(src, thumb, tip)
            pick = next((c for c in chosen if motor._same_source(c, src)), None)
            t.set_checked(pick is not None)
            t.set_weight(int(pick.get("weight", 1)) if pick else 1)
            t.changed.connect(self._show_mode)
            self.grid.addWidget(t, i // 3, i % 3)
            self.tiles.append(t)

    def sources(self) -> list:
        out = []
        for t in self.tiles:
            if t.checked:
                s = dict(t.src)
                s["weight"] = t.weight
                out.append(s)
        return out

    def check(self, kind: str, key_or_name: str, weight: int = 1) -> None:
        """Tick one object (tests and the console)."""
        for t in self.tiles:
            src = t.src
            if src["kind"] == kind and (src.get("key") == key_or_name
                                        or src.get("name") == key_or_name):
                t.set_checked(True)
                t.set_weight(weight)
                return
        raise KeyError(key_or_name)

    # ---- parameters -----------------------------------------------------------

    def _mode_changed(self, _i=None) -> None:
        # Each way of counting keeps its own number.
        new = self.mode.currentData()
        before = getattr(self, "_amount_mode", None)
        store = self.__dict__.setdefault("_other_amount", {})
        if before is not None and before != new:
            store[before] = self.amount.value()
        self._amount_mode = new
        self._apply_range(new)
        if before is not None and before != new and new in store:
            self.amount.setValue(store[new])

    def _apply_range(self, mode) -> None:
        if mode == "density":
            self.amount.setRange(0.01, 1000.0)
            self.amount.setDecimals(2)
            self.amount.setSingleStep(0.5)
        else:
            self.amount.setRange(1, 20000)
            self.amount.setDecimals(0)
            self.amount.setSingleStep(10)

    def set_params(self, p) -> None:
        p = {**motor.DEFAULTS, **p}
        self._other_amount = {"count": p["count"], "density": p["density"]}
        self.mode.blockSignals(True)
        self.mode.setCurrentIndex(max(0, self.mode.findData(p["mode"])))
        self.mode.blockSignals(False)
        self._amount_mode = p["mode"]
        self._apply_range(p["mode"])
        self.amount.setValue(p["density"] if p["mode"] == "density" else p["count"])
        self.distance.setValue(p["min_distance"])
        self.smin.setValue(int(p["scale"][0]))
        self.smax.setValue(int(p["scale"][1]))
        self.rotation.setValue(p["rotation"])
        self.align.setChecked(bool(p["align"]))
        self.terrain.setChecked(bool(p["terrain"]))
        self.max_slope.setValue(p["max_slope"])
        self.seed.setValue(int(p["seed"]))
        self.brush.setValue(float(p["brush"]))
        self.brush_density.setValue(float(p["brush_density"]))

    def params(self) -> dict:
        mode = self.mode.currentData()
        p = {"mode": mode,
             "count": int(self.amount.value()) if mode == "count"
             else int(self._other_amount.get("count", motor.DEFAULTS["count"])),
             "density": float(self.amount.value()) if mode == "density"
             else float(self._other_amount.get("density", motor.DEFAULTS["density"])),
             "min_distance": self.distance.value(),
             "scale": [float(self.smin.value()), float(self.smax.value())],
             "rotation": self.rotation.value(),
             "align": self.align.isChecked(),
             "terrain": self.terrain.isChecked(),
             "max_slope": self.max_slope.value(),
             "seed": self.seed.value(),
             "brush": self.brush.value(),
             "brush_density": self.brush_density.value(),
             "sources": self.sources()}
        return p

    def _new_seed(self) -> None:
        self.seed.setValue(random.randint(1, 999999))

    # ---- selection ------------------------------------------------------------

    def _tick(self) -> None:
        if self.isVisible():
            self._refresh_selection()

    def _document_changed(self) -> None:
        if self._editing is not None and self._editing not in self.app.scene.groups:
            self._editing = None
        if self._last is not None and self._last not in self.app.scene.groups:
            self._last = None
        if not self.isVisible():
            # IngeTrazo calls this on every edit and selection. Measuring the
            # selection is the slow part, and nobody is looking at the
            # numbers: do it when the tab comes to the front.
            self._stale = True
            return
        self._stale = False
        self.fill_objects()
        self._refresh_selection()

    def showEvent(self, ev) -> None:  # noqa: N802
        super().showEvent(ev)
        if self._stale and hasattr(self, "go"):
            self._stale = False
            self.fill_objects()
            self._refresh_selection()

    def _refresh_selection(self, force=False) -> None:
        sel = list(self.app.scene.selection)
        # The model's version too: the same group edited is a new surface.
        key = (len(sel), tuple(sorted(id(e) for e in sel[:200])),
               getattr(self.app.scene, "content_version", None))
        if key == self._sel_key and not force:
            return
        self._sel_key = key
        scatters = [g for g in sel if motor.is_scatter(g)]
        if len(sel) == 1 and scatters:
            self._pending = None
            self.edit(scatters[0])
            return
        faces = motor.selection_face_count(sel)
        if faces > motor.BIG_SELECTION:
            # Too many faces to triangulate at every click: say so, and
            # measure when the button is pressed (see run()).
            self._tris = []
            self._pending = sel
            self._editing = None
            self.where_big.setText("…")
            self.where.setText(tr("Selection: {n} faces. The surface is "
                                  "measured when you scatter.", n=f"{faces:,}"))
            self._show_mode()
            return
        self._pending = None
        self._tris = motor.surface_from_selection(sel, self.max_slope.value())
        if self._tris:
            self._editing = None
            self.where_big.setText(f"{motor.surface_area(self._tris):.0f} m²")
            self.where.setText(tr("Selection: {a} m² ({n} triangles)",
                                  n=len(self._tris),
                                  a=f"{motor.surface_area(self._tris):.1f}"))
        elif not sel and self._editing in self.app.scene.groups:
            self.edit(self._editing)     # painted: still editing it
            return
        else:
            self.where_big.setText("—")
            self.where.setText(tr("Select faces or a group in the model."))
        self._show_mode()

    def edit(self, group) -> None:
        """Bring a scatter's numbers into the panel, to change them."""
        e = group.ext[motor.KEY]
        if self._editing is not group:
            self.set_params(e)
            self.fill_objects(e.get("sources", []))
            if not e["surface"] and self.way_name() != "brush":
                self.set_way("brush")    # painted by hand: open the brush
        self._editing = group
        self._last = group
        self._tris = []
        self.where_big.setText(f"{motor.surface_area(e['surface']):.0f} m²"
                               if e["surface"] else "—")
        if e["surface"]:
            text = tr("The scatter's surface: {a} m² ({n} triangles)",
                      n=len(e["surface"]),
                      a=f"{motor.surface_area(e['surface']):.1f}")
        else:
            text = tr("Painted by hand.")
        strokes = len(e.get("strokes") or [])
        if strokes:
            text += " " + tr("Brush strokes: {n}.", n=strokes)
        self.where.setText(text)
        self._show_mode()

    def _show_mode(self) -> None:
        if not hasattr(self, "go"):
            return                       # still being built
        brush = self.way_name() == "brush"
        if self._editing is not None:
            text = "<b>" + tr("Editing: {name}", name=self._editing.name) + "</b>"
            if not brush:
                text += "<br>" + tr("Change the numbers and scatter again on the "
                                    "same surface; or select faces to start a new one.")
            self.editing.setText(text)
            self.go.setText(tr("Scatter again"))
            self.go.setEnabled(not self._busy)
            self.brush_note.setText(tr("The brush adds to “{name}”.",
                                       name=self._editing.name))
        else:
            self.editing.setText("")
            self.go.setText(tr("Scatter on the selection"))
            self.go.setEnabled(bool(self._tris or self._pending)
                               and not self._busy)
            self.brush_note.setText(tr("The brush starts a new scatter."))
        target = self._zone_target()
        if target is None:
            self.zones.setText("")
            tip = tr("Make or select a scatter first.")
            self.clear_btn.setEnabled(False)
            self.free_btn.setEnabled(False)
        else:
            n = len(target.ext[motor.KEY].get("clear") or [])
            self.zones.setText(tr("{n} zones", n=n))
            tip = tr("In “{name}”: {n} zones kept clear.", name=target.name, n=n)
            sel = [g for g in self.app.scene.selection if not motor.is_scatter(g)]
            self.clear_btn.setEnabled(bool(sel) and not self._busy)
            self.free_btn.setEnabled(n > 0 and not self._busy)
        self.zones.setToolTip(tip)
        self.clear_btn.setToolTip(tr("Keep the selection clear") + "\n" + tip)

    # ---- the button -----------------------------------------------------------

    def run(self) -> None:
        params = self.params()
        if not params["sources"]:
            self.status.setText(tr("Choose at least one object to scatter."))
            return
        old = self._editing
        if old is None and self._pending is not None:
            # A big selection: its surface is measured now, once.
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QApplication
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                self._tris = motor.surface_from_selection(
                    self._pending, self.max_slope.value())
            finally:
                QApplication.restoreOverrideCursor()
            if not self._tris:
                self.status.setText(tr("The selection has no faces facing up."))
                return
        tris = None if old is not None else list(self._tris)
        self._apply(old, lambda scene, terrain: motor.prepare(
            scene, params, tris=tris, old=old, terrain=terrain))

    def _apply(self, old, make, select=True) -> bool:
        """Build with ``make(scene, terrain)`` and put the result in place
        of ``old`` (or beside the rest), as one undo step."""
        from core.history import SnapshotImport
        vp = self.app.viewport
        scene = self.app.scene
        terrain = getattr(scene, "terrain", None)
        end = getattr(vp, "end_group_edit", None)
        if callable(end) and getattr(scene, "edit_group", None) is not None:
            end()
        # Reading the objects, building the copies and IngeTrazo's own
        # first drawing of them can take seconds: say so, and wait visibly.
        from PySide6.QtWidgets import QApplication
        self.status.setText(tr("Scattering…"))
        self._busy = True
        self.go.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        try:
            try:
                box, placed, wanted = make(scene, terrain)
            except ValueError as exc:
                self.status.setText(str(exc))
                return False
            vp.history.execute(SnapshotImport(lambda s: motor.place(s, box, old)))
            if box not in scene.groups:  # IngeTrazo logged why; nothing changed
                self.status.setText(getattr(vp.history, "last_error", None) or "")
                return False
            self._finish(vp, scene, box, placed, wanted, select)
            return True
        finally:
            # After the next paint: the timer cannot fire while IngeTrazo is
            # still busy drawing the new copies for the first time.
            QTimer.singleShot(200, self._idle)

    # ---- the brush --------------------------------------------------------------

    def _paint_toggled(self, on: bool) -> None:
        vp = self.app.viewport
        if on:
            if self._tool is None:
                from .brush import BrushTool
                self._tool = BrushTool(self)
            if vp.active_tool is not self._tool:
                vp.set_active_tool(self._tool)
        elif self._tool is not None and vp.active_tool is self._tool:
            self.stop_brush()

    def stop_brush(self) -> None:
        win = self.app.window
        go = getattr(win, "_activate_tool", None)
        try:
            go("select")
        except Exception:                # noqa: BLE001
            self.app.viewport.set_active_tool(None)

    def brush_on(self, on: bool) -> None:
        """The tool says it came or went (another tool may have been picked)."""
        self.paint_btn.blockSignals(True)
        self.paint_btn.setChecked(on)
        self.paint_btn.blockSignals(False)

    def draw_brush(self, viewport, painter) -> None:
        if self._tool is not None and viewport.active_tool is self._tool:
            self._tool.draw(self.app, painter)

    def say(self, text: str) -> None:
        self.status.setText(text)

    def paint(self, stroke) -> bool:
        """One brush stroke into the scatter being edited, or a new one."""
        old = self._editing
        if old is not None and old not in self.app.scene.groups:
            old = None
        if old is None and stroke.get("erase"):
            self.status.setText(tr("Select a scatter to take copies away from it."))
            return False
        here = self.params()
        if not stroke.get("erase"):
            if not here["sources"]:
                self.status.setText(tr("Choose at least one object to scatter."))
                return False
            stroke = {**stroke, "sources": here["sources"],
                      "density": here["brush_density"], "scale": here["scale"],
                      "rotation": here["rotation"], "align": here["align"]}
        if old is not None:
            e = old.ext[motor.KEY]
            params = {k: e[k] for k in motor.DEFAULTS if k in e}
            params["sources"] = e.get("sources") or []
            params.update(brush=here["brush"], brush_density=here["brush_density"])
            strokes = list(e.get("strokes") or []) + [stroke]
            return self._apply(old, lambda scene, terrain: motor.prepare(
                scene, params, old=old, terrain=terrain, strokes=strokes),
                select=False)
        return self._apply(None, lambda scene, terrain: motor.prepare(
            scene, here, tris=[], terrain=terrain, strokes=[stroke], clear=[]),
            select=False)

    # ---- zones kept clear ---------------------------------------------------------

    def _zone_target(self):
        for g in (self._editing, self._last):
            if g is not None and g in self.app.scene.groups:
                return g
        return None

    def _redo_with(self, target, clear) -> bool:
        e = target.ext[motor.KEY]
        params = {k: e[k] for k in motor.DEFAULTS if k in e}
        params["sources"] = e.get("sources") or []
        return self._apply(target, lambda scene, terrain: motor.prepare(
            scene, params, old=target, terrain=terrain, clear=clear),
            select=False)

    def keep_clear(self) -> bool:
        target = self._zone_target()
        if target is None:
            return False
        zone = motor.footprint(self.app.scene.selection)
        if not zone:
            self.status.setText(tr("The selection covers nothing seen from above."))
            return False
        clear = list(target.ext[motor.KEY].get("clear") or []) + [zone]
        return self._redo_with(target, clear)

    def free_zones(self) -> bool:
        target = self._zone_target()
        if target is None:
            return False
        return self._redo_with(target, [])

    def _idle(self) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.restoreOverrideCursor()
        self._busy = False
        self._show_mode()

    def _finish(self, vp, scene, box, placed, wanted, select=True) -> None:
        notify = getattr(vp, "notify_scene_changed", None)
        if callable(notify):
            notify()
        # The brush leaves the selection empty: selecting a big scatter makes
        # IngeTrazo 0.6 measure every copy for the Parts list, seconds per
        # stroke. The panel keeps editing it all the same.
        scene.selection.clear()
        if select:
            scene.selection.add(box)
        self._editing = box
        self._last = box
        self._sel_key = None
        e = box.ext[motor.KEY]
        by_hand = bool(e.get("strokes") or e.get("clear"))
        msg = (tr("{n} copies in the scatter.", n=placed) if by_hand else
               tr("{n} copies placed.", n=placed) if placed >= wanted else
               tr("{n} of {w} copies placed: there is no room for more at "
                  "that distance.", n=placed, w=wanted))
        self.status.setText(msg + " " + tr("Ctrl+Z undoes it at once."))
        self._refresh_selection(True)
