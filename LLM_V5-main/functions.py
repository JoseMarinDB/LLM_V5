import pandas as pd
import numpy as np

def fmt2(x):
    """Devuelve un string con 2 decimales (respeta signos)."""
    if pd.isna(x):
        return "-"
    return f"{x:.2f}"

def calcular_metricas_basicas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula las métricas básicas del universo de negocio:
    - AIV: Average Item Value
    - AFV: Average Food Value
    - BS: Basket Size
    """
    df = df.copy()
    df["bs_ref"] = df["qty_ref"] / df["orders_ref"]
    df["bs_act"] = df["qty_act"] / df["orders_act"]
    df["afv_ref"] = df["gfv_ref"] / df["orders_ref"]
    df["afv_act"] = df["gfv_act"] / df["orders_act"]
    df["aiv_ref"] = df["afv_ref"] / df["bs_ref"]
    df["aiv_act"] = df["afv_act"] / df["bs_act"]
    # Incentivos por pedido
    df["incent_ref_pp"] = df["incent_ref"] / df["orders_ref"]
    df["incent_act_pp"] = df["incent_act"] / df["orders_act"]
    
    return df

def calcular_deltas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula los deltas de AFV, BS y AIV, y los deltas de shares de act_gfv_country y act_gfv_local.
    Agrega las columnas:
    - delta_afv = afv_act - afv_ref
    - delta_bs = bs_act - bs_ref
    - delta_aiv = aiv_act - aiv_ref
    - delta_share_gfv_country = share_act_gfv_country - share_ref_gfv_country
    - delta_share_gfv_local = share_act_gfv_local - share_ref_gfv_local
    """
    df = df.copy()
    df["delta_afv"] = df["afv_act"] - df["afv_ref"]
    df["delta_bs"] = df["bs_act"] - df["bs_ref"]
    df["delta_aiv"] = df["aiv_act"] - df["aiv_ref"]
    df["delta_share_orders_country"] = df["share_act_orders_country"] - df["share_ref_orders_country"]
    df["delta_share_orders_local"] = df["share_act_orders_local"] - df["share_ref_orders_local"]
    # Incentivos
    df["delta_incent_pp"] = df["incent_act_pp"] - df["incent_ref_pp"]

    return df
       
def calcular_efectos_afv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Descompone ΔAFV interno ($/pedido) y, para filas VERTICAL,
    añade contribución al AFV OVERALL.
    """
    df = df.copy()

    # --- 1. Drivers internos (BS, AIV) -----------------------------------
    df["efecto_bs"]  = (df["bs_act"]  - df["bs_ref"])  * df["aiv_ref"]
    df["efecto_aiv"] = (df["aiv_act"] - df["aiv_ref"]) * df["bs_act"]

    # --- 2. Share interno (solo OVERALL) ---------------------------------
    df["efecto_share"] = 0.0
    mask_overall = df["nivel1"] == "OVERALL"
#    df.loc[mask_overall, "efecto_share"] = (
#        (df["share_act_orders_country"] - df["share_ref_orders_country"])
#        * df["afv_ref"]
#    )
    df.loc[mask_overall, "efecto_share"] = (
        (df["share_act_orders_country"] - df["share_ref_orders_country"])
        * df["afv_ref"]
    )

    # --- 3. Mix (residual) ----------------------------------------------
    df["efecto_mix"] = (
        df["delta_afv"]
        - df["efecto_bs"]
        - df["efecto_aiv"]
        - df["efecto_share"]
    )

    # --- 4. Contribución de cada VERTICAL al AFV país --------------------
    df["contrib_share_overall"] = 0.0         # impacto por pérdida/ganancia de share
    df["contrib_afv_intra"]     = 0.0         # mejora/deterioro propio ponderado

    mask_vertical = df["nivel1"] == "VERTICAL"
    df.loc[mask_vertical, "contrib_share_overall"] = (
        (df["share_act_orders_country"] - df["share_ref_orders_country"])
        * df["afv_ref"]
    )
    df.loc[mask_vertical, "contrib_afv_intra"] = (
        df["share_act_orders_country"]
        * (df["afv_act"] - df["afv_ref"])
    )

    # Para la fila OVERALL, sumamos las contribuciones de todas las verticales
    if mask_overall.any():
        df.loc[mask_overall, "contrib_share_overall"] = (
            df.loc[mask_vertical, "contrib_share_overall"].sum()
        )
        df.loc[mask_overall, "contrib_afv_intra"] = (
            df.loc[mask_vertical, "contrib_afv_intra"].sum()
        )

    # --- 5. Chequeo interno ---------------------------------------------
    df["descuadre"] = (
        df["efecto_bs"] + df["efecto_aiv"] +
        df["efecto_mix"] + df["efecto_share"] -
        df["delta_afv"]
    )

    # --- 6. Contribución local (todos los niveles) -----------------------
    # impacto que el nodo genera en el AFV de su nivel padre
    df["contrib_share_local"] = (
        df["delta_share_orders_local"] * df["afv_ref"]
    )

    df["contrib_afv_intra_local"] = (
        df["share_act_orders_local"] * (df["afv_act"] - df["afv_ref"])
    )

    return df

def calcular_deltas_porcentaje(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade variaciones relativas (%) y variaciones de share en puntos porcentuales (p.p.).

    Nuevas columnas:
        delta_afv_pct                → % vs AFV_ref
        delta_bs_pct                 → % vs BS_ref
        delta_aiv_pct                → % vs AIV_ref
        delta_share_orders_country_pp→ p.p. (Share_act - Share_ref)*100
        delta_share_orders_local_pp  → p.p. idem local
    """
    out = df.copy()

    # --- % sobre el valor base ------------------------------------------
    out["delta_afv_pct"] = np.where(out["afv_ref"] == 0, np.nan , (out["delta_afv"] / out["afv_ref"]) * 100 )
    out["delta_bs_pct"] = np.where(out["bs_ref"] == 0, np.nan , (out["delta_bs"] / out["bs_ref"]) * 100)
    out["delta_aiv_pct"] = np.where( out["aiv_ref"] == 0, np.nan, (out["delta_aiv"] / out["aiv_ref"]) * 100)

    # --- puntos porcentuales -------------------------------------------
    out["delta_share_orders_country_pp"] = ( out["delta_share_orders_country"] * 100)
    out["delta_share_orders_local_pp"] = ( out["delta_share_orders_local"] * 100)

    # Redondeo final
    cols_round = [
        "delta_afv_pct", "delta_bs_pct", "delta_aiv_pct",
        "delta_share_orders_country_pp", "delta_share_orders_local_pp"
    ]
    out[cols_round] = out[cols_round].round(2)

    return out

