# main_generate.py – genera todos los datasets jerárquicos con lógica separada
import json, pathlib
import pandas as pd
from functions import *
from datetime import datetime
from llm import llm_invoke
from dotenv import load_dotenv
import os
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account
import re

# ───── Configuración ──────────────────────────────────────────────────
LOAD_DOTENV = load_dotenv()

# ───── Funciones ───────────────────────────────────────────────────────
def make_llm_prompt(biz_json):
    """
    Devuelve el prompt con placeholders {{…}} para que el LLM los complete
    usando el JSON que se entrega al final.
    """
    return f"""
Eres analista senior en quick-commerce. Generá un informe EXACTAMENTE en este formato Markdown:

## 📌 Finance Insights
<!--CHART:LINE_AFV-->
- **AFV país:** ${{overall.afv_act}}
- **ΔAFV total:** **${{overall.delta_afv}} ({{overall.delta_afv_pct}}%)**
- **Efectos:**
    - Basket Size: ${{overall.efecto_bs}}
    - AIV: ${{overall.efecto_aiv}}
    - Mix: ${{overall.efecto_mix}}

- **Análisis:** 
    Indica claramente qué verticales aportaron más y cómo interactuaron los efectos de share y AFV interno.

    <!--CHART:BAR_VERTICALS-->

- **Cocinas clave:** 
    Resume en 2-3 frases qué cocinas explican la caída o suba de AFV usando `cocinasdown` y `cocinasup` (nombres, ΔShare, AFV). No utilices cursivas ni negritas en esta frase.
    
    <!--CHART:SCATTER_COCINAS-->

- **Análisis de Usuarios:** 
    Explica {{incomesummary}}

    <!--CHART:BAR_INCOME-->

---

## 📌 Análisis Detallado por Vertical
{{#each verticals}}
    ### 🏷️ {{name}}

    | Métrica | Valor |
    |---------|-------|
    | **AFV actual** | ${{afv_act}} |
    | **ΔAFV** | ${{delta_afv}} ({{delta_afv_pct}} %) |
    | **Impacto país** | Efecto Share: ${{contrib_share}} · AFV interno: ${{contrib_afv}} · **Neto: ${{impacto_neto}}** |
    | **Efectos** | BS: ${{efecto_bs}} · AIV: ${{efecto_aiv}} · Mix: ${{efecto_mix}} |
    | **Incentivo p/orden** | ${{incent_act_pp}} (Δ {{delta_incent}}) |

    **Análisis:** Resume en una frase por qué sube o baja usando los datos de la tabla (máx. 35 palabras).

    <!--CHART:WF_{{name}}-->

{{/each}}

---

## 📌 Segmentos con mayor cambio de share (≥ ±0,3 p.p.)

### 🔼 Suben
| Vertical | Segmento | ΔShare | Contribución ($) | Comentario |
|----------|----------|--------|------------------|------------|
{{#each segments_up}}
| {{vertical}} | {{name}} | {{delta_share}} | {{contrib}} | {{comment}} |
{{/each}}

### 🔽 Bajan
| Vertical | Segmento | ΔShare | Contribución ($) | Comentario |
|----------|----------|--------|------------------|------------|
{{#each segments_down}}
| {{vertical}} | {{name}} | {{delta_share}} | {{contrib}} | {{comment}} |
{{/each}}

---

## 📌 Cocinas con mayor cambio de share (≥ ±0,3 p.p.)

### 🔼 Suben
| Vertical | Cocina | ΔShare | AFV ($) |
|----------|--------|--------|---------|
{{#each cocinas_up}}
| {{vertical}} | {{name}} | {{delta_share}} | {{afv}} |
{{/each}}

### 🔽 Bajan
| Vertical | Cocina | ΔShare | AFV ($) |
|----------|--------|--------|---------|
{{#each cocinas_down}}
| {{vertical}} | {{name}} | {{delta_share}} | {{afv}} |
{{/each}}

---

Usá el siguiente JSON para completar estrictamente los campos:

```json
{json.dumps(biz_json, ensure_ascii=False, indent=2)}
"""


# ─────────────────────────────── BigQuery ──────────────────────────────
def run_bigquery_query(creds_path: str, query: str) -> pd.DataFrame:
    client = bigquery.Client(
        credentials=service_account.Credentials.from_service_account_file(creds_path)
    )
    job_config = bigquery.QueryJobConfig()
    job_config.use_query_cache = True

    return client.query(query, job_config=job_config).to_dataframe()

# ─────────────────────────────── Limpieza de Markdown ──────────────────────────────
def clean_md_whitespace(md_text: str) -> str:
    # elimina cursivas y dobles espacios donde aparezca patrón _texto_
    md_text = re.sub(r'_([^_]+)_', r'\1', md_text)
    # normaliza espacios que hayan quedado pegados a paréntesis
    md_text = re.sub(r'\)\s*(?=[A-Za-z0-9])', ') ', md_text)
    return md_text


