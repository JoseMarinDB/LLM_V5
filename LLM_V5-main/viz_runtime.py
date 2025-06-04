# viz_runtime.py
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ───── Funciones de visualización ──────────────────────────────────────

def build_waterfall(ctx):
    overall_bs = ctx["bs"]
    overall_aiv = ctx["aiv"]
    overall_mix = ctx["mix"]
    fig = go.Figure(go.Waterfall(
        measure=["relative", "relative", "relative"],
        x=["Basket Size", "AIV", "Mix"],
        y=[overall_bs, overall_aiv, overall_mix],
        connector={"line": {"color": "grey"}}
    ))
    fig.update_layout(
        title="Drivers del ΔAFV país (solo variaciones)",
        xaxis_title="",
        yaxis_title="$ por pedido"
    )
    return fig

def build_bar_verticals(ctx, umbral_lbl=0.2):
    df = ctx["verticals"].copy()
    df["impacto_neto"] = df["contrib_share_overall"] + df["contrib_afv_intra"]
    df = df.sort_values("impacto_neto")            # orden neto

    df["etiqueta_y"] = [
        f"{row['nivel2']} ({row['impacto_neto']:+.2f})" for _, row in df.iterrows()
    ]

    fig = go.Figure()

    # helper para etiquetas
    fmt = lambda v: f"{v:+.2f}" if abs(v) >= umbral_lbl else ""
    txt_color = lambda v: "white" if abs(v) >= umbral_lbl else "rgba(0,0,0,0)"

    # --- Share (rojo) ---
    fig.add_bar(
        y=df["etiqueta_y"], x=df["contrib_share_overall"], orientation="h",
        name="Share", marker_color="#e74c3c", opacity=0.9, offsetgroup="share",
        text=[fmt(v) for v in df["contrib_share_overall"]],
        textfont_color=[txt_color(v) for v in df["contrib_share_overall"]],
        textposition="inside", insidetextanchor="middle"
    )

    # --- AFV interno (azul) ---
    fig.add_bar(
        y=df["etiqueta_y"], x=df["contrib_afv_intra"], orientation="h",
        name="AFV interno", marker_color="#3498db", opacity=0.9, offsetgroup="afv",
        text=[fmt(v) for v in df["contrib_afv_intra"]],
        textfont_color=[txt_color(v) for v in df["contrib_afv_intra"]],
        textposition="inside", insidetextanchor="middle"
    )

    # línea cero
    fig.add_shape(type="line", x0=0, x1=0, y0=-0.5, y1=len(df)-0.5,
                  line=dict(color="gray", width=1))

    fig.update_layout(
        template="plotly_dark",
        barmode="overlay",                     # ⬅️ barras superpuestas, no apiladas
        bargap=0.35,
        title="Impacto de cada vertical en AFV país",
        xaxis_title="$/pedido (impacto sobre el promedio país)",
        yaxis_title="", legend_title=""
    )
    return fig

def build_scatter_cocinas(ctx):
    df = ctx["cocinas_movers"]

    signo = np.where(df["delta_share_pp"] > 0, "Sube", "Baja")
    fig = go.Figure(go.Scatter(
        x=df["delta_share_pp"],
        y=df["afv"],
        mode="markers+text",
        text=df["name"],
        textposition="bottom center",          # ← etiqueta debajo
        textfont=dict(size=10),
        marker=dict(
            size=np.sqrt(np.abs(df["contrib"])) * 6,  # burbuja ∝ √|impacto|
            color=np.where(signo == "Sube", "limegreen", "crimson"),
            line=dict(width=1, color="white"),
            opacity=0.9
        ),
        hovertemplate="<b>%{text}</b><br>ΔShare: %{x:+.2f} p.p.<br>AFV: $%{y}<br>Impacto: %{marker.size:.1f}<extra></extra>"
    ))

    # Líneas guía
    fig.add_vline(x=0, line_width=1, line_dash="dot", line_color="gray")
    fig.add_hline(y=ctx["afv_ref"], line_width=1, line_dash="dot", line_color="gray",
                  annotation_text="AFV país", annotation_position="top left")

    fig.update_layout(
        xaxis_title="Cambio de share (p.p.)",
        yaxis_title="AFV actual ($)",
        template="plotly_dark",
        height=420
    )
    return fig

