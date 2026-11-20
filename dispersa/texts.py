# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Victor Crespo (3dvic.com · github.com/vicc3d)
"""The extension's own words (IngeTrazo's catalogues stay IngeTrazo's).
English is the key; Spanish and Portuguese are the translations."""
from __future__ import annotations

_TEXTS = {
    "es": {
                        "Show the Dispersa tab: trees, plants, stones or people spread over faces or the terrain.":
            "Mostrar la pestaña Dispersa: árboles, plantas, piedras o personas repartidos sobre caras o el terreno.",
        "Spread copies of components over faces, a group or the terrain, with their size and turn at random.":
            "Reparte copias de componentes sobre caras, un grupo o el terreno, con tamaño y giro al azar.",
        "Objects": "Objetos",
        "Object": "Objeto",
        "Share": "Proporción",
        "How often this object comes out, against the others":
            "Cuántas veces sale este objeto frente a los demás",
        "In the model": "En el modelo",
        "IngeTrazo": "IngeTrazo",
        "Surface": "Superficie",
        "Select faces or a group in the model.":
            "Selecciona caras o un grupo en el modelo.",
        "Selection: {a} m² ({n} triangles)": "Selección: {a} m² ({n} triángulos)",
        "Selection: {n} faces. The surface is measured when you scatter.":
            "Selección: {n} caras. La superficie se mide al dispersar.",
        "The selection has no faces facing up.":
            "La selección no tiene caras mirando hacia arriba.",
        "The scatter's surface: {a} m² ({n} triangles)": "Superficie de la dispersión: {a} m² ({n} triángulos)",
        "On the terrain": "Sobre el terreno",
        "Drop every copy onto the 3D terrain of the Terrain tab, inside the selected area":
            "Bajar cada copia al terreno 3D de la pestaña Terreno, dentro del área seleccionada",
        "Steepest slope": "Pendiente máxima",
        "From a group, only the faces this close to level (its floors and roofs, not its walls)":
            "De un grupo, solo las caras con esta pendiente o menos (pisos y techos, no muros)",
        "Copies": "Copias",
        "Number of copies": "Número de copias",
        "Copies per 100 m²": "Copias por 100 m²",
        "Distance between copies": "Distancia entre copias",
        "The least distance from one copy to the next (0 = no limit)":
            "La distancia mínima entre una copia y la siguiente (0 = sin límite)",
        "Variation": "Variación",
        "Size from": "Tamaño de",
        "to": "a",
        "Turn up to": "Giro hasta",
        "Each copy turns at random, from 0 up to this angle":
            "Cada copia gira al azar, de 0 hasta este ángulo",
        "Lean with the surface": "Inclinar con la superficie",
        "Copies follow the slope (stones, grass) instead of standing upright (trees, people)":
            "Las copias siguen la pendiente (piedras, pasto) en vez de quedar de pie (árboles, personas)",
        "Seed": "Semilla",
        "The same seed gives the same scatter":
            "La misma semilla da la misma dispersión",
        "New": "Nueva",
        "Another random arrangement": "Otra disposición al azar",
        "Scatter on the selection": "Repartir sobre la selección",
        "Scatter again": "Volver a repartir",
        "Editing: {name}": "Editando: {name}",
        "Change the numbers and scatter again on the same surface; or select faces to start a new one.":
            "Cambia los valores y vuelve a dispersar sobre la misma superficie; o selecciona caras para empezar otra.",
        "Scattering…": "Dispersando…",
        "{n} copies placed.": "{n} copias puestas.",
        "{n} of {w} copies placed: there is no room for more at that distance.":
            "{n} de {w} copias puestas: no caben más a esa distancia.",
        "Ctrl+Z undoes it at once.": "Ctrl+Z lo deshace de una vez.",
        "Choose at least one object to scatter.":
            "Elige al menos un objeto para dispersar.",
        "Select faces or a group to scatter on.":
            "Selecciona caras o un grupo sobre el que dispersar.",
        "The selection has no surface to scatter on.":
            "La selección no tiene superficie sobre la que dispersar.",
        "There is no 3D terrain yet: build it in the Terrain tab, or untick “On the terrain”.":
            "Todavía no hay terreno 3D: créalo en la pestaña Terreno, o desmarca «Sobre el terreno».",
        "“{name}” is no longer in the model.": "«{name}» ya no está en el modelo.",
        "Could not read {name}.": "No se pudo leer {name}.",
                "Edit in Dispersa…": "Editar en Dispersa…",
        "Seed {s}": "Semilla {s}",
        "Scatter":
            "Repartir",
        "Spread copies over the selected faces, a group or the terrain":
            "Reparte copias sobre las caras seleccionadas, un grupo o el terreno",
        "Paint copies by hand where you drag":
            "Pinta copias a mano donde arrastras",
        "Spacing":
            "Separación",
        "Where":
            "Dónde",
        "Steepest":
            "Pendiente máx.",
        "How many":
            "Cuántas",
        "copies":
            "copias",
        "per 100 m²":
            "por 100 m²",
        "Size":
            "Tamaño",
        "How thick the brush paints, with the objects and the variation":
            "Cuán denso pinta el pincel, con los objetos y la variación",
        "Drag: paint · <b>Shift</b>: take away · <b>[ ]</b>: size · <b>Esc</b>: stop":
            "Arrastra: pinta · <b>Mayús</b>: quita · <b>[ ]</b>: tamaño · <b>Esc</b>: termina",
        "Nothing goes inside what you select, seen from above: a path, a house, a pond.":
            "Nada cae dentro de lo que selecciones, visto desde arriba: un camino, una casa, un estanque.",
        "Keep this clear":
            "Dejar libre",
        "Free all":
            "Quitar todas",
        "{n} zones":
            "{n} zonas",
        "Nothing to paint on there: the faces under the brush are too steep.":
            "No hay dónde pintar ahí: las caras bajo el pincel son demasiado empinadas.",
        "Brush":
            "Pincel",
        "Paint":
            "Pintar",
        "Drag over faces (or the terrain, with “On the terrain”) to add copies; Shift+drag takes them away. [ and ] change the size.":
            "Arrastra sobre caras (o el terreno, con «Sobre el terreno») para añadir copias; Mayús+arrastrar las quita. [ y ] cambian el tamaño.",
        "The brush's radius":
            "El radio del pincel",
        "Brush size":
            "Tamaño del pincel",
        "How thick the brush paints, with the objects and the variation above":
            "Cuán denso pinta el pincel, con los objetos y la variación de arriba",
        "Keep clear":
            "Zonas libres",
        "Nothing goes inside what you select here, seen from above: a path, a house, a pond.":
            "Nada cae dentro de lo que selecciones aquí, visto desde arriba: un camino, una casa, un estanque.",
        "Keep the selection clear":
            "Dejar libre la selección",
        "Free all zones":
            "Quitar todas las zonas",
        "Painted by hand.":
            "Pintada a mano.",
        "Brush strokes: {n}.":
            "Trazos de pincel: {n}.",
        "The brush adds to “{name}”.":
            "El pincel añade a «{name}».",
        "The brush starts a new scatter.":
            "El pincel empieza una dispersión nueva.",
        "Make or select a scatter first.":
            "Primero haz o selecciona una dispersión.",
        "In “{name}”: {n} zones kept clear.":
            "En «{name}»: {n} zonas libres.",
        "Select a scatter to take copies away from it.":
            "Selecciona una dispersión para quitarle copias.",
        "The selection covers nothing seen from above.":
            "La selección no cubre nada visto desde arriba.",
        "{n} copies in the scatter.":
            "{n} copias en la dispersión.",
        "Drag to paint copies, Shift+drag to take them away. [ and ] change the size; Esc stops.":
            "Arrastra para pintar copias, Mayús+arrastrar para quitarlas. [ y ] cambian el tamaño; Esc termina.",
    },
    "pt": {
                        "Show the Dispersa tab: trees, plants, stones or people spread over faces or the terrain.":
            "Mostrar a aba Dispersa: árvores, plantas, pedras ou pessoas espalhadas sobre faces ou o terreno.",
        "Spread copies of components over faces, a group or the terrain, with their size and turn at random.":
            "Espalha cópias de componentes sobre faces, um grupo ou o terreno, com tamanho e giro aleatórios.",
        "Objects": "Objetos",
        "Object": "Objeto",
        "Share": "Proporção",
        "How often this object comes out, against the others":
            "Com que frequência este objeto aparece, em relação aos outros",
        "In the model": "No modelo",
        "IngeTrazo": "IngeTrazo",
        "Surface": "Superfície",
        "Select faces or a group in the model.":
            "Selecione faces ou um grupo no modelo.",
        "Selection: {a} m² ({n} triangles)": "Seleção: {a} m² ({n} triângulos)",
        "Selection: {n} faces. The surface is measured when you scatter.":
            "Seleção: {n} faces. A superfície é medida ao dispersar.",
        "The selection has no faces facing up.":
            "A seleção não tem faces voltadas para cima.",
        "The scatter's surface: {a} m² ({n} triangles)": "Superfície da dispersão: {a} m² ({n} triângulos)",
        "On the terrain": "Sobre o terreno",
        "Drop every copy onto the 3D terrain of the Terrain tab, inside the selected area":
            "Baixar cada cópia ao terreno 3D da aba Terreno, dentro da área selecionada",
        "Steepest slope": "Inclinação máxima",
        "From a group, only the faces this close to level (its floors and roofs, not its walls)":
            "De um grupo, só as faces com esta inclinação ou menos (pisos e telhados, não paredes)",
        "Copies": "Cópias",
        "Number of copies": "Número de cópias",
        "Copies per 100 m²": "Cópias por 100 m²",
        "Distance between copies": "Distância entre cópias",
        "The least distance from one copy to the next (0 = no limit)":
            "A distância mínima entre uma cópia e a seguinte (0 = sem limite)",
        "Variation": "Variação",
        "Size from": "Tamanho de",
        "to": "a",
        "Turn up to": "Giro até",
        "Each copy turns at random, from 0 up to this angle":
            "Cada cópia gira ao acaso, de 0 até este ângulo",
        "Lean with the surface": "Inclinar com a superfície",
        "Copies follow the slope (stones, grass) instead of standing upright (trees, people)":
            "As cópias seguem a inclinação (pedras, grama) em vez de ficarem de pé (árvores, pessoas)",
        "Seed": "Semente",
        "The same seed gives the same scatter":
            "A mesma semente dá a mesma dispersão",
        "New": "Nova",
        "Another random arrangement": "Outra disposição aleatória",
        "Scatter on the selection": "Espalhar sobre a seleção",
        "Scatter again": "Espalhar de novo",
        "Editing: {name}": "Editando: {name}",
        "Change the numbers and scatter again on the same surface; or select faces to start a new one.":
            "Mude os valores e espalhe de novo sobre a mesma superfície; ou selecione faces para começar outra.",
        "Scattering…": "Espalhando…",
        "{n} copies placed.": "{n} cópias colocadas.",
        "{n} of {w} copies placed: there is no room for more at that distance.":
            "{n} de {w} cópias colocadas: não cabem mais a essa distância.",
        "Ctrl+Z undoes it at once.": "Ctrl+Z desfaz tudo de uma vez.",
        "Choose at least one object to scatter.":
            "Escolha pelo menos um objeto para espalhar.",
        "Select faces or a group to scatter on.":
            "Selecione faces ou um grupo sobre o qual espalhar.",
        "The selection has no surface to scatter on.":
            "A seleção não tem superfície sobre a qual espalhar.",
        "There is no 3D terrain yet: build it in the Terrain tab, or untick “On the terrain”.":
            "Ainda não há terreno 3D: crie-o na aba Terreno, ou desmarque «Sobre o terreno».",
        "“{name}” is no longer in the model.": "«{name}» já não está no modelo.",
        "Could not read {name}.": "Não foi possível ler {name}.",
                "Edit in Dispersa…": "Editar em Dispersa…",
        "Seed {s}": "Semente {s}",
        "Scatter":
            "Espalhar",
        "Spread copies over the selected faces, a group or the terrain":
            "Espalha cópias sobre as faces selecionadas, um grupo ou o terreno",
        "Paint copies by hand where you drag":
            "Pinta cópias à mão onde você arrasta",
        "Spacing":
            "Espaçamento",
        "Where":
            "Onde",
        "Steepest":
            "Inclinação máx.",
        "How many":
            "Quantas",
        "copies":
            "cópias",
        "per 100 m²":
            "por 100 m²",
        "Size":
            "Tamanho",
        "How thick the brush paints, with the objects and the variation":
            "Quão denso o pincel pinta, com os objetos e a variação",
        "Drag: paint · <b>Shift</b>: take away · <b>[ ]</b>: size · <b>Esc</b>: stop":
            "Arraste: pinta · <b>Shift</b>: remove · <b>[ ]</b>: tamanho · <b>Esc</b>: termina",
        "Nothing goes inside what you select, seen from above: a path, a house, a pond.":
            "Nada cai dentro do que você selecionar, visto de cima: um caminho, uma casa, um lago.",
        "Keep this clear":
            "Deixar livre",
        "Free all":
            "Remover todas",
        "{n} zones":
            "{n} zonas",
        "Nothing to paint on there: the faces under the brush are too steep.":
            "Não há onde pintar ali: as faces sob o pincel são íngremes demais.",
        "Brush":
            "Pincel",
        "Paint":
            "Pintar",
        "Drag over faces (or the terrain, with “On the terrain”) to add copies; Shift+drag takes them away. [ and ] change the size.":
            "Arraste sobre faces (ou o terreno, com «Sobre o terreno») para adicionar cópias; Shift+arrastar as remove. [ e ] mudam o tamanho.",
        "The brush's radius":
            "O raio do pincel",
        "Brush size":
            "Tamanho do pincel",
        "How thick the brush paints, with the objects and the variation above":
            "Quão denso o pincel pinta, com os objetos e a variação acima",
        "Keep clear":
            "Zonas livres",
        "Nothing goes inside what you select here, seen from above: a path, a house, a pond.":
            "Nada cai dentro do que você selecionar aqui, visto de cima: um caminho, uma casa, um lago.",
        "Keep the selection clear":
            "Deixar a seleção livre",
        "Free all zones":
            "Remover todas as zonas",
        "Painted by hand.":
            "Pintada à mão.",
        "Brush strokes: {n}.":
            "Traços de pincel: {n}.",
        "The brush adds to “{name}”.":
            "O pincel adiciona a «{name}».",
        "The brush starts a new scatter.":
            "O pincel começa uma nova dispersão.",
        "Make or select a scatter first.":
            "Primeiro faça ou selecione uma dispersão.",
        "In “{name}”: {n} zones kept clear.":
            "Em «{name}»: {n} zonas livres.",
        "Select a scatter to take copies away from it.":
            "Selecione uma dispersão para remover cópias dela.",
        "The selection covers nothing seen from above.":
            "A seleção não cobre nada vista de cima.",
        "{n} copies in the scatter.":
            "{n} cópias na dispersão.",
        "Drag to paint copies, Shift+drag to take them away. [ and ] change the size; Esc stops.":
            "Arraste para pintar cópias, Shift+arrastar para removê-las. [ e ] mudam o tamanho; Esc termina.",
    },
}

LANGUAGE = None


def tr(text: str, **kw) -> str:
    try:
        lang = LANGUAGE() if LANGUAGE is not None else "en"
    except Exception:                    # noqa: BLE001 (an older IngeTrazo)
        lang = "en"
    out = _TEXTS.get(lang, {}).get(text, text)
    return out.format(**kw) if kw else out