# ───── Parámetros ─────────────────────────────────────────────────────
CRED_PATH  = pathlib.Path(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
SQL_PATH   = pathlib.Path("segments_base.sql")
SQL_INCOME_PATH = pathlib.Path("segments_income.sql")
OUT_DIR    = pathlib.Path("out_data")
SQL_AFV_TREND_PATH = pathlib.Path("afv_timeline.sql")   # guarda tu query aquí


# Calcular fechas FROM y TO

FROM_REF = '2025-01-01'
TO_REF   = '2025-01-31'
FROM_ACT = '2025-02-01'
TO_ACT   = '2025-02-28'
COUNTRY  = 'Uruguay'





# ───── Cargar plantilla SQL ────────────────────────────────────────────
with open(SQL_PATH, "r", encoding="utf-8") as f:
    sql_template = f.read()
 
SQL_QUERY = sql_template.format(
    ref_from=FROM_REF,
    ref_to=TO_REF,
    act_from=FROM_ACT,
    act_to=TO_ACT,
    country=COUNTRY
)
# ───── Cargar plantilla SQL de ingresos ─────────────────────────────────
with open(SQL_INCOME_PATH, "r", encoding="utf-8") as f:
    sql_template_2 = f.read()

SQL_INCOME_QUERY= sql_template_2.format(
    ref_from=FROM_REF,
    ref_to=TO_REF,
    act_from=FROM_ACT,
    act_to=TO_ACT,
    country=COUNTRY,
    income=True
)

# ───── Cargar plantilla SQL de tendencia AFV ───────────────────────────
with open(SQL_AFV_TREND_PATH, "r", encoding="utf-8") as f:
    sql_tl_template = f.read()

SQL_AFV_TREND = sql_tl_template.format(
    act_to=TO_ACT,          # último mes = mes “actual”
    num_total_months_to_display=12,
    country=COUNTRY
)

# ───── Calcular días de referencia y actividad ──────────────────────────
def days_between(start, end):
    return (datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days + 1
REF_DAYS = days_between(FROM_REF, TO_REF)
ACT_DAYS = days_between(FROM_ACT, TO_ACT)

# ───── Crear directorio de salida ──────────────────────────────────────
OUT_DIR.mkdir(exist_ok=True)


# ───── 1) Extrae datos base de BigQuery ───────────────────────────────
df_base = run_bigquery_query(CRED_PATH, SQL_QUERY)

df_income = run_bigquery_query(CRED_PATH, SQL_INCOME_QUERY)

df_timeline = run_bigquery_query(CRED_PATH, SQL_AFV_TREND)
df_timeline["month_date"] = pd.to_datetime(df_timeline["month_date"])

# Guardar datos base en CSV
df_base.to_csv(OUT_DIR / "datos_base.csv", index=False)
df_income.to_csv(OUT_DIR / "datos_ingresos.csv", index=False)


# 2) Split por nivel ---------------------------------------------------------
nivel_map = {"OVERALL": "overall", "VERTICAL": "vertical",
             "SEGMENT": "segment", "COCINA": "cocina"}

dfs = {key: df_base[df_base["nivel1"] == lvl].copy()
       for lvl, key in nivel_map.items()}

# 3) Transformaciones comunes -----------------------------------------------
for key, df in dfs.items():
    dfs[key] = (df.pipe(calcular_metricas_basicas)
                  .pipe(calcular_deltas)
                  .pipe(calcular_efectos_afv)
                  .pipe(calcular_deltas_porcentaje))

# 4) Clasificar driver + relevancia en verticales ----------------------------
dfs["vertical"] = clasificar_driver_vertical(dfs["vertical"])

# 5) Resúmenes segment / cocina ---------------------------------------------
seg_json   = resumen_segment(dfs["segment"])
coc_json   = resumen_cocina(dfs["cocina"])
# 5.1) Ingresos por segmento y cocina ---------------------------------------
income_up   = df_income[df_income["dif_share_en_pp"] > 0]\
               .assign(delta=lambda d: "+"+d["dif_share_en_pp"].astype(str)+" p.p.")\
               .to_dict("records")
income_down = df_income[df_income["dif_share_en_pp"] < 0]\
               .assign(delta=lambda d: d["dif_share_en_pp"].astype(str)+" p.p.")\
               .to_dict("records")
income_summary = build_income_summary(df_income)


#GUARDAR TODOS LOS DATAFRAMES EN CSV
for key, df in dfs.items():
    df.to_csv(OUT_DIR / f"datos_{key}.csv", index=False)
    
    
# 6) Business JSON para el LLM ----------------------------------------------
biz_json = preparar_json_llm(
    df_overall = dfs["overall"],
    df_vertical= dfs["vertical"],
    df_segment = dfs["segment"],
    df_cocina  = dfs["cocina"]       # pasa los DF completos; la función internamente filtra
)
seg_up, seg_down = top_movers(dfs["segment"], "SEGMENT")
coc_up, coc_down = top_movers(dfs["cocina"],  "COCINA")

biz_json["segments_up"]   = seg_up
biz_json["segments_down"] = seg_down
biz_json["cocinasup"]    = coc_up
biz_json["cocinasdown"]  = coc_down
# Agregar ingresos por income
biz_json["incomeup"]   = income_up
biz_json["incomedown"] = income_down
biz_json["incomesummary"] = income_summary

#guardar biz_json en un archivo
(OUT_DIR / "business_data.json").write_text(
    json.dumps(biz_json, ensure_ascii=False, indent=2), encoding="utf-8"
)


# 7) Prompt + llamada --------------------------------------------------------
prompt = make_llm_prompt(biz_json)
#guardar el prompt en un archivo
(OUT_DIR / "prompt_llm.md").write_text(prompt, encoding="utf-8")
respuesta_llm, costo = llm_invoke(prompt)

if respuesta_llm:
    (OUT_DIR / "report_llm.md").write_text(respuesta_llm, encoding="utf-8")
    print(f"✅ Reporte generado – costo estimado USD {costo:.4f}")
else:
    print("❌ No se pudo generar el análisis")

# 8) Guardar CSVs finales (opcional) -----------------------------------------
for key, df in dfs.items():
    df.to_csv(OUT_DIR / f"datos_{key}.csv", index=False)

ctx = {
    "afv_ref": dfs["overall"].iat[0, dfs["overall"].columns.get_loc("afv_ref")],
    "bs"     : dfs["overall"].iat[0, dfs["overall"].columns.get_loc("efecto_bs")],
    "aiv"    : dfs["overall"].iat[0, dfs["overall"].columns.get_loc("efecto_aiv")],
    "mix"    : dfs["overall"].iat[0, dfs["overall"].columns.get_loc("efecto_mix")],
    "verticals": dfs["vertical"],        # df completo
    "cocinas_movers": pd.DataFrame(coc_up + coc_down),
    "income_df": df_income,
    "afv_timeline": df_timeline
}

# ───── Interfaz Streamlit para mostrar el reporte ─────────────────────────────
import re, streamlit as st
from viz_runtime import CHART_BUILDERS ,build_waterfall_vertical



for vert in ctx["verticals"]["nivel2"].unique():
    CHART_BUILDERS[f"WF_{vert}"] = (
        lambda v=vert: (lambda c: build_waterfall_vertical(c, v, pct_base=True))
    )()

st.set_page_config(page_title="AFV Dashboard", layout="centered")
st.markdown("## Análisis de AFV")

#pattern = r"<!--CHART:([A-Z_]+)-->"
pattern = r"<!--CHART:([^>]+)-->"      # todo lo que haya hasta -->

chunks  = re.split(pattern, respuesta_llm)

for i, chunk in enumerate(chunks):
    if i % 2 == 0:                         # texto markdown
        if chunk.strip():
            st.markdown(chunk, unsafe_allow_html=True)
    else:                                  # nombre del gráfico
        key = chunk.strip()
        builder = CHART_BUILDERS.get(key)
        if builder:
            fig = builder(ctx)
            st.plotly_chart(fig, use_container_width=True)
            if key == "SCATTER_COCINAS":
                with st.expander("Ver explicación del gráfico", expanded=False):
                    st.info("""
                    • Eje X: ΔShare (p.p.) — derecha sube, izquierda baja.  
                    • Eje Y: AFV actual ($).  
                    • Burbuja: impacto absoluto en ΔAFV país (más grande = más importante).  
                    • Color: verde gana share / rojo pierde share.
                    """)
        else:
            st.warning(f"[Grafico {key} no registrado]")


with st.expander("Ver datos base"):
    # Mostrar los datos base
    st.markdown("### Datos Base")
    st.dataframe(df_base)

    # Mostrar los datos por nivel
    for key, df in dfs.items():
        st.markdown(f"### Datos {key.capitalize()}")
        st.dataframe(df)

    # Mostrar el JSON de negocio
    st.markdown("### JSON de Negocio")
    st.json(biz_json, expanded=True)

    # Mostrar los segmentos y cocinas con mayor cambio de share
    st.markdown("### Segmentos con Mayor Cambio de Share")
    st.markdown("#### Segmentos que Suben")
    st.dataframe(pd.DataFrame(seg_up))
    st.markdown("#### Segmentos que Bajan")
    st.dataframe(pd.DataFrame(seg_down))
    st.markdown("#### Cocinas que Suben")
    st.dataframe(pd.DataFrame(coc_up))
    st.markdown("#### Cocinas que Bajan")
    st.dataframe(pd.DataFrame(coc_down))


# ───── Fin del script ───────────────────────────────────────────────────