def preparar_json_llm(df_overall, df_vertical, df_segment, df_cocina):
    """
    Devuelve un dict listo para el modelo:
      overall  · verticals  · segments  · cocinas
    """

    # ---------- OVERALL ----------
    overall_cols = [
        "afv_act",
        "delta_afv", "delta_afv_pct",
        "contrib_share_overall", "contrib_afv_intra",
        "efecto_bs", "efecto_aiv", "efecto_mix",
        "delta_bs", "delta_bs_pct"
    ]

    overall = (
        df_overall.iloc[0][overall_cols]
          .apply(fmt2)        # <-- formatea TODOS los campos
          .to_dict()
    )
    # --- verticales ------------------------------------------------------
    v_list = []
    for _, r in df_vertical.iterrows():
        if not r["is_relevante"]:
            continue
        

        block = {
            "name":           r["nivel2"],
            "afv_act":        fmt2(r["afv_act"]), 
            "driver":         r["driver"],
            "delta_afv":      round(r["delta_afv"], 2),
            "delta_afv_pct":  round(r["delta_afv_pct"], 2),
            "delta_share_pp": round(r["delta_share_orders_country_pp"], 2),
            "contrib_share":  round(r["contrib_share_overall"], 2),
            "contrib_afv":    round(r["contrib_afv_intra"], 2),
            "impacto_neto":   round(r["contrib_share_overall"], 2) + round(r["contrib_afv_intra"], 2),
            "efecto_bs":      fmt2(r["efecto_bs"]),
            "efecto_aiv":     fmt2(r["efecto_aiv"]),
            "efecto_mix":     fmt2(r["efecto_mix"]),
            "incent_act_pp":  fmt2(r["incent_act_pp"]),
            "delta_incent":   round(r["delta_incent_pp"], 2)
        }

        # contexto interno (solo vertical)
        block.update({
            "efecto_bs":  round(r["efecto_bs"], 2),
            "efecto_aiv": round(r["efecto_aiv"], 2),
            "efecto_mix": round(r["efecto_mix"], 2)
        })
        v_list.append(block)

    # --- segmentos & cocinas --------------------------------------------
    def resumen(df, nivel_key):
        out = []
        for _, r in df.iterrows():
            out.append({
                "vertical":      r["nivel2"],
                "name":          r["nivel3"],
                "delta_share_pp": round(r["delta_share_orders_local_pp"], 2),
                "delta_afv":      round(r["delta_afv"], 2),
                "contrib_share":  round(r["contrib_share_local"], 2),
                "contrib_afv":    round(r["contrib_afv_intra_local"], 2)
            })
        # ordená por |contrib_share| descendente
        return sorted(out, key=lambda x: abs(x["contrib_share"]), reverse=True)

    seg_json = resumen(df_segment, "SEGMENT")
    coc_json = resumen(df_cocina, "COCINA")
    
    return {
        "overall": overall,
        "verticals": v_list,
        "segments": seg_json,
        "cocinas":  coc_json
    }