def build_bar_income(ctx, umbral=0.05):
    df = ctx["income_df"]  # ← No filtra por umbral
    fig = go.Figure(go.Bar(
        y=df["segmento"],
        x=df["dif_share_en_pp"],
        orientation="h",
        marker_color=np.where(df["dif_share_en_pp"] > 0, "limegreen", "crimson"),
        text=df["dif_share_en_pp"].map(lambda v: f"{v:+.2f}"),
        textposition="inside"
    ))
    fig.update_layout(
        title="Share por income (p.p.)",
        xaxis_title="Puntos porcentuales",
        template="plotly_dark",
        height=320
    )
    return fig


def build_line_afv(ctx):
    df = ctx["afv_timeline"]
    latest_month = df["month_date"].max()

    fig = go.Figure()

    for vert, sub in df.groupby("vertical"):
        # línea completa
        fig.add_scatter(
            x=sub["month_date"],
            y=sub["afv"],
            mode="lines+markers",
            name=vert,
            line=dict(width=2)
        )

        # punto del mes actual con etiqueta
        last_row = sub[sub["month_date"] == latest_month]
        if not last_row.empty:
            afv_val = last_row["afv"].iloc[0]
            fig.add_scatter(
                x=last_row["month_date"],
                y=last_row["afv"],
                mode="markers+text",
                marker=dict(size=10, symbol="circle", color="yellow"),
                text=[f"${afv_val:,.2f}"],              # ← etiqueta visible
                textposition="top center",
                showlegend=False,
                hovertemplate=f"<b>{vert}</b><br>AFV actual: $%{{y:.2f}}"
            )

    fig.update_layout(
        title="AFV mensual por vertical (último punto resaltado)",
        xaxis_title="Mes",
        yaxis_title="AFV ($)",
        template="plotly_dark"
    )
    return fig
def build_waterfall_vertical(ctx, vertical, pct_base=True, umbral=0.05):
    """
    Waterfall para la vertical con drivers internos (Basket-Size, AIV, Mix) y Subtotal.

    Parameters
    ----------
    ctx : dict
        Contexto con df de verticales.
    vertical : str
        Nombre exacto de la vertical a graficar.
    pct_base : bool, default True
        • True  -> valores como % sobre AFV_ref.  
        • False -> valores en $ por pedido.
    umbral : float, default 0.05
        Umbral (en unidades finales) por debajo del cual el texto se coloca outside
        para evitar que se aplaste dentro de la barra.
    """
    # ---------------- datos ----------------
    df  = ctx["verticals"]
    row = df[df["nivel2"] == vertical].iloc[0]

    efectos = {
        "Basket Size": row["efecto_bs"],
        "Avg Item Value": row["efecto_aiv"],
        "Mix": row["efecto_mix"],
    }
    delta   = row["delta_afv"]
    afv_ref = row["afv_ref"]

    # ---------------- escala ----------------
    if pct_base and afv_ref != 0:
        efectos = {k: v / afv_ref * 100 for k, v in efectos.items()}
        delta_val = delta / afv_ref * 100
        unidad = "% del AFV ref"
        fmt = lambda x: f"{x:+.2f}%"
    else:
        delta_val = delta
        unidad = "$ por pedido"
        fmt = lambda x: f"{x:+.2f}"

    valores = list(efectos.values()) + [delta_val]
    labels  = [fmt(v) for v in valores]

    # ---------------- colocación de textos ----------------
    posiciones = ["inside" if abs(v) >= umbral else "outside" for v in valores]

    # ---------------- dibujo ----------------
    fig = go.Figure(go.Waterfall(
        measure   = ["relative"]*3 + ["total"],
        x         = list(efectos.keys()) + ["Subtotal"],
        y         = valores,
        text      = labels,
        textposition = posiciones,
        textfont  = dict(size=11, color="white"),
        texttemplate = "%{text}",
        cliponaxis = False,                         # permite texto fuera del eje
        connector  = dict(line=dict(color="lightgrey")),
        increasing = dict(marker=dict(color="#2ecc71")),
        decreasing = dict(marker=dict(color="#e74c3c")),
        totals     = dict(marker=dict(color="#95a5a6"))
    ))

    fig.update_layout(
        title=f"Efectos internos – {vertical}",
        yaxis_title=unidad,
        template="plotly_dark",
        showlegend=False,
        margin=dict(t=80)                           # margen superior p/ textos outside
    )
    return fig






CHART_BUILDERS = {
#    "WATERFALL_AFV":  build_waterfall,
    "BAR_VERTICALS":  build_bar_verticals,
    "SCATTER_COCINAS": build_scatter_cocinas,
    "BAR_INCOME": build_bar_income,
    "LINE_AFV": build_line_afv

    # agrega más aquí
}

# en la misma sección donde defines CHART_BUILDERS
def _wf_factory(vert):
    return lambda ctx, v=vert: build_waterfall_vertical(ctx, v)
