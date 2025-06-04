
Eres analista senior en quick-commerce. Generá un informe EXACTAMENTE en este formato Markdown:

## 📌 Finance Insights
<!--CHART:LINE_AFV-->
- **AFV país:** ${overall.afv_act}
- **ΔAFV total:** **${overall.delta_afv} ({overall.delta_afv_pct}%)**
- **Efectos:**
    - Basket Size: ${overall.efecto_bs}
    - AIV: ${overall.efecto_aiv}
    - Mix: ${overall.efecto_mix}

- **Análisis:** 
    Indica claramente qué verticales aportaron más y cómo interactuaron los efectos de share y AFV interno.

    <!--CHART:BAR_VERTICALS-->

- **Cocinas clave:** 
    Resume en 2-3 frases qué cocinas explican la caída o suba de AFV usando `cocinasdown` y `cocinasup` (nombres, ΔShare, AFV). No utilices cursivas ni negritas en esta frase.
    
    <!--CHART:SCATTER_COCINAS-->

- **Análisis de Usuarios:** 
    Explica {incomesummary}

    <!--CHART:BAR_INCOME-->

---

## 📌 Análisis Detallado por Vertical
{#each verticals}
    ### 🏷️ {name}

    | Métrica | Valor |
    |---------|-------|
    | **AFV actual** | ${afv_act} |
    | **ΔAFV** | ${delta_afv} ({delta_afv_pct} %) |
    | **Impacto país** | Share: ${contrib_share} · AFV interno: ${contrib_afv} · **Neto: ${impacto_neto}** |
    | **Efectos** | BS: ${efecto_bs} · AIV: ${efecto_aiv} · Mix: ${efecto_mix} |
    | **Incentivo p/orden** | ${incent_act_pp} (Δ {delta_incent}) |

    **Análisis:** Resume en una frase por qué sube o baja usando los datos de la tabla (máx. 35 palabras).

    <!--CHART:WF_{name}-->

{/each}

---

## 📌 Segmentos con mayor cambio de share (≥ ±0,3 p.p.)

### 🔼 Suben
| Vertical | Segmento | ΔShare | Contribución ($) | Comentario |
|----------|----------|--------|------------------|------------|
{#each segments_up}
| {vertical} | {name} | {delta_share} | {contrib} | {comment} |
{/each}

### 🔽 Bajan
| Vertical | Segmento | ΔShare | Contribución ($) | Comentario |
|----------|----------|--------|------------------|------------|
{#each segments_down}
| {vertical} | {name} | {delta_share} | {contrib} | {comment} |
{/each}

---

## 📌 Cocinas con mayor cambio de share (≥ ±0,3 p.p.)

### 🔼 Suben
| Vertical | Cocina | ΔShare | AFV ($) |
|----------|--------|--------|---------|
{#each cocinas_up}
| {vertical} | {name} | {delta_share} | {afv} |
{/each}

### 🔽 Bajan
| Vertical | Cocina | ΔShare | AFV ($) |
|----------|--------|--------|---------|
{#each cocinas_down}
| {vertical} | {name} | {delta_share} | {afv} |
{/each}

---

Usá el siguiente JSON para completar estrictamente los campos:

```json
{
  "overall": {
    "afv_act": "734.23",
    "delta_afv": "-8.72",
    "delta_afv_pct": "-1.17",
    "contrib_share_overall": "0.00",
    "contrib_afv_intra": "0.00",
    "efecto_bs": "-13.03",
    "efecto_aiv": "4.31",
    "efecto_mix": "-0.00",
    "delta_bs": "-0.05",
    "delta_bs_pct": "-1.75"
  },
  "verticals": [
    {
      "name": "D-Mart",
      "afv_act": "1021.55",
      "driver": "SHARE",
      "delta_afv": 5.99,
      "delta_afv_pct": 0.59,
      "delta_share_pp": -0.9,
      "contrib_share": -9.14,
      "contrib_afv": 0.91,
      "impacto_neto": -8.23,
      "efecto_bs": 6.11,
      "efecto_aiv": -0.12,
      "efecto_mix": 0.0,
      "incent_act_pp": "11.02",
      "delta_incent": -1.61
    },
    {
      "name": "Food",
      "afv_act": "735.06",
      "driver": "AFV",
      "delta_afv": -7.8,
      "delta_afv_pct": -1.05,
      "delta_share_pp": 0.42,
      "contrib_share": 3.12,
      "contrib_afv": -5.42,
      "impacto_neto": -2.3,
      "efecto_bs": -8.22,
      "efecto_aiv": 0.42,
      "efecto_mix": -0.0,
      "incent_act_pp": "4.93",
      "delta_incent": -0.77
    },
    {
      "name": "Local Stores",
      "afv_act": "773.27",
      "driver": "SHARE",
      "delta_afv": 3.75,
      "delta_afv_pct": 0.49,
      "delta_share_pp": -0.13,
      "contrib_share": -0.98,
      "contrib_afv": 0.15,
      "impacto_neto": -0.83,
      "efecto_bs": 5.53,
      "efecto_aiv": -1.78,
      "efecto_mix": 0.0,
      "incent_act_pp": "0.52",
      "delta_incent": -0.11
    },
    {
      "name": "Local Stores (Market)",
      "afv_act": "755.92",
      "driver": "SHARE",
      "delta_afv": -3.9,
      "delta_afv_pct": -0.51,
      "delta_share_pp": 0.37,
      "contrib_share": 2.85,
      "contrib_afv": -0.19,
      "impacto_neto": 2.66,
      "efecto_bs": -12.75,
      "efecto_aiv": 8.85,
      "efecto_mix": 0.0,
      "incent_act_pp": "6.01",
      "delta_incent": -2.3
    }
  ],
  "segments": [
    {
      "vertical": "Food",
      "name": "Local Hero",
      "delta_share_pp": 5.81,
      "delta_afv": 3.43,
      "contrib_share": 43.6,
      "contrib_afv": 0.84
    },
    {
      "vertical": "Food",
      "name": "Long Tail",
      "delta_share_pp": -5.22,
      "delta_afv": -23.76,
      "contrib_share": -40.84,
      "contrib_afv": -6.78
    },
    {
      "vertical": "Local Stores (Market)",
      "name": "AAA",
      "delta_share_pp": 0.75,
      "delta_afv": -43.68,
      "contrib_share": 10.98,
      "contrib_afv": -5.18
    },
    {
      "vertical": "Local Stores (Market)",
      "name": "Not AAA",
      "delta_share_pp": -0.75,
      "delta_afv": -5.32,
      "contrib_share": -5.01,
      "contrib_afv": -4.69
    },
    {
      "vertical": "Food",
      "name": "Global KA",
      "delta_share_pp": -0.61,
      "delta_afv": -6.85,
      "contrib_share": -3.93,
      "contrib_afv": -1.63
    },
    {
      "vertical": "Food",
      "name": "Food N/D",
      "delta_share_pp": 0.33,
      "delta_afv": 26.97,
      "contrib_share": 2.44,
      "contrib_afv": 0.23
    },
    {
      "vertical": "Food",
      "name": "National KA",
      "delta_share_pp": -0.29,
      "delta_afv": 2.05,
      "contrib_share": -2.4,
      "contrib_afv": 0.31
    },
    {
      "vertical": "Food",
      "name": "Large Chain",
      "delta_share_pp": -0.01,
      "delta_afv": 5.68,
      "contrib_share": -0.04,
      "contrib_afv": 0.41
    },
    {
      "vertical": "Courier",
      "name": "Courier",
      "delta_share_pp": 0.0,
      "delta_afv": 0.0,
      "contrib_share": -0.0,
      "contrib_afv": 0.0
    },
    {
      "vertical": "D-Mart",
      "name": "D-Mart",
      "delta_share_pp": 0.0,
      "delta_afv": 5.99,
      "contrib_share": 0.0,
      "contrib_afv": 5.99
    },
    {
      "vertical": "Local Stores",
      "name": "Not AAA",
      "delta_share_pp": 0.0,
      "delta_afv": 3.75,
      "contrib_share": 0.0,
      "contrib_afv": 3.75
    }
  ],
  "cocinas": [
    {
      "vertical": "Food",
      "name": "Pizzas",
      "delta_share_pp": -0.92,
      "delta_afv": -11.2,
      "contrib_share": -7.23,
      "contrib_afv": -1.93
    },
    {
      "vertical": "Food",
      "name": "Hamburguesas",
      "delta_share_pp": -0.62,
      "delta_afv": 2.12,
      "contrib_share": -4.53,
      "contrib_afv": 0.49
    },
    {
      "vertical": "Food",
      "name": "Milanesas",
      "delta_share_pp": -0.33,
      "delta_afv": 2.63,
      "contrib_share": -2.51,
      "contrib_afv": 0.21
    },
    {
      "vertical": "Food",
      "name": "Cafetería",
      "delta_share_pp": 0.38,
      "delta_afv": -14.51,
      "contrib_share": 2.25,
      "contrib_afv": -0.8
    },
    {
      "vertical": "Food",
      "name": "Helados",
      "delta_share_pp": 0.35,
      "delta_afv": -7.11,
      "contrib_share": 2.19,
      "contrib_afv": -0.66
    },
    {
      "vertical": "Food",
      "name": "Postres",
      "delta_share_pp": 0.3,
      "delta_afv": -40.63,
      "contrib_share": 1.98,
      "contrib_afv": -0.95
    },
    {
      "vertical": "Food",
      "name": "Sushi",
      "delta_share_pp": -0.12,
      "delta_afv": -24.99,
      "contrib_share": -1.6,
      "contrib_afv": -0.79
    },
    {
      "vertical": "Food",
      "name": "Poke",
      "delta_share_pp": 0.2,
      "delta_afv": 1.73,
      "contrib_share": 1.49,
      "contrib_afv": 0.05
    },
    {
      "vertical": "Food",
      "name": "Pastas",
      "delta_share_pp": 0.21,
      "delta_afv": -14.09,
      "contrib_share": 1.43,
      "contrib_afv": -0.3
    },
    {
      "vertical": "Food",
      "name": "UNKNOWN",
      "delta_share_pp": -0.17,
      "delta_afv": -81.95,
      "contrib_share": -1.36,
      "contrib_afv": -0.69
    },
    {
      "vertical": "Food",
      "name": "Comida Armenia",
      "delta_share_pp": 0.16,
      "delta_afv": -1.18,
      "contrib_share": 1.3,
      "contrib_afv": -0.02
    },
    {
      "vertical": "Food",
      "name": "Carnes",
      "delta_share_pp": 0.09,
      "delta_afv": -11.71,
      "contrib_share": 1.1,
      "contrib_afv": -0.15
    },
    {
      "vertical": "Food",
      "name": "Tartas",
      "delta_share_pp": 0.22,
      "delta_afv": 41.94,
      "contrib_share": 1.1,
      "contrib_afv": 0.37
    },
    {
      "vertical": "Food",
      "name": "Pollo",
      "delta_share_pp": 0.14,
      "delta_afv": -13.26,
      "contrib_share": 1.07,
      "contrib_afv": -0.15
    },
    {
      "vertical": "Food",
      "name": "Empanadas",
      "delta_share_pp": -0.13,
      "delta_afv": -13.12,
      "contrib_share": -0.96,
      "contrib_afv": -0.72
    },
    {
      "vertical": "Food",
      "name": "Chivitos",
      "delta_share_pp": 0.1,
      "delta_afv": 12.21,
      "contrib_share": 0.9,
      "contrib_afv": 0.16
    },
    {
      "vertical": "Food",
      "name": "Panchos",
      "delta_share_pp": 0.11,
      "delta_afv": 22.01,
      "contrib_share": 0.84,
      "contrib_afv": 0.18
    },
    {
      "vertical": "Food",
      "name": "Sándwiches",
      "delta_share_pp": 0.15,
      "delta_afv": -8.14,
      "contrib_share": 0.84,
      "contrib_afv": -0.24
    },
    {
      "vertical": "Food",
      "name": "Licuados y Jugos",
      "delta_share_pp": -0.11,
      "delta_afv": 14.77,
      "contrib_share": -0.65,
      "contrib_afv": 0.02
    },
    {
      "vertical": "Food",
      "name": "Comida Mexicana",
      "delta_share_pp": -0.07,
      "delta_afv": 38.17,
      "contrib_share": -0.58,
      "contrib_afv": 0.34
    },
    {
      "vertical": "Food",
      "name": "Comida Vegetariana",
      "delta_share_pp": 0.05,
      "delta_afv": -8.2,
      "contrib_share": 0.31,
      "contrib_afv": -0.08
    },
    {
      "vertical": "Food",
      "name": "Comida China",
      "delta_share_pp": 0.03,
      "delta_afv": -18.04,
      "contrib_share": 0.29,
      "contrib_afv": -0.18
    },
    {
      "vertical": "Food",
      "name": "Picadas",
      "delta_share_pp": 0.03,
      "delta_afv": -3.86,
      "contrib_share": 0.24,
      "contrib_afv": -0.02
    },
    {
      "vertical": "Food",
      "name": "Woks",
      "delta_share_pp": 0.03,
      "delta_afv": 126.0,
      "contrib_share": 0.21,
      "contrib_afv": 0.05
    },
    {
      "vertical": "Food",
      "name": "Comida Venezolana",
      "delta_share_pp": -0.02,
      "delta_afv": 8.04,
      "contrib_share": -0.11,
      "contrib_afv": 0.07
    },
    {
      "vertical": "Food",
      "name": "Ensaladas",
      "delta_share_pp": -0.02,
      "delta_afv": -3.6,
      "contrib_share": -0.11,
      "contrib_afv": -0.04
    },
    {
      "vertical": "Food",
      "name": "Panaderías",
      "delta_share_pp": -0.02,
      "delta_afv": 0.58,
      "contrib_share": -0.11,
      "contrib_afv": 0.01
    },
    {
      "vertical": "Food",
      "name": "Tortillas",
      "delta_share_pp": -0.01,
      "delta_afv": 35.3,
      "contrib_share": -0.08,
      "contrib_afv": 0.13
    },
    {
      "vertical": "Food",
      "name": "Pescados y Mariscos",
      "delta_share_pp": 0.01,
      "delta_afv": -2.39,
      "contrib_share": 0.07,
      "contrib_afv": -0.01
    },
    {
      "vertical": "Food",
      "name": "Wraps",
      "delta_share_pp": -0.01,
      "delta_afv": 11.14,
      "contrib_share": -0.06,
      "contrib_afv": 0.16
    },
    {
      "vertical": "Food",
      "name": "Comida Japonesa",
      "delta_share_pp": -0.0,
      "delta_afv": -30.17,
      "contrib_share": -0.04,
      "contrib_afv": -0.02
    },
    {
      "vertical": "Food",
      "name": "Comida Vegana",
      "delta_share_pp": -0.0,
      "delta_afv": 20.7,
      "contrib_share": -0.02,
      "contrib_afv": 0.04
    },
    {
      "vertical": "Courier",
      "name": "UNKNOWN",
      "delta_share_pp": 0.0,
      "delta_afv": 0.0,
      "contrib_share": -0.0,
      "contrib_afv": 0.0
    },
    {
      "vertical": "D-Mart",
      "name": "UNKNOWN",
      "delta_share_pp": 0.0,
      "delta_afv": 5.99,
      "contrib_share": 0.0,
      "contrib_afv": 5.99
    },
    {
      "vertical": "Local Stores",
      "name": "UNKNOWN",
      "delta_share_pp": 0.0,
      "delta_afv": 3.75,
      "contrib_share": 0.0,
      "contrib_afv": 3.75
    },
    {
      "vertical": "Local Stores (Market)",
      "name": "UNKNOWN",
      "delta_share_pp": 0.0,
      "delta_afv": -3.9,
      "contrib_share": 0.0,
      "contrib_afv": -3.9
    }
  ],
  "segments_up": [
    {
      "vertical": "Food",
      "name": "Local Hero",
      "delta_share_pp": 5.81,
      "delta_share": "⬆️ 5.81",
      "contrib": 43.6,
      "afv": 754.39
    },
    {
      "vertical": "Local Stores (Market)",
      "name": "AAA",
      "delta_share_pp": 0.75,
      "delta_share": "⬆️ 0.75",
      "contrib": 10.98,
      "afv": 1426.36
    },
    {
      "vertical": "Food",
      "name": "Food N/D",
      "delta_share_pp": 0.33,
      "delta_share": "⬆️ 0.33",
      "contrib": 2.44,
      "afv": 765.5
    }
  ],
  "segments_down": [
    {
      "vertical": "Food",
      "name": "Long Tail",
      "delta_share_pp": -5.22,
      "delta_share": "⬇️ 5.22",
      "contrib": -40.84,
      "afv": 757.94
    },
    {
      "vertical": "Local Stores (Market)",
      "name": "Not AAA",
      "delta_share_pp": -0.75,
      "delta_share": "⬇️ 0.75",
      "contrib": -5.01,
      "afv": 665.63
    },
    {
      "vertical": "Food",
      "name": "Global KA",
      "delta_share_pp": -0.61,
      "delta_share": "⬇️ 0.61",
      "contrib": -3.93,
      "afv": 637.53
    },
    {
      "vertical": "Food",
      "name": "National KA",
      "delta_share_pp": -0.29,
      "delta_share": "⬇️ 0.29",
      "contrib": -2.4,
      "afv": 817.45
    }
  ],
  "cocinasup": [
    {
      "vertical": "Food",
      "name": "Cafetería",
      "delta_share_pp": 0.38,
      "delta_share": "⬆️ 0.38",
      "contrib": 2.25,
      "afv": 575.16
    },
    {
      "vertical": "Food",
      "name": "Helados",
      "delta_share_pp": 0.35,
      "delta_share": "⬆️ 0.35",
      "contrib": 2.19,
      "afv": 620.46
    },
    {
      "vertical": "Food",
      "name": "Postres",
      "delta_share_pp": 0.3,
      "delta_share": "⬆️ 0.30",
      "contrib": 1.98,
      "afv": 615.11
    },
    {
      "vertical": "Food",
      "name": "Tartas",
      "delta_share_pp": 0.22,
      "delta_share": "⬆️ 0.22",
      "contrib": 1.1,
      "afv": 544.13
    },
    {
      "vertical": "Food",
      "name": "Pastas",
      "delta_share_pp": 0.21,
      "delta_share": "⬆️ 0.21",
      "contrib": 1.43,
      "afv": 654.43
    },
    {
      "vertical": "Food",
      "name": "Poke",
      "delta_share_pp": 0.2,
      "delta_share": "⬆️ 0.20",
      "contrib": 1.49,
      "afv": 752.25
    },
    {
      "vertical": "Food",
      "name": "Comida Armenia",
      "delta_share_pp": 0.16,
      "delta_share": "⬆️ 0.16",
      "contrib": 1.3,
      "afv": 807.48
    },
    {
      "vertical": "Food",
      "name": "Sándwiches",
      "delta_share_pp": 0.15,
      "delta_share": "⬆️ 0.15",
      "contrib": 0.84,
      "afv": 559.0
    },
    {
      "vertical": "Food",
      "name": "Pollo",
      "delta_share_pp": 0.14,
      "delta_share": "⬆️ 0.14",
      "contrib": 1.07,
      "afv": 743.43
    },
    {
      "vertical": "Food",
      "name": "Panchos",
      "delta_share_pp": 0.11,
      "delta_share": "⬆️ 0.11",
      "contrib": 0.84,
      "afv": 795.6
    }
  ],
  "cocinasdown": [
    {
      "vertical": "Food",
      "name": "Pizzas",
      "delta_share_pp": -0.92,
      "delta_share": "⬇️ 0.92",
      "contrib": -7.23,
      "afv": 776.75
    },
    {
      "vertical": "Food",
      "name": "Hamburguesas",
      "delta_share_pp": -0.62,
      "delta_share": "⬇️ 0.62",
      "contrib": -4.53,
      "afv": 732.88
    },
    {
      "vertical": "Food",
      "name": "Milanesas",
      "delta_share_pp": -0.33,
      "delta_share": "⬇️ 0.33",
      "contrib": -2.51,
      "afv": 767.33
    },
    {
      "vertical": "Food",
      "name": "UNKNOWN",
      "delta_share_pp": -0.17,
      "delta_share": "⬇️ 0.17",
      "contrib": -1.36,
      "afv": 716.7
    },
    {
      "vertical": "Food",
      "name": "Empanadas",
      "delta_share_pp": -0.13,
      "delta_share": "⬇️ 0.13",
      "contrib": -0.96,
      "afv": 704.45
    },
    {
      "vertical": "Food",
      "name": "Sushi",
      "delta_share_pp": -0.12,
      "delta_share": "⬇️ 0.12",
      "contrib": -1.6,
      "afv": 1324.83
    },
    {
      "vertical": "Food",
      "name": "Licuados y Jugos",
      "delta_share_pp": -0.11,
      "delta_share": "⬇️ 0.11",
      "contrib": -0.65,
      "afv": 597.46
    }
  ],
  "incomeup": [
    {
      "segmento": "HIGH",
      "ordenes_act": 268884,
      "ordenes_ref": 257404,
      "share_act": 23.55,
      "share_ref": 22.97,
      "dif_share_en_pp": 0.58,
      "delta": "+0.58 p.p."
    }
  ],
  "incomedown": [
    {
      "segmento": "MID-LOW",
      "ordenes_act": 8844,
      "ordenes_ref": 9006,
      "share_act": 0.77,
      "share_ref": 0.8,
      "dif_share_en_pp": -0.03,
      "delta": "-0.03 p.p."
    },
    {
      "segmento": "MID-HIGH",
      "ordenes_act": 663245,
      "ordenes_ref": 652433,
      "share_act": 58.1,
      "share_ref": 58.22,
      "dif_share_en_pp": -0.12,
      "delta": "-0.12 p.p."
    },
    {
      "segmento": "MID",
      "ordenes_act": 195337,
      "ordenes_ref": 197280,
      "share_act": 17.11,
      "share_ref": 17.61,
      "dif_share_en_pp": -0.5,
      "delta": "-0.5 p.p."
    }
  ],
  "incomesummary": "HIGH +0.58 p.p. ganaron participación, mientras que MID-LOW -0.03 p.p., MID-HIGH -0.12 p.p. la perdieron. El mix se desplaza hacia tickets más altos."
}