def resumen_generico(df, nivel, top_n=3, min_pp=0.25):
    """
    Unifica la lógica para SEGMENT y COCINA.
    nivel: 'SEGMENT' o 'COCINA'
    Agrupa por vertical para dar top movers dentro de cada una.
    """
    assert nivel in ("SEGMENT", "COCINA")
    df = df[df["nivel1"] == nivel].copy()

    # Ordenamos por vertical
    resumen = []

    for vert, sub in df.groupby("nivel2"):

        # Ordenar por cambio de share local (p.p.)
        sub["delta_abs"] = sub["delta_share_orders_local_pp"].abs()
        sub_sorted = sub.sort_values("delta_abs", ascending=False)

        # 1) Filtramos por umbral
        relevantes = sub_sorted[sub_sorted["delta_abs"] >= min_pp]

        # 2) Si no hay suficientes, traemos top_n
        if len(relevantes) < top_n:
            relevantes = pd.concat([relevantes,
                                    sub_sorted.head(top_n)]).drop_duplicates()

        # armamos la lista
        for _, row in relevantes.iterrows():
            resumen.append({
                "vertical": vert,
                "name":     row["nivel3"] if nivel == "COCINA" else row["nivel3"],  # classification o cuisine
                "delta_share_pp": round(row["delta_share_orders_local_pp"], 2),
                "delta_afv":      round(row["delta_afv"], 2)
            })

    # devuelve lista de dicts ya ordenada por |Δshare|
    return sorted(resumen, key=lambda x: abs(x["delta_share_pp"]), reverse=True)

def resumen_segment(df_segment, top_n=3, min_pp=0.25):
    return resumen_generico(df_segment, "SEGMENT", top_n, min_pp)

def resumen_cocina(df_cocina, top_n=3, min_pp=0.25):
    return resumen_generico(df_cocina, "COCINA", top_n, min_pp)

def top_movers(df, level, top_n=10, min_pp=0.1):
    """
    Devuelve dos listas: top_suben, top_bajan (máx top_n cada una)
    """
    df = df[df["nivel1"] == level].copy()
    df["abs_pp"] = df["delta_share_orders_local_pp"].abs()

    # Filtra los que superan el umbral
    df = df[df["abs_pp"] >= min_pp]

    up   = df[df["delta_share_orders_local_pp"] > 0]\
           .sort_values("abs_pp", ascending=False).head(top_n)
    down = df[df["delta_share_orders_local_pp"] < 0]\
           .sort_values("abs_pp", ascending=False).head(top_n)

    def row_to_dict(r):
        delta_pp = r["delta_share_orders_local_pp"]      # numérico
        arrow = "⬆️" if delta_pp > 0 else "⬇️"
        return {
            "vertical": r["nivel2"],
            "name":     r["nivel3"],
            "delta_share_pp": round(delta_pp, 2),        # <-- numérico puro
            "delta_share":     f"{arrow} {abs(delta_pp):.2f}",  # sólo para la tabla
            "contrib":  round(r["contrib_share_local"], 2),
            "afv":      round(r["afv_act"], 2)
        }

    return [row_to_dict(r) for _, r in up.iterrows()], \
           [row_to_dict(r) for _, r in down.iterrows()]

def clasificar_driver_vertical(df_vert, umbral_pp=0.1, umbral_afv=0.5):
    """
    Devuelve df con columna driver = 'SHARE' o 'AFV'.
    Se basa en cuál explicación absoluta pesa más.
    """
    df = df_vert.copy()

    cond_share = df["contrib_share_overall"].abs() >= df["contrib_afv_intra"].abs()
    df["driver"] = np.where(cond_share, "SHARE", "AFV")

    # pequeño filtro de relevancia para no hablar de ruído
    df["is_relevante"] = (
        (df["contrib_share_overall"].abs() > umbral_pp) |
        (df["contrib_afv_intra"].abs()   > umbral_afv)
    )
    return df

def build_income_summary(df_income, top_n=2):
    """Devuelve una frase ya armada para el Executive Brief."""
    df_sorted = df_income.sort_values("dif_share_en_pp", ascending=False)

    winners = df_sorted[df_sorted["dif_share_en_pp"] > 0]\
              .head(top_n)[["segmento", "dif_share_en_pp"]]
    losers  = df_sorted[df_sorted["dif_share_en_pp"] < 0]\
              .head(top_n)[["segmento", "dif_share_en_pp"]]

    # Redondeo y signo
    w_txt = ", ".join([f"{seg} +{pp:.2f} p.p." for seg, pp in winners.values])
    l_txt = ", ".join([f"{seg} {pp:.2f} p.p."  for seg, pp in losers.values])

    return (f"{w_txt} ganaron participación, mientras que "
            f"{l_txt} la perdieron. El mix se desplaza "
            f"hacia {'tickets más altos' if winners.iloc[0]['segmento']=='HIGH' else 'tickets más bajos'}.")
